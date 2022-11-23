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


def extract_svg_polygons_from_ifc_building(ifc_building: IfcBuilding):
    ifc_elements = ifc_building.ifc_elements

    ifc_polygons = [ifc_element.polygons for ifc_element in ifc_elements]

    x_translation, y_translation, width, height = calculate_translation_props(ifc_polygons)

    svg_polygons = []
        
    for ifc_element in ifc_elements:
        ifc_polygons = ifc_element.polygons
        ifc_id = ifc_element.id

        for ifc_polygon in ifc_polygons:
            x_coords = [round((pt[0]+x_translation)*SIZE_FACTOR,2) for pt in ifc_polygon]
            y_coords = [round((pt[1]+y_translation)*SIZE_FACTOR,2) for pt in ifc_polygon]

            # Creating a HTML compliant string to hold the polygon coordinates
            element_string = ""
            for x_coord, y_coord in zip(x_coords, y_coords):
                element_string += f"{x_coord},{y_coord} "

            # Adding color to the shape
            color = COLORS_BY_IFC[ifc_element.type]

            html_string = f"<svg class=\"primary\" width=\"{round(width*SIZE_FACTOR, 2)}\" height=\"{round(height*SIZE_FACTOR, 2)}\" fill=\"{color}\">\n"
            html_string += f"<polygon points=\"{element_string[:-1]}\"\>\n"
            html_string += "</svg>\n"

            svg_polygons.append(SvgPolygon(html_string, ifc_id))

    return svg_polygons


def serialize_svg_polygons_to_json(svg_polygons: list[SvgPolygon]):
    return {svg_polygon.id: svg_polygon.html_string for svg_polygon in svg_polygons}