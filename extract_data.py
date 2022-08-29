import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom

# Initializing IFC model
DUPLEX = r'C:\Users\kfjor\Google Drev\DTU\7. semester\11034 Advanced BIM\Duplex_A_20110907.ifc'
ifc = ifcopenshell.open(DUPLEX)

def get_amount_ifc_spaces(ifc_model):
    # Querying all spaces and returning length of list
    ifc_spaces = ifc_model.by_type('IfcSpace')
    return len(ifc_spaces)


def get_amount_of_stories(ifc_model):
    # Querying all building storeys and returning length of list
    ifc_levels = ifc_model.by_type('IfcBuildingStorey')
    return len(ifc_levels)


def get_all_unique_materials(ifc_model):
    # Querying all elements in IFC model
    ifc_elements = ifc_model.by_type('IfcProduct')

    all_materials = []
    for ifc_element in ifc_elements:
        # Using try statement because not all elements contain materials pset
        try:
            # Reading all materials from element
            elem_mats = list(ifcopenshell.util.element.get_psets(ifc_element)["PSet_Revit_Type_Materials and Finishes"].values())
            
            # Filtering out illegible materials and adding unique entries to output list
            elem_mats_filtered = [elem_mat for elem_mat in elem_mats if isinstance(elem_mat, str)]
            [all_materials.append(elem_mat_filtered) for elem_mat_filtered in elem_mats_filtered if elem_mat_filtered not in all_materials]
        except: 
            pass

    return all_materials


def get_total_floor_area(ifc_model):
    # Querying all floor elements in IFC model
    ifc_floors = ifc_model.by_type('IfcSlab')

    total_floor_area = 0
    for ifc_floor in ifc_floors:
        # Using try statement because not all elements contain dimensions pset
        try:
            # Reading floor area from element and adding it to total floor area
            floor_area = ifcopenshell.util.element.get_psets(ifc_floor)["PSet_Revit_Dimensions"]["Area"]
            total_floor_area += floor_area
        except:
            pass

    return total_floor_area


# Printing out needed variables
print(f"Total amount of spaces: {get_amount_ifc_spaces(ifc)}")
print(f"Total amount of stories: {get_amount_of_stories(ifc)}")
print(f"Unique materials: {get_all_unique_materials(ifc)}")
print(f"Total floor areal: {round(get_total_floor_area(ifc), 2)} m2")