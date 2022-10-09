import json
import ifcopenshell
from assignment1 import *

def main_html(model, volume_unit, materials):
    # Generate the initial HTML, which also references the JS and CSS files
    html_string = ""
    html_string += "<html>\n"
    html_string += "<head>\n"
    html_string += "<link rel='stylesheet' href='main.css'></link>\n"
    html_string += "<script src='main.js'></script>\n"
    html_string += "<script src='ifc_export.js'></script>\n"
    html_string += "<script src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.js'></script>\n"
    html_string += "</head>\n"
    html_string += "<body onload=\"main()\">\n"  

    # Generate the BIM specific parts of the HTML
    html_string += custom_html(model, volume_unit, materials)
    
    html_string += "\t</body>\n"   
    html_string += "</html>\n"

    return html_string

# Some of the code in this method is based on Tim's sample from repo
def custom_html(model, volume_unit, materials):  

    # Getting the project name of the IFC model  
    project_name = model.by_type('IfcProject')[0].LongName

    # Getting the address of the IFC model
    address = model.by_type("IfcAddress")[0]
    formatted_address = f"{address.Town}, {address.Country}"
    
    # Getting the elevation of the IFC model
    site = model.by_type('IfcSite')[0]
    site_elev = round(site.RefElevation)
    
    # Implementing these properties in the HTML
    html_string = ""
    html_string += "<model->\n"
    html_string += f"<project- name=\"{project_name}\">\n"
    html_string += f"<site- lat=\"{site.RefLatitude}\" long=\"{site.RefLongitude}\" elev=\"{site_elev}\" address=\"{formatted_address}\">\n"
    html_string += "<building->\n"
    
    floors = model.by_type('IfcBuildingStorey')
    floors.sort(key=lambda x: x.Elevation, reverse=True)  
    
    # This method is 100% created by Tim
    html_string += classify_floors(floors,site_elev)

    html_string += "</building->\n"
    html_string += "</site->\n"

    # Adding the material input list
    html_string += material_table_html(materials, volume_unit)
    html_string += "</project->\n"
    html_string += "</model->\n"
    html_string += "<view->\n"
    html_string += "<plan-></plan->\n"
    html_string += "<props1-></props1->\n"
    html_string += "<props2->\n"

    # Call JS function from this buttoon
    html_string += "<button type=\"button\" onclick=\"calculateCostAndLoads()\">Calculate building</button>\n"

    # This div will contain the output cost
    html_string += "<props2result-  id=\"building_cost\"->\n"
    html_string += "</props2result->\n"
    html_string += "</props2->\n"
    html_string += "<p id = \"info\"></p>\n"
    html_string += "</view->\n"

    return html_string

# All of the code in this method is based on Tim's sample from repo
def classify_floors(floors,site_elev):
    lower_floors = sum(f.Elevation < 0.1 for f in floors)
    level = len(floors) - lower_floors
    
    html_string = ""
    for floor in floors:
        if site_elev - 0.1 <= floor.Elevation <= site_elev + 0.1:
            type = "floor_ground"
        elif site_elev < floor.Elevation:
            type = "floor_upper"
        else:
            type = "floor_lower"

        html_string += f"<floor- class=\"{type}\" name='{floor.Name}'  level='{level}' elev=\"{floor.Elevation}\" >{floor.Name} <span class=\"floor_stats\">{round(float(floor.Elevation),3)}</span> </floor->\n"    
        level -= 1

        if type == "floor_ground":
            html_string += "<ground-></ground->\n"
            
    return html_string

def material_table_html(unique_materials, volume_unit):
    # Giving each individual tag its own line in the HTML for improved readability
    html_string = ""
    html_string += "<table id=\"user_input\">\n"
    html_string += "<tr>\n"
    html_string += "<td>\n"
    html_string += "<label for=\"column1\">\n"
    html_string += "\n"
    html_string += "</label>\n"
    html_string += "</td>\n"
    html_string += "<td>\n"
    html_string += "<label for=\"column2\">\n"
    html_string += f"Densities [kr./{volume_unit}]\n"
    html_string += "</label>\n"
    html_string += "</td>\n"
    html_string += "<td>\n"
    html_string += "<label for=\"column3\">\n"
    html_string += f"Cost [kr./{volume_unit}]\n"
    html_string += "</label>\n"
    html_string += "</td>\n"
    html_string += "</tr>\n"
    
    # Generate a new row for each unique material
    for material in unique_materials:
        html_string +=  "<tr>\n"
        html_string +=  "<td>\n"
        html_string +=  f"<label for=\"text\">{material}</label>\n"
        html_string +=  "</td>\n"

        # Each material in the table is assigned its own unique ID in order to parse the table later
        html_string += f"<td><input type=\"text\" id=\"{material}_density\"/></td>\n"
        html_string += f"<td><input type=\"text\" id=\"{material}_cost\"/></td>\n"
        html_string +=  "</tr>\n"

    html_string += "</table>\n"
    
    return html_string

def format_unit(ifc_unit):
    # A simple map to convert the raw IFC units to more common notation
    formatted_units_by_ifc_units = {
        "CUBIC_METRE": "m3",
        "SQUARE_METRE": "m2",
        "METRE": "m",
        "SECOND": "s",
        "INCH": "inch",
        "CUBIC_FEET": "ft2",
        "SQUARE_FEET": "ft3"
    }
    
    return formatted_units_by_ifc_units[ifc_unit]

def main():
    # Load IFC model to memory
    file_path = input("Enter file path of IFC model here: ")
    ifc = ifcopenshell.open(file_path)

    # Fetch all structural elements in model
    elements = []
    for ifc_type in ["IfcWall", "IfcBeam", "IfcRoof", "IfcSlab"]:
        elements = elements + ifc.by_type(ifc_type)

    # Utilize method from Assignment 1 to generate database of the model
    db, error_log, unique_materials = generate_element_db(elements)

    # Get the volume unit of the IFC model
    volume_unit = [unit.Name for unit in ifc.by_type("IfcProject")[0].UnitsInContext.Units if unit.UnitType == "VOLUMEUNIT"][0]
    formatted_volume_unit = format_unit(volume_unit)

    # Generate the HTML string 
    html_string = main_html(ifc, formatted_volume_unit, unique_materials)

    # Save HTML to file
    with open("index.html", "w") as f:
        f.write(html_string)    

    # This is a bit of a sketchy workaround. Loading an actual JSON file from the browser proved
    # to be difficult due to security protocols. To fix this, an independent JS script is generated
    # with the entire building database "hardcoded" into it. Since the rest of the HTML is generated
    # from this Python script anyways, it is deemed an acceptable solution
    with open("ifc_export.js", "w") as f:
        f.write("var data = ")
        f.write(json.dumps(db))

if __name__ == "__main__":
    main()