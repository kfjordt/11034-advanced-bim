import ifcopenshell.geom
from shapely.geometry import Polygon


class IfcFloor:
    def __init__(
        self, 
        name: str,
        height: float,
        floor_type: str

    ) -> None:
        self.name = name
        self.height = height
        self.floor_type = floor_type


class IfcElement:
    def __init__(
        self, 
        id: str,
        polygons: list[Polygon], 
        volume: float, 
        floor_str: str, 
        type: str, 
        materials: list[tuple], 
        structural: bool
    ) -> None:

        self.id = id
        self.storey = floor_str
        self.polygons = polygons
        self.type = type
        self.volume = volume
        self.materials = materials
        self.structural = structural


class IfcBuilding:
    def __init__(
        self, 
        project_name: str,
        address: str,
        elevation: str,
        latitude: str,
        longitude: str,
        unique_materials: list[str],
        ifc_floors: list[IfcFloor],
        ifc_elements: list[IfcElement]
    ) -> None:
        
        self.project_name = project_name
        self.address = address
        self.elevation = elevation
        self.latitude = latitude
        self.longitude = longitude
        self.unique_materials = unique_materials
        self.ifc_floors = ifc_floors
        self.ifc_elements = ifc_elements


class SvgPolygon:
    def __init__(self, html_string: str, id: str) -> None:
        self.html_string = html_string
        self.id = id

STOREY_BY_TYPE = {
    "IfcWall": ["PSet_Revit_Constraints", "Base Constraint"],
    "IfcWallStandardCase": ["PSet_Revit_Constraints", "Base Constraint"],
    "IfcDoor": ["PSet_Revit_Constraints", "Level"],
    "IfcWindow": ["PSet_Revit_Constraints", "Level"],
    "IfcSlab": ["PSet_Revit_Constraints", "Level"],
    "IfcBeam": ["PSet_Revit_Constraints", "Reference Level"],
    "IfcRoof": ["PSet_Revit_Constraints", "Base Level"]
}

COLORS_BY_IFC = {
    "IfcSlab": "white",
    "IfcWall": "black",
    "IfcWallStandardCase": "black",
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

GEOMETRY_SETTINGS = ifcopenshell.geom.settings()
GEOMETRY_SETTINGS.set(GEOMETRY_SETTINGS.USE_WORLD_COORDS, True)

STRUCTURAL_ELEMENT_TYPES = ["IfcWall", "IfcBeam", "IfcRoof", "IfcSlab"]
NON_STRUCTURAL_ELEMENT_TYPES = ["IfcDoor", "IfcWindow"]

SIZE_FACTOR = 30

