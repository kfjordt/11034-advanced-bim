import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
from python_modules.classes_and_constants import *
from python_modules.svg_utils import format_string
from shapely.geometry import Polygon
from shapely.ops import unary_union
import os


def load_model() -> ifcopenshell.file:
    '''
    Loads an IFC model to memory.
    '''

    all_models_present = [
        file for file in os.listdir(MODEL_LOOKUP_DIRECTORY)
        if file.split(".")[-1] == "ifc"
    ]

    all_models_present.sort()

    return ifcopenshell.open(f"{MODEL_LOOKUP_DIRECTORY}/{all_models_present[0]}")


def load_elements(ifc_model: ifcopenshell.file, ifc_types: list[str]) -> list[ifcopenshell.entity_instance]:
    '''
    Loads all elements of specified types from IFC model.
    '''
    elements = []
    for ifc_type in ifc_types:
        elements = elements + ifc_model.by_type(ifc_type)
    
    return elements


def get_element_materials(ifc_element: ifcopenshell.entity_instance) -> list[tuple]:
    '''
    Retrieves a list of tuples containing the materials and how many percent the given material takes up of the element.
    '''
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


def get_element_properties(ifc_element: ifcopenshell.entity_instance) -> tuple:
    '''
    Gets the element psets according to the element type.
    
    Indices:
    0 = volume, 1 = storey, 2 = ifc type, 3 = structural, 4 = id
    '''

    # Each different IFC type has different psets, meaning that each unique element type
    # has to be accessed differently
    element_psets = ifcopenshell.util.element.get_psets(ifc_element)

    element_volume = element_psets.get("PSet_Revit_Dimensions", {}).get("Volume")
    
    element_type = ifc_element.is_a()

    structural = element_type in STRUCTURAL_ELEMENT_TYPES
    lookup_path = STOREY_BY_TYPE[ifc_element.is_a()]

    element_storey = element_psets.get(lookup_path[0], {}).get(lookup_path[1])
    element_id = ifc_element[0]

    return (element_volume, element_storey, element_type, structural, element_id)


def get_elements_polygons(ifc_element: ifcopenshell.entity_instance) -> list[tuple]:
    '''
    Parses element geometry and returns a list of coordinates.
    '''
    try: 
        shape = ifcopenshell.geom.create_shape(GEOMETRY_SETTINGS, ifc_element)
    except RuntimeError:
        return None 

    faces, verts = shape.geometry.faces, shape.geometry.verts

    # Making the flat list be grouped in the vertex pairs
    grouped_verts = [[round(verts[i], 3), round(verts[i + 1], 3)] for i in range(0, len(verts), 3)]
    grouped_faces = [[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)]

    # Getting all the polygons associated with a given element
    polygons = []

    for face in grouped_faces:
        current_verts = [grouped_verts[idx] for idx in face]

        polygons.append(Polygon(current_verts))

    # Attempt to merge the different polygons in the element to a single
    # polygon. Occasionally this will fail due to some elements having
    # non adjacent polygons, hence the try except statement
    polygon_coords = []
    try:
        union_polygon = unary_union(polygons)
        x, y = union_polygon.exterior.xy
        polygon_coords.append(list(zip(x,y)))
                
    except AttributeError:
        for polygon in polygons:
            x, y = polygon.exterior.xy
            polygon_coords.append(list(zip(x,y)))

    return polygon_coords


def get_building_storeys(ifc_model: ifcopenshell.file) -> list[IfcFloor]:
    ifc_storeys = load_elements(ifc_model, ["IfcBuildingStorey"])
    ifc_storeys.sort(key=lambda x: x.Elevation, reverse=False)
    
    ifc_floors = []
    for idx, ifc_storey in enumerate(ifc_storeys):
        storey_name = ifc_storey.Name

        if idx < len(ifc_storeys) - 1:
            storey_height = abs(ifc_storeys[idx+1].Elevation  - ifc_storey.Elevation)
            storey_type = "Regular"
        else:
            storey_height = 1  # Symbolic height
            storey_type = "Roof"

        if ifc_storey.Elevation < 0:
            storey_type = "Basement"
        
        ifc_floors.append(
            IfcFloor(
                storey_name, round(storey_height, 2), storey_type
            )
        )
    
    return ifc_floors


def get_static_properties(ifc_model: ifcopenshell.file) -> tuple:
    # Getting the project name of the IFC model  
    project_name = ifc_model.by_type('IfcProject')[0].LongName

    # Getting the address of the IFC model
    address = ifc_model.by_type("IfcAddress")[0]
    formatted_address = f"{address.Town}, {address.Country}"
    
    # Getting the elevation of the IFC model
    site = ifc_model.by_type('IfcSite')[0]

    site_elev = round(site.RefElevation)
    site_lat = site.RefLatitude
    site_long = site.RefLongitude

    return (project_name, formatted_address, site_elev, site_lat, site_long)


def parse_model() -> list[IfcElement]:
    model = load_model()

    element_types = STRUCTURAL_ELEMENT_TYPES + NON_STRUCTURAL_ELEMENT_TYPES
    elements = load_elements(model, element_types)

    ifc_elements = []
    for element in elements:
        materials = get_element_materials(element)
        polygons = get_elements_polygons(element)
        properties = get_element_properties(element)

        # Guard clause
        if not polygons:
            continue

        volume = properties[0]
        storey = properties[1]
        ifc_type = properties[2]
        structural = properties[3]
        id = properties[4]

        if not materials:
            materials = [(f"{ifc_type} Generic Material", 1)]

        ifc_element = IfcElement(
            id,
            polygons, 
            volume,
            storey,
            ifc_type,
            materials,
            structural
        )

        ifc_elements.append(ifc_element)

    unique_materials = list(set([materials[0]
                   for sublist in [ifc_element.materials for ifc_element in ifc_elements] 
                   for materials in sublist]))

    project_name, formatted_address, site_elev, site_lat, site_long = get_static_properties(model)

    ifc_storeys = get_building_storeys(model)

    ifc_building = IfcBuilding(
        project_name,
        formatted_address,
        site_elev,
        site_lat,
        site_long,
        unique_materials,
        ifc_storeys,
        ifc_elements
    )
    
    return ifc_building


def serialize_ifc_building_to_json(ifc_building: IfcBuilding):
    ifc_building_json = {
            "project_name": ifc_building.project_name,
            "address": ifc_building.address,
            "elevation": ifc_building.elevation,
            "latitude": ifc_building.latitude,
            "longitude": ifc_building.longitude,
            "unique_materials": ifc_building.unique_materials,
            "ifc_floors": {},
            "ifc_elements": {},
        }

    for ifc_floor in ifc_building.ifc_floors:
        ifc_building_json["ifc_floors"][format_string(ifc_floor.name)] = {
            "name": ifc_floor.name,
            "height": ifc_floor.height,
            "floor_type": ifc_floor.floor_type
        }

    for ifc_element in ifc_building.ifc_elements:

        ifc_building_json["ifc_elements"][ifc_element.id] = {
            "storey": ifc_element.storey,
            "type": ifc_element.type,
            "volume": ifc_element.volume,
            "materials": ifc_element.materials,
            "structural": ifc_element.structural
        }

    return ifc_building_json
