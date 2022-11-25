from python_modules.classes_and_constants import *
from python_modules.ifc_utils import *
from python_modules.svg_utils import *
import json

def main():
    ifc_building = parse_model()
    
    save_polygons_from_building_to_files(ifc_building)
    ifc_building_json = serialize_ifc_building_to_json(ifc_building)

    with open("output/data.json", "w") as f:
        f.write(json.dumps(ifc_building_json))

if __name__ == "__main__":
    main()