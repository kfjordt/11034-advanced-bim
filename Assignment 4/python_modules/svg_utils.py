from python_modules.classes_and_constants import *

def calculate_translation_props(polygons):
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
    ifc_elements = [
        element for element in ifc_building.ifc_elements
        if element.type not in ELEMENT_TYPES_NOT_TO_BE_DRAWN
    ]

    ifc_polygons = [ifc_element.polygons for ifc_element in ifc_elements]
    
    x_translation, y_translation, width, height = calculate_translation_props(ifc_polygons)

    svg_polygons_by_floor = {}
        
    for ifc_element in ifc_elements:
        ifc_polygons = ifc_element.polygons
        ifc_floor = ifc_element.storey

        if ifc_floor not in svg_polygons_by_floor.keys():
            svg_polygons_by_floor[ifc_floor] = f"<svg class=\"{ifc_floor}\" viewBox=\"0 0 {round(width*SIZE_FACTOR, 2)} {round(height*SIZE_FACTOR, 2)}\" >\n"
        
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



    svg_polygons_by_floor["section"] = generate_section_drawing_svg(ifc_building)


    for floor, svg_polygons in svg_polygons_by_floor.items():

        with open(f"output/{format_string(floor)}.html", "w") as f:
            f.write(svg_polygons)
    

def format_string(input_string: str) -> str:
    return input_string.replace(" ", "").replace("/","").lower()


def generate_section_drawing_svg(ifc_building: IfcBuilding) -> str:
    svg_string = f"<svg class=\"ifc_building\" viewBox=\"0 0 100 100\" >\n"

    total_height = ifc_building.get_total_height()
    start_y = 90
    ground_y = 0

    for ifc_floor in ifc_building.ifc_floors:
        draw_height = 80 * (ifc_floor.height / total_height)
        start_y -= draw_height

        if ifc_floor.floor_type == "Regular":
            svg_string += f"<rect id=\"{format_string(ifc_floor.name)}\" class=\"ifc_floor\" x=\"15\" y=\"{start_y}\" width=\"70\" height=\"{draw_height}\" style=\"fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0)\"\></rect>\n"


        elif ifc_floor.floor_type == "Basement":
            svg_string += f"<rect id=\"{format_string(ifc_floor.name)}\" class=\"ifc_floor\" x=\"15\" y=\"{start_y}\" width=\"70\" height=\"{draw_height}\" style=\"fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0);stroke-dasharray:2 2\"\></rect>\n"
            ground_y = start_y
        
        elif ifc_floor.floor_type == "Roof":
            polygon_points = f"10,{start_y+draw_height} 90,{start_y+draw_height} 85,{start_y} 15,{start_y}"
            svg_string += f"<polygon id=\"{format_string(ifc_floor.name)}\" class=\"ifc_floor\" points=\"{polygon_points}\" style=\"fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0);\"\></polygon>\n"

        svg_string += f"<text x=\"18\" y=\"{(start_y+draw_height)-3}\" font-size=\"30%\">{ifc_floor.name}</text>"

    svg_string += f"<rect id=\"ground\" class=\"ifc_floor\" x=\"5\" y=\"{ground_y}\" width=\"90\" height=\"{3}\" style=\"fill:rgb(0,0,0)\"\></rect>\n"

    return svg_string