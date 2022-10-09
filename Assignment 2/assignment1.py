import ifcopenshell
import ifcopenshell.util.element
import json


def get_element_materials(ifc_element):
    materials_list = []
    try:
        # Finding relations of element and returning the association if it is a material
        for association in ifc_element.HasAssociations:
            if association.is_a('IfcRelAssociatesMaterial'):

                # Reading elements with multiple material layers (compound families)  
                try: 
                    material_associations = association.RelatingMaterial.ForLayerSet.MaterialLayers

                    # Calculating total thickness in order to calculate the percentage of a given material in an element
                    total_thickness = sum([material.LayerThickness for material in material_associations])

                    # Creating a material / thickness percentage tuple and appending it to the material list of the given element
                    for material in material_associations:
                        material_name = material.Material.Name
                        material_thickness_pct = material.LayerThickness / total_thickness

                        materials_list.append((material_name, material_thickness_pct))
                 
                # Reading elements with no material layers
                except:
                    material_name = association.RelatingMaterial.Name

                    materials_list.append(material_name, 1)  # Material thickness percent is simply 100%
            
        return materials_list

    except:
        return None


def get_element_properties(ifc_element):
    # Each different IFC type has different psets, meaning that each unique element type
    # has to be accessed differently
    element_psets = ifcopenshell.util.element.get_psets(ifc_element)

    try:
        element_volume = element_psets["PSet_Revit_Dimensions"]["Volume"]

        if ifc_element.is_a() == "IfcSlab":
            element_name = element_psets["Pset_SlabCommon"]["Reference"]
            element_storey = element_psets["PSet_Revit_Constraints"]["Level"]
        elif "IfcWall" in ifc_element.is_a():
            element_name = element_psets["Pset_WallCommon"]["Reference"]
            element_storey = element_psets["PSet_Revit_Constraints"]["Base Constraint"]
        elif ifc_element.is_a() == "IfcRoof":
            element_name = element_psets["Pset_RoofCommon"]["Reference"]
            element_storey = element_psets["PSet_Revit_Constraints"]["Base Level"]
        elif ifc_element.is_a() == "IfcBeam":
            element_name = element_psets["Pset_BeamCommon"]["Reference"]
            element_storey = element_psets["PSet_Revit_Constraints"]["Reference Level"]
    
    # If the attempted dictionary keys are not present, return None for the error log
    except:
        return None

    return {
        "Element Name": element_name,
        "Storey": element_storey,
        "Volume": element_volume
    }


def generate_element_db(ifc_elements):
    # Allocating memory to variables later used
    error_log, unique_materials, db = [], [], {}

    # Retrieve psets for each relevant element in the IFC Model
    for element in ifc_elements:
        element_id = str(element.id())
        element_properties = get_element_properties(element)
        element_materials = get_element_materials(element)

        # Guard clause for faulty elements
        if element_materials and element_properties:
            element_volume = element_properties["Volume"]
            
            element_amounts = {}

            # To correctly calculate the value of each unique material in the element, the thicknesses
            # of each layer are used to calculate the percentwise distribution of the total volume w.r.t.
            # the different materials
            for material_thickness_tuple in element_materials:
                element_material = material_thickness_tuple[0]

                # Creating a list of unique materials for the template file
                if element_material not in unique_materials:
                    unique_materials.append(element_material)

                material_amount = element_volume * material_thickness_tuple[1]
                element_amounts[element_material] = material_amount

            element_properties["Amounts"] = element_amounts

            db[element_id] = element_properties

        else:
            error_log.append(element_id)
    
    return db, error_log, unique_materials


def export_error_log(element_ids):
    with open('Error log.txt', 'w') as file:
        file.write('Elements with IDs:\n')
        file.write(str(element_ids))
        file.write("\n failed to load.")


def export_template_file(unique_materials, unit):
    with open('Material cost and densities.txt', 'w') as file:
        file.write(f"Enter the cost and densities of the materials listed here. \n\n")
        file.write(f"[kr./{unit};kg/{unit}]\n")
        file.write('i.e. Concrete: 1000;1000\n\n')

        [file.write(f'{material}: \n') for material in unique_materials]

        return file


