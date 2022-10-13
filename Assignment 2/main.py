import json
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
from shapely.geometry import Polygon
from shapely.ops import unary_union
from assignment1 import *

# TO-DO:
# Reorganize the html generation so it is more structured
# Comment the SVG parts of the code
# Clean up CSS

# Various lookup tables
STOREY_BY_TYPE = {
    "IfcWall": ["PSet_Revit_Constraints", "Base Constraint"],
    "IfcDoor": ["PSet_Revit_Constraints", "Level"],
    "IfcWindow": ["PSet_Revit_Constraints", "Level"]
}

COLORS_BY_IFC = {
    "IfcWall": "black",
    "IfcDoor": "darkgrey",
    "IfcWindow": "darkgrey"
}

UNITS_BY_IFC_UNITS = {
    "CUBIC_METRE": "m3",
    "SQUARE_METRE": "m2",
    "METRE": "m",
    "SECOND": "s",
    "INCH": "inch",
    "CUBIC_FEET": "ft2",
    "SQUARE_FEET": "ft3"
}

def get_polygons_from_model(model, ifc_type):
    # Initialize the geometry extraction
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    list_of_polygon_coords = {}

    # Get the appropriate pset path
    pset_path = STOREY_BY_TYPE[ifc_type]
    
    for element in model.by_type(ifc_type):
        # Extract the storey of the given element
        element_psets = ifcopenshell.util.element.get_psets(element)
        element_storey = element_psets[pset_path[0]][pset_path[1]]

        # Making sure that the dictionary has the appropriate key
        if element_storey not in list_of_polygon_coords.keys():
            list_of_polygon_coords[element_storey] = []

        # Read the geometry of the element
        try:
            shape = ifcopenshell.geom.create_shape(settings, element)
            faces, verts = shape.geometry.faces, shape.geometry.verts
        except:
            continue
        
        # Making the flat list be grouped in the vertex pairs
        grouped_verts = [[round(verts[i], 3), round(verts[i + 1], 3)] for i in range(0, len(verts), 3)]
        grouped_faces = [[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)]

        # Getting all the polygons associated with a given element
        element_polygons = []
        for face in grouped_faces:
            current_verts = [grouped_verts[idx] for idx in face]

            element_polygons.append(Polygon(current_verts))

        # Attempt to merge the different polygons in the element to a single
        # polygon. Occasionally this will fail due to some elements having
        # non adjacent polygons, hence the try except statement
        try:
            union_polygon = unary_union(element_polygons)
            x, y = union_polygon.exterior.xy
            list_of_polygon_coords[element_storey].append(list(zip(x,y)))
        except AttributeError:
            for element_polygon in element_polygons:
                x, y = element_polygon.exterior.xy
                list_of_polygon_coords[element_storey].append(list(zip(x,y)))

    
    return list_of_polygon_coords

def create_parent_html(width, height, size_factor, level):
    # Each parent entity is the base for the floor plan. Therefore, this is
    # simply a rectangle with a level attribute 
    html_string = ""
    html_string += f"<div class=\"parent\" level=\"{level}\">\n"
    html_string += f"<svg class=\"svg-one\" width=\"{round(width*size_factor, 2)}\" height=\"{round(height*size_factor, 2)}\">\n"
    html_string += f"<rect x=\"0\" y=\"0\" width=\"{round(width*size_factor, 2)}\" height=\"{round(height*size_factor, 2)}\" fill=\"#F4F6F6\"/>\n"
    html_string += "</svg>\n"

    return html_string

def convert_polygons_to_svg(polygon_coords, width, height, x_translation, y_translation, size_factor):
    html_string = ""

    for ifc_type, polygons in polygon_coords.items():

        for element_pts in polygons:
            # Calculating the translated coordinates of the polygon
            x_coords = [round((pt[0]+x_translation)*size_factor,2) for pt in element_pts]
            y_coords = [round((pt[1]+y_translation)*size_factor,2) for pt in element_pts]

            # Creating a HTML compliant string to hold the polygon coordinates
            element_string = ""
            for x_coord, y_coord in zip(x_coords, y_coords):
                element_string += f"{x_coord},{y_coord} "

            # Adding color to the shape
            color = COLORS_BY_IFC[ifc_type]

            # Adding the coordinates, color and other properties to the html
            # element
            html_string += f"<svg class=\"primary\" width=\"{round(width*size_factor, 2)}\" height=\"{round(height*size_factor, 2)}\" fill=\"{color}\">\n"
            html_string += f"<polygon points=\"{element_string[:-1]}\"\>\n"
            html_string += "</svg>\n"
        
    return html_string

def calculate_translation_props(polygons):
    # The floor plans works by having multiple small polygons be positioned
    # on top of the parent entity. Therefore, the polygons all have to be 
    # positioned correctly

    # Exctracting all the point associated with a list of polygons
    all_points = []
    for ifc_type in polygons.values():
        for polygon in ifc_type.values():
            all_points += [item for sublist in polygon for item in sublist]

    # These values determine the bounding box of the floor plan
    min_x, min_y = min([pt[0] for pt in all_points]), min([pt[1] for pt in all_points]) 
    max_x, max_y = max([pt[0] for pt in all_points]), max([pt[1] for pt in all_points]) 

    # The coordinate system has to start at (0,0) since an svg element can't
    # have negative values in their properties (e.g. a rectangle with a negative
    # height)
    x_translation, y_translation = 0 - min_x, 0 - min_y
    width, height = max_x - min_x, max_y - min_y

    return x_translation, y_translation, width, height

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

    # Add the SVG floor plans beneath the other properties
    html_string += "<floor_plan->\n"
    html_string += create_svg_floor_plans(model)
    html_string += "</floor_plan->\n"
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

def create_svg_floor_plans(ifc_model):
    # Read all polygons of the walls, windows and doors of the ifc model
    polygons_by_types = {}
    polygons_by_types["IfcWall"] = get_polygons_from_model(ifc_model, "IfcWall")
    polygons_by_types["IfcWindow"] = get_polygons_from_model(ifc_model, "IfcWindow")
    polygons_by_types["IfcDoor"] = get_polygons_from_model(ifc_model, "IfcDoor")

    # Translate the polygons to comply to the SVG parent entity
    x_translation, y_translation, width, height = calculate_translation_props(polygons_by_types)
    
    # When the polygons are read, they will be in the given IFC unit. This variable
    # is a size factor, i.e. 1 meter = 30 pixels
    SIZE_FACTOR = 30

    # "Transpose" the polygon dictionary to the primary key is the levels and not 
    # the types
    polygons_by_levels = {}
    for ifc_type, levels in polygons_by_types.items():
        for level, polygons in levels.items():
            if level not in polygons_by_levels.keys():
                polygons_by_levels[level] = {}

            polygons_by_levels[level][ifc_type] = polygons

    # For each level, generate a SVG floor plan
    html_string = ""
    for level in list(polygons_by_types.values())[0].keys():
        html_string += create_parent_html(width, height, SIZE_FACTOR, level)
        html_string += convert_polygons_to_svg(polygons_by_levels[level], width,height, x_translation, y_translation, SIZE_FACTOR)
        html_string += "</div>"
    
    return html_string

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
    formatted_volume_unit = UNITS_BY_IFC_UNITS[volume_unit]

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