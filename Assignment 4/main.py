from python_modules.classes_and_constants import *
from python_modules.ifc_utils import *
from python_modules.svg_utils import *
import json

def main():
    file_path = "models\Duplex_A_20110907.ifc"

    ifc_building = parse_model(file_path)
    svg_polygons = extract_svg_polygons_from_ifc_building(ifc_building)

    ifc_building_json = serialize_ifc_building_to_json(ifc_building)
    svg_polygons_json = serialize_svg_polygons_to_json(svg_polygons)
    
    output_json = {
        "building": ifc_building_json,
        "polygons": svg_polygons_json
    }

    with open("scripts/data.json", "w") as f:
        f.write(json.dumps(output_json))

if __name__ == "__main__":
    main()