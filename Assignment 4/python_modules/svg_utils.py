from python_modules.classes_and_constants import *

def calculate_translation_props(polygons):
    '''
    Technically this function is unnecessary since the new SVG elements use viewboxes (i.e. aligning the sub-elements via percents and not absolute coordinates.)
    '''
    # The floor plans works by having multiple small polygons be positioned
    # on top of the parent entity. Therefore, the polygons all have to be 
    # positioned correctly

    # Exctracting all the point associated with a list of polygons
    all_points = []
    for polygon in polygons:
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

def save_polygons_from_building_to_files(ifc_building: IfcBuilding):
    '''
    Extracts all polygon from an instance of IfcBuilding and save them to the /output folder as .html files.
    '''

    # Grab all applicable element
    ifc_elements = [
        element for element in ifc_building.ifc_elements
        if element.type not in ELEMENT_TYPES_NOT_TO_BE_DRAWN
    ]

    # Calculate the translation properties based on all the polygons present
    ifc_polygons = [ifc_element.polygons for ifc_element in ifc_elements]
    x_translation, y_translation, width, height = calculate_translation_props(ifc_polygons)

    svg_polygons_by_floor = {}
    # Begin iteration over all elements in the building
    for ifc_element in ifc_elements:
        ifc_polygons = ifc_element.polygons
        ifc_floor = ifc_element.storey

        # Initialize the floor plan if they have not been already
        if ifc_floor not in svg_polygons_by_floor.keys():
            svg_polygons_by_floor[ifc_floor] = f"<svg class=\"{ifc_floor}\" viewBox=\"0 0 {round(width*SIZE_FACTOR, 2)} {round(height*SIZE_FACTOR, 2)}\" >\n"
        
        # Calculate the coordinates for each polygon associated with the element
        for ifc_polygon in ifc_polygons:
            x_coords = [round((pt[0]+x_translation)*SIZE_FACTOR,2) for pt in ifc_polygon]
            y_coords = [round((pt[1]+y_translation)*SIZE_FACTOR,2) for pt in ifc_polygon]

            # Creating a HTML compliant string to hold the polygon coordinates
            element_string = ""
            for x_coord, y_coord in zip(x_coords, y_coords):
                element_string += f"{x_coord},{y_coord} "
            
            # Adding color to the shape
            color = COLORS_BY_IFC[ifc_element.type]

            svg_polygons_by_floor[ifc_floor] += f"<polygon id=\"{ifc_element.id}\" class=\"ifc_element\" points=\"{element_string[:-1]}\" fill=\"{color}\"\></polygon>\n"

    # Add the section drawing to the string
    svg_polygons_by_floor["section"] = generate_section_drawing_svg(ifc_building)

    # Export each SVG drawing to the output folder
    for floor, svg_polygons in svg_polygons_by_floor.items():
        with open(f"{OUTPUT_FOLDER}/{format_string(floor)}.html", "w") as f:
            f.write(svg_polygons)
    
def format_string(input_string: str) -> str:
    # Remove characters which would break the accessing of the static files
    return input_string.replace(" ", "").replace("/","").lower()


def generate_section_drawing_svg(ifc_building: IfcBuilding) -> str:
    '''
    Generates section drawing based on all the floors present in the IfcBuilding.
    '''
    # Setting the initial svg string with a viewbox of (100%, 100%)
    svg_string = f"<svg class=\"ifc_building\" viewBox=\"0 0 100 100\" >\n"

    # Initialize variables needed to properly draw the building
    total_height = ifc_building.get_total_height()

    TOTAL_BUILDING_HEIGHT = 95

    start_y = TOTAL_BUILDING_HEIGHT
    ground_y = 0

    # Begin loop over each floor in the building
    for ifc_floor in ifc_building.ifc_floors:

        # Calculate the percentwise height of the floor
        draw_height = TOTAL_BUILDING_HEIGHT * (ifc_floor.height / total_height)
        start_y -= draw_height

        # If regular floor type, create rectangle with floor height, width = 90% and solid stroke
        if ifc_floor.floor_type == "Regular":
            svg_string += f"<rect id=\"{format_string(ifc_floor.name)}\" class=\"ifc_floor\" x=\"5\" y=\"{start_y}\" width=\"90\" height=\"{draw_height}\" style=\"fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0)\"\></rect>\n"

        # If basement floor type, create rectangle with floor height, width = 90% and dotted stroke
        elif ifc_floor.floor_type == "Basement":
            svg_string += f"<rect id=\"{format_string(ifc_floor.name)}\" class=\"ifc_floor\" x=\"5\" y=\"{start_y}\" width=\"90\" height=\"{draw_height}\" style=\"fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0);stroke-dasharray:2 2\"\></rect>\n"
            
            # Update the ground y coordinate, which will be used for drawing the ground later
            ground_y = start_y
        
        # If roof floor type, create polygon with overhang
        elif ifc_floor.floor_type == "Roof":
            polygon_points = f"0,{round(start_y+draw_height, 2)} 100,{round(start_y+draw_height, 2)} 95,{round(start_y, 2)} 5,{round(start_y, 2)}"
            svg_string += f"<polygon id=\"{format_string(ifc_floor.name)}\" class=\"ifc_floor\" points=\"{polygon_points}\" style=\"fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0);\"\></polygon>\n"

        # Add text to represent the floor names
        svg_string += f"<text x=\"11\" y=\"{(start_y+draw_height)-3}\" font-size=\"30%\">{ifc_floor.name}</text>"

    # Add the ground rectangle, which will be 100% wide
    svg_string += f"<rect id=\"ground\" class=\"ifc_floor\" x=\"0\" y=\"{ground_y}\" width=\"100\" height=\"{3}\" style=\"fill:rgb(0,0,0)\"\></rect>\n"

    return svg_string