def parse_template_file(template_file_path):
    material_cost_density = {}

    with open(template_file_path) as file:
        contents = file.read()  

        # Parsing template file according to the relevant data values
        for line in contents.split("\n")[5:-1]:
            material = line.split(":")[0]
            cost = line.split(";")[0].split(" ")[-1]
            density = line.split(";")[-1]
            
            material_cost_density[material] = {
                "Cost": cost,
                "Density": density
            }

    return material_cost_density


def calculate_cost(ifc_export, cost_densities):
    final_cost = 0
    
    # For each element, read the volume-material pair and look up its cost in the user-inputted file
    for element in ifc_export:

        for materials in ifc_export[element]["Amounts"]:
            volume = ifc_export[element]["Amounts"][materials]
            material_cost = cost_densities[materials]["Cost"]

            final_cost = final_cost + float(volume) * float(material_cost)

    return final_cost


def calculate_loads(ifc_export, cost_densities):
    # Reading all unique levels present in the IFC model
    unique_levels = list(set([ifc_export[key]["Storey"] for key in ifc_export]))

    GRAVITY = 9.82

    #Initializing the output dict
    final_loads = {floor: 0 for floor in unique_levels}
    
    # For each element, read the volume-material pair and look up its density in the user-inputted file
    for element in ifc_export:
        element_storey = ifc_export[element]["Storey"]
        element_force = 0

        # Making sure that all material layers are calculated
        for materials in ifc_export[element]["Amounts"]:
            volume = ifc_export[element]["Amounts"][materials]
            material_density = cost_densities[materials]["Density"]

            element_force += volume * float(material_density) * GRAVITY
        
        # Update the dict with the contribution from the new material layer
        final_loads[element_storey] += element_force

    return final_loads


def main():
            
    print("----------------------------------------------")
    print("| Program started. Follow instructions below |")
    print("----------------------------------------------")


    load_building_flag = int(input("Enter \"0\" to load building, and \"1\" to calculate building: "))

    if load_building_flag == 0: # User has chosen to load a new building

        # Prompting user to enter input
        export_error_log_flag = input("Export error log? (y/n) ")
        file_path = input("Enter file path of building: ")

        # Loading IFC model to memory
        ifc = ifcopenshell.open(file_path)

        # Not all IFC Products are deemed important to the structural calculations
        STRUCTURAL_ELEMENTS = ["IfcWall", "IfcBeam", "IfcRoof", "IfcSlab"]

        # Retrieving all relevant elements
        elements = []
        for ifc_type in STRUCTURAL_ELEMENTS:
            elements = elements + ifc.by_type(ifc_type)

        # Generating element database
        db, error_log, unique_materials = generate_element_db(elements)

        if export_error_log_flag == "y":
            export_error_log(error_log)

        # Extracting the volume unit from the IFC file
        volume_unit = [unit.Name for unit in ifc.by_type("IfcProject")[0].UnitsInContext.Units if unit.UnitType == "VOLUMEUNIT"][0]
        
        # Exporting the necessary files for the user to fill out
        export_template_file(unique_materials, volume_unit)

        with open("IFC Export.json", "w") as outfile:
            outfile.write(json.dumps(db, indent=4))

        print("-----------------------------------------------------")
        print("| Building Loaded. Input material data in .txt file |")
        print("-----------------------------------------------------")
        
    elif load_building_flag == 1: # User has chosen to calculate building
        
        template_file_path = 'Material cost and densities.txt'
        material_costs_densities = parse_template_file(template_file_path)

        # Loading previously generated database JSON
        with open("IFC Export.json") as ifc_export:
            element_db = json.loads(ifc_export.read())

        # Printing out the calculated values for the cost and loads
        print(f'The total cost of the building is: {round(calculate_cost(element_db, material_costs_densities))} kr. \n')

        loads = calculate_loads(element_db, material_costs_densities)
        for storey in loads:
            print(f"Total load from {storey} is {round(loads[storey] / 1000)} kN.")


if __name__ == "__main__":
    main()
