import os
import sys
import bpy
import uuid
import math
import json
import time
import bmesh
import random
import mathutils
from math import radians, atan2, sqrt, acos, degrees


class SimpleLogger:
    # Defining log levels
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

    def __init__(self, level=INFO):
        self.level = level

    def debug(self, msg):
        self._log(self.DEBUG, "DEBUG", msg)

    def info(self, msg):
        self._log(self.INFO, "INFO", msg)

    def warning(self, msg):
        self._log(self.WARNING, "WARNING", msg)

    def error(self, msg):
        self._log(self.ERROR, "ERROR", msg)

    def critical(self, msg):
        self._log(self.CRITICAL, "CRITICAL", msg)

    def _log(self, level, level_name, msg):
        if level >= self.level:
            print(f"[{level_name}] {msg}")


logging = SimpleLogger(level=SimpleLogger.DEBUG)


def remove_old_objects():
    # Ensure we're in Object mode
    # bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    # bpy.ops.object.mode_set(mode='OBJECT')

    # # Delete all objects
    # bpy.ops.object.select_all(action='SELECT')
    # bpy.ops.object.delete()
    while bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[0])

    # Meshes
    while bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[0])

    # Delete all materials
    while bpy.data.materials:
        bpy.data.materials.remove(bpy.data.materials[0])

    # Delete all textures
    while bpy.data.textures:
        bpy.data.textures.remove(bpy.data.textures[0])

    # Armatures and Bone Groups
    while bpy.data.armatures:
        bpy.data.armatures.remove(bpy.data.armatures[0])

    # Particles
    while bpy.data.particles:
        bpy.data.particles.remove(bpy.data.particles[0])

    # Worlds
    while bpy.data.worlds:
        bpy.data.worlds.remove(bpy.data.worlds[0])

    # Grease Pencils
    while bpy.data.grease_pencils:
        bpy.data.grease_pencils.remove(bpy.data.grease_pencils[0])

    # Cameras
    while bpy.data.cameras:
        bpy.data.cameras.remove(bpy.data.cameras[0])

    # Lamps/Lights
    while bpy.data.lights:
        bpy.data.lights.remove(bpy.data.lights[0])

    # Images
    image_names = [img.name for img in bpy.data.images]

    for image_name in image_names:
        k = 0
        while image_name in bpy.data.images and k < 10:
            image = bpy.data.images[image_name]
            image.user_clear()
            if image.users == 0:
                bpy.data.images.remove(image)
            k += 1

    logging.debug('ran "remove_old_objects"')


def get_assets_info():
    assets = {}

    blend_files = [
        ("1000_beds_bundle", "beds"),
        ("1000_cabinets_bundle", "cabinets"),
        ("1000_chairs_bundle", "chairs"),
        ("1000_decor_bundle", "decor"),
        ("1000_electronics_bundle", "electronics"),
        ("1000_lamps_bundle", "lamps"),
        ("1000_plants_bundle", "plants"),
        ("1000_shelves_bundle", "shelves"),
        ("1000_sofas_bundle", "sofas"),
        ("1000_tables_bundle", "tables"),
        ("1000_tablesets_bundle", "tablesets"),
    ]

    for blend_file, category in blend_files:
        with bpy.data.libraries.load(f"//assets/interior_models/{blend_file}.blend", link=False) as (data_from, _):
            for value in data_from.objects:
                assets[value] = {}
                assets[value]["name"] = value
                assets[value]["category"] = category
                assets[value]["file"] = f"{blend_file}.blend"

    logging.debug('ran "get_assets_info"')

    return assets


def get_random_asset(assets, nonrandom_asset="plant_49", randomness=True):
    if randomness:
        index = random.randint(0, len(assets) - 1)
        asset = assets[list(assets.keys())[index]]
    else:
        if nonrandom_asset in assets:
            asset = assets[nonrandom_asset]
        else:
            asset = assets[list(assets.keys())[0]]

    logging.debug('ran "get_random_asset"')

    return asset


def add_asset(
        filepath="//assets/interior_models/1000_plants_bundle.blend", object_name='plant_24', rotation_degrees=0.0,
        randomness=False):

    rotation_degrees = random.random() * 360 if randomness else rotation_degrees

    collection_name = "Collection"

    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
    else:
        logging.CRITICAL('Collection not found!')

    if object_name in bpy.data.objects:
        print(f"Object '{object_name}' already exists in the current file.")

    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        if object_name in data_from.objects:
            data_to.objects = [object_name]
        else:
            print(f"Object '{object_name}' not found in {filepath}")

    if object_name not in bpy.data.objects:
        print(f"Failed to append material '{object_name}' from {filepath}")

    obj = bpy.data.objects[object_name]

    if obj.name not in collection.objects:
        collection.objects.link(obj)

    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, radians(rotation_degrees))

    logging.debug('ran "add_asset"')


def append_material_from_library(blend_path, material_name):
    logging.debug('started "append_material_from_library" function.')
    # Define the path to the material inside the .blend file
    # material_path = f"./assets/materials/{blend_path}/{blend_path}/Material/"
    # material_path_dir = f"./assets/materials/{blend_path}/{blend_path}/Material/"

    logging.debug(f'blend_path: "{blend_path}"')
    logging.debug(f'material_name: "{material_name}"')

    base_assets_path = "//assets/materials/"
    absolute_blend_path = os.path.join(base_assets_path, blend_path, blend_path)

    if material_name in bpy.data.materials:
        print(f"Material '{material_name}' already exists in the current file.")

    # material_directory = os.path.join(base_assets_path, blend_path, blend_path, "Material")

    # Append the material
    with bpy.data.libraries.load(absolute_blend_path) as (data_from, data_to):
        if material_name in data_from.materials:
            data_to.materials = [material_name]
        else:
            print(f"Material '{material_name}' not found in {absolute_blend_path}")

    if material_name not in bpy.data.materials:
        print(f"Failed to append material '{material_name}' from {absolute_blend_path}")

    # bpy.ops.wm.append(filename=material_name, directory=material_path)

    logging.debug('ran "append_material_from_library"')


def append_node_group_from_library(blend_path, node_group_name):
    base_assets_path = "//assets/materials/"
    absolute_blend_path = os.path.join(base_assets_path, blend_path, blend_path)

    if node_group_name in bpy.data.node_groups:
        print(f"Node group '{node_group_name}' already exists in the current file.")

    with bpy.data.libraries.load(absolute_blend_path) as (data_from, data_to):
        if node_group_name in data_from.node_groups:
            data_to.node_groups = [node_group_name]
        else:
            print(f"Node group '{node_group_name}' not found in {absolute_blend_path}")

    if node_group_name not in bpy.data.node_groups:
        print(f"Failed to append node group '{node_group_name}' from {absolute_blend_path}")

    logging.debug('ran "append_node_group_from_library"')


def add_and_rename_material(materials, material_name='piano_key'):
    logging.debug('started "add_and_rename_material" function.')
    material = materials[material_name]
    new_material_name = f'{material["name"]}_{uuid.uuid4().int}'
    append_material_from_library(material['file'], material['name'])
    bpy.data.materials[material['name']].name = new_material_name

    logging.debug(f'ran "add_and_rename_material" and added material {new_material_name}')

    return new_material_name


def get_materials_info():
    materials = {
        'brick_wall_02': {
            'name': 'brick_wall_02',
            'file': 'brick_wall_02_4k.blend',
            'types': ['wall']
        },
        'brick_wall_006': {
            'name': 'brick_wall_006',
            'file': 'brick_wall_006_4k.blend',
            'types': ['wall']
        },
        'ceiling_interior': {
            'name': 'ceiling_interior',
            'file': 'ceiling_interior_4k.blend',
            'types': ['ceiling']
        },
        'concrete_floor_03': {
            'name': 'concrete_floor_03',
            'file': 'concrete_floor_03_4k.blend',
            'types': ['floor']
        },
        'concrete_layers_02': {
            'name': 'concrete_layers_02',
            'file': 'concrete_layers_02_4k.blend',
            'types': ['floor', 'wall', 'ceiling']
        },
        'concrete_wall_005': {
            'name': 'concrete_wall_005',
            'file': 'concrete_wall_005_4k.blend',
            'types': ['wall']
        },
        'concrete_wall_008': {
            'name': 'concrete_wall_008',
            'file': 'concrete_wall_008_4k.blend',
            'types': ['wall']
        },
        'cw-glass-universe': {
            'name': 'cw-glass-universe',
            'file': 'cw-glass-universe.blend',
            'types': []
        },
        'distance': {
            'name': 'distance',
            'file': 'distance.blend',
            'types': []
        },
        'garage_floor': {
            'name': 'garage_floor',
            'file': 'garage_floor_4k.blend',
            'types': ['floor']
        },
        'grey_stone_path': {
            'name': 'grey_stone_path',
            'file': 'grey_stone_path_4k.blend',
            'types': ['floor']
        },
        'herringbone_parquet': {
            'name': 'herringbone_parquet',
            'file': 'herringbone_parquet_4k.blend',
            'types': ['floor']
        },
        'laminate_floor_02': {
            'name': 'laminate_floor_02',
            'file': 'laminate_floor_02_4k.blend',
            'types': ['floor', 'ceiling']
        },
        'mossy_cobblestone': {
            'name': 'mossy_cobblestone',
            'file': 'mossy_cobblestone_4k.blend',
            'types': ['floor']
        },
        'normal.blend': {
            'name': 'normal',
            'file': 'normal.blend',
            'types': []
        },
        'patterned_brick_floor': {
            'name': 'patterned_brick_floor',
            'file': 'patterned_brick_floor_4k.blend',
            'types': ['floor']
        },
        'piano_key': {
            'name': 'piano_key',
            'file': 'piano_key.blend',
            'types': []
        },
        'pitch_black': {
            'name': 'pitch_black',
            'file': 'pitch_black.blend',
            'types': []
        },
        'plastered_stone_wall': {
            'name': 'plastered_stone_wall',
            'file': 'plastered_stone_wall_4k.blend',
            'types': ['wall']
        },
        'preconcrete_wall_001': {
            'name': 'preconcrete_wall_001',
            'file': 'preconcrete_wall_001_4k.blend',
            'types': ['wall']
        },
        'raw_plank_wall': {
            'name': 'raw_plank_wall',
            'file': 'raw_plank_wall_4k.blend',
            'types': ['wall']
        },
        'rustic_stone_wall_02': {
            'name': 'rustic_stone_wall_02',
            'file': 'rustic_stone_wall_02_4k.blend',
            'types': ['wall']
        },
        'rusty_metal_sheet': {
            'name': 'rusty_metal_sheet',
            'file': 'rusty_metal_sheet_4k.blend',
            'types': ['floor', 'wall', 'ceiling']
        },
        'short_bricks_floor': {
            'name': 'short_bricks_floor',
            'file': 'short_bricks_floor_4k.blend',
            'types': ['floor']
        },
        'sy_alum_matte': {
            'name': 'sy_alum_matte',
            'file': 'sy_alum_matte.blend',
            'types': []
        },
        'sy_alum_shiny': {
            'name': 'sy_alum_shiny',
            'file': 'sy_alum_shiny.blend',
            'types': []
        },
        'sy_glass_EK': {
            'name': 'sy_glass_EK',
            'file': 'sy_glass_EK.blend',
            'types': []
        },
        'sy_glass_JL': {
            'name': 'sy_glass_JL',
            'file': 'sy_glass_JL.blend',
            'types': []
        },
        'sy_lite_shiny': {
            'name': 'sy_lite_shiny',
            'file': 'sy_lite_shiny.blend',
            'types': []
        },
        'sy_white_matte': {
            'name': 'sy_white_matte',
            'file': 'sy_white_matte.blend',
            'types': []
        },
        'kc-glass-clear': {
            'name': 'kc-glass-clear',
            'file': 'sy-cyc-glass-clear.blend',
            'types': []
        },
        'sy-glass-frosted': {
            'name': 'sy-glass-frosted',
            'file': 'sy-glass-frosted.blend',
            'types': []
        },
        'white': {
            'name': 'white',
            'file': 'white.blend',
            'types': []
        },
        'window': {
            'name': 'window',
            'file': 'window.blend',
            'types': []
        },
        'wood_floor_deck': {
            'name': 'wood_floor_deck',
            'file': 'wood_floor_deck_4k.blend',
            'types': ['floor']
        },
        # '': {
        #     'name': '',
        #     'file': '',
        #     'types': []
        # },
    }

    logging.debug('ran "get_materials_info"')

    return materials


def get_random_hdri(randomness=True):
    files = os.listdir("./assets/background/")
    exr_files = [f for f in files if f.endswith(".exr")]
    assert len(exr_files) > 0, "Should have .exr files in background directory"

    if randomness:
        exr_file = exr_files[random.randint(0, len(exr_files) - 1)]
    else:
        if "dreifaltigkeitsberg_4k.exr" in exr_files:
            exr_file = "dreifaltigkeitsberg_4k.exr"
        else:
            exr_file = exr_files[0]

    logging.debug('ran "get_random_hdri"')

    return f"//assets/background/{exr_file}", exr_file


def assign_material_to_object(obj_name, material_name):
    obj = bpy.data.objects[obj_name]
    mat = bpy.data.materials[material_name]

    # Check if object has a material slot, if not, create one
    if not obj.material_slots:
        bpy.ops.object.material_slot_add({'object': obj})

    # Assign the material to the object's first material slot
    obj.material_slots[0].material = mat

    logging.debug('ran "assign_material_to_object"')


def convert_coords(dead_axis='z', dead_coord=0, bottom_left=(0, 0), top_right=(1, 1)):
    bottom_right = (top_right[0], bottom_left[1])
    top_left = (bottom_left[0], top_right[1])

    coords = []
    for coordinate in [bottom_left, bottom_right, top_right, top_left]:
        if dead_axis == 'z':
            coordinate = (coordinate[0], coordinate[1], dead_coord)
        elif dead_axis == 'y':
            coordinate = (coordinate[0], dead_coord, coordinate[1])
        elif dead_axis == 'x':
            coordinate = (dead_coord, coordinate[0], coordinate[1])

        coords.append(coordinate)

    logging.debug('ran "convert_coords"')

    return coords


def create_plane(dead_axis, dead_coord, bottom_left, top_right, material_name):
    coords = convert_coords(dead_axis, dead_coord, bottom_left, top_right)

    # create names
    object_id = uuid.uuid4().int
    mesh_name = f"Plane_{object_id}"
    obj_name = f"Plane_Object_{object_id}"

    # Create a new mesh
    mesh = bpy.data.meshes.new(name=mesh_name)
    obj = bpy.data.objects.new(obj_name, mesh)
    bpy.context.collection.objects.link(obj)

    # Make sure nothing is selected, then select the object by its name
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[obj_name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[obj_name]

    # Create the vertices and faces
    mesh.from_pydata(coords, [], [(0, 1, 2, 3)])
    mesh.update()

    assign_material_to_object(obj_name, material_name)

    logging.debug('ran "create_plane"')


def create_texture_plane(dead_axis, dead_coord, bottom_left, top_right, flip, material, has_texture=True):
    coords = convert_coords(dead_axis, dead_coord, bottom_left, top_right)

    # create names
    object_id = uuid.uuid4().int
    mesh_name = f"Plane_{object_id}"
    obj_name = f"Plane_Object_{object_id}"
    material_name = f'material_{object_id}'

    # Create a new mesh
    mesh = bpy.data.meshes.new(name=mesh_name)
    obj = bpy.data.objects.new(obj_name, mesh)
    bpy.context.collection.objects.link(obj)

    # Make sure nothing is selected, then select the object by its name
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[obj_name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[obj_name]

    # Create the vertices and faces
    mesh.from_pydata(coords, [], [(0, 1, 2, 3)])
    mesh.update()

    # UV unwrap the mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()

    for face in bm.faces:
        for loop in face.loops:
            if dead_axis == 'z':
                loop[uv_layer].uv = loop.vert.co.xy
            elif dead_axis == 'x':
                loop[uv_layer].uv = loop.vert.co.yz
            else:
                loop[uv_layer].uv = loop.vert.co.xz

    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # subdivision modifier
    mod_subsurf = obj.modifiers.new("Subdivision Modifier", "SUBSURF")
    mod_subsurf.subdivision_type = 'SIMPLE'
    mod_subsurf.levels = 7
    mod_subsurf.render_levels = 10

    # add material from library
    append_material_from_library(material['file'], material['name'])
    bpy.data.materials[material['name']].name = material_name
    assign_material_to_object(obj_name, material_name)

    if has_texture:
        mat = bpy.data.materials[material_name]
        nodes = mat.node_tree.nodes

        if flip:
            nodes['Displacement'].inputs[2].default_value = -nodes['Displacement'].inputs[2].default_value

    logging.debug('ran "create_texture_plane"')


def add_world_background(exr_file_path, strength=1.0, rotation_degrees=0.0, randomness=False):
    rotation_degrees = random.random() * 360 if randomness else rotation_degrees

    # Load the image into Blender
    image = bpy.data.images.load(exr_file_path)

    # Check if the image is loaded correctly
    if not image:
        logging.warning("Failed to load the exr image!")
        exit()

    scene = bpy.context.scene
    if not scene.world:
        new_world = bpy.data.worlds.new(name="NewWorld")
        scene.world = new_world

    # Ensure the world uses nodes
    scene.world.use_nodes = True

    # Get the node tree of the world and clear out existing nodes
    node_tree = scene.world.node_tree
    node_tree.nodes.clear()

    # Create new Environment Texture node
    environment_texture_node = node_tree.nodes.new(type='ShaderNodeTexEnvironment')
    environment_texture_node.image = image

    # Create a Background node
    background_node = node_tree.nodes.new(type='ShaderNodeBackground')
    background_node.inputs[1].default_value = strength

    # Create mapping and texture coordinate nodes for controlling rotation
    tex_coord_node = node_tree.nodes.new(type='ShaderNodeTexCoord')
    mapping_node = node_tree.nodes.new(type='ShaderNodeMapping')

    # Set the rotation in Z axis
    mapping_node.inputs["Rotation"].default_value[2] = radians(rotation_degrees)

    # Connect nodes
    node_tree.links.new(tex_coord_node.outputs["Generated"], mapping_node.inputs["Vector"])
    node_tree.links.new(mapping_node.outputs["Vector"], environment_texture_node.inputs["Vector"])
    node_tree.links.new(environment_texture_node.outputs["Color"], background_node.inputs["Color"])

    # Create and connect the World Output node
    world_output_node = node_tree.nodes.new(type='ShaderNodeOutputWorld')
    node_tree.links.new(background_node.outputs["Background"], world_output_node.inputs["Surface"])

    # add strength
    background_node.inputs[1].default_value = strength

    logging.debug('ran "add_world_background"')


def get_asset_size(obj_name):

    obj = bpy.data.objects[obj_name]

    bpy.context.view_layer.update()

    global_bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]

    x_values = [coord.x for coord in global_bbox_corners]
    y_values = [coord.y for coord in global_bbox_corners]
    z_values = [coord.z for coord in global_bbox_corners]

    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    min_z, max_z = min(z_values), max(z_values)

    logging.debug('ran "get_asset_size"')

    return (max_x - min_x, max_y - min_y, max_z - min_z)


def customize_render_quality(show_background=False, high_quality=True, image_size=1024):
    if 'Scene' not in bpy.data.scenes:
        logging.critical('Error! No scene named "Scene". Error happened in customize_render_quality()')
    bpy.data.scenes['Scene'].render.resolution_x = image_size
    bpy.data.scenes['Scene'].render.resolution_y = image_size

    if high_quality:
        bpy.data.scenes['Scene'].render.engine = 'CYCLES'
        bpy.data.scenes['Scene'].cycles.device = 'GPU'
        bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'OPTIX'
        for device in bpy.context.preferences.addons['cycles'].preferences.get_devices_for_type('OPTIX'):
            if device.type == 'OPTIX':
                device.use = True
                logging.debug(f"OPTIX device {device.name}")
        bpy.ops.wm.save_userpref()
        bpy.data.scenes['Scene'].cycles.adaptive_threshold = 0.1
    else:
        bpy.data.scenes['Scene'].render.engine = 'BLENDER_EEVEE'
        bpy.context.scene.render.film_transparent = not show_background

        # Ambient Occlusion
        bpy.context.scene.eevee.use_gtao = True
        bpy.context.scene.eevee.gtao_distance = 1.0
        bpy.context.scene.eevee.gtao_factor = 1.0
        bpy.context.scene.eevee.gtao_quality = 0.25

        # Bloom
        bpy.context.scene.eevee.use_bloom = True
        bpy.context.scene.eevee.bloom_threshold = 0.8
        bpy.context.scene.eevee.bloom_intensity = 0.05

        # Depth of Field (Assuming a camera is selected)

        # Subsurface Scattering
        bpy.context.scene.eevee.sss_samples = 10

        # Screen Space Reflections
        bpy.context.scene.eevee.use_ssr = True
        bpy.context.scene.eevee.ssr_quality = 1.0
        bpy.context.scene.eevee.ssr_thickness = 0.1
        bpy.context.scene.eevee.ssr_border_fade = 0.1

        # Shadows
        bpy.context.scene.eevee.shadow_cube_size = '1024'
        bpy.context.scene.eevee.shadow_cascade_size = '1024'
        bpy.context.scene.eevee.use_shadow_high_bitdepth = True
        bpy.context.scene.eevee.use_soft_shadows = True

        # Enable volumetric
        bpy.context.scene.eevee.use_volumetric_lights = True
        bpy.context.scene.eevee.volumetric_samples = 64

    logging.debug('ran "customize_render_quality"')


def angle_of_vectors(a, b):
    a_x, a_y = a
    b_x, b_y = b
    dot_product = a_x * b_x + a_y * b_y
    mod = sqrt(a_x * a_x + a_y * a_y) * sqrt(b_x * b_x + b_y * b_y)
    if mod == 0:
        logging.critical('Error! Angle of vectors is zero!')

    result = acos(min(1, max(-1, dot_product / mod)))

    logging.debug('ran "angle_of_vectors"')

    return result


def rotate_object_around_point(object_name, point=(0, 0, 0), rotation=45, axis='Z'):

    bpy.ops.object.select_all(action='DESELECT')
    if object_name in bpy.data.objects:
        obj = bpy.data.objects[object_name]
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        original_pivot = bpy.context.scene.tool_settings.transform_pivot_point
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        bpy.context.scene.cursor.location = point

        bpy.ops.transform.rotate(value=radians(rotation), orient_axis=axis)

        bpy.context.scene.tool_settings.transform_pivot_point = original_pivot

    else:
        logging.warning(f"Object named {object_name} does not exist in the current scene.")

    logging.debug('ran "rotate_object_around_point"')


def add_camera(asset_size, randomness=True):
    x, y, z = asset_size
    y_camera_random = random.random() if randomness else 0.5
    z_camera_random = random.random() if randomness else 0.5
    y_camera = -((y / 2) + (max(x, z) * (1 + y_camera_random * 2)))
    z_alternative = ((x + y) / 3) + z_camera_random * ((x + y) / 3)
    z_camera = min(max(max((z * 0.2) + (z_camera_random * z * 1.3), z_alternative), 0.3), 1.8)
    angle = atan2(abs(y_camera), z_camera - (z / 2))
    distance = (abs(y_camera) ** 2 + (z_camera - (z / 2)) ** 2) ** 0.5

    camera_position = (0.0, round(y_camera, 6), round(z_camera, 6))
    cam_data = bpy.data.cameras.new(name="Camera")
    cam_object = bpy.data.objects.new("ProductCamera", cam_data)
    bpy.context.collection.objects.link(cam_object)
    cam_object.location = camera_position
    cam_object.rotation_euler = (angle, 0, 0)
    bpy.context.scene.camera = cam_object
    logging.debug('camera added')

    x_fov_angle = atan2(x / 2, abs(y_camera) - (y / 2))
    z_fov_angle = angle_of_vectors(
        (abs(y_camera), z_camera - (z / 2)),
        (abs(y_camera) - (y / 2), z_camera)
    )
    fov_angle = max(z_fov_angle, x_fov_angle)
    logging.info(f'fov angles: {z_fov_angle} {x_fov_angle}')

    if 'Camera' not in bpy.data.cameras:
        logging.critical('Error! No camera named "Camera". Error happened in add_camera()')

    bpy.data.cameras['Camera'].lens_unit = 'FOV'
    bpy.data.cameras['Camera'].angle = fov_angle * 2 * 1.2
    # bpy.context.active_object.data.dof.use_dof = True
    # bpy.context.active_object.data.dof.focus_distance = 2
    # bpy.context.active_object.data.dof.aperture_fstop = 0.8

    camera_rotation_random = random.random() - 0.5 if randomness else 0
    camera_rotation = camera_rotation_random * 40

    rotate_object_around_point("ProductCamera", rotation=camera_rotation)
    camera_position = tuple(cam_object.location)
    logging.info(f'cam position and angle: {camera_position} {angle}')

    logging.debug('ran "add_camera"')

    return camera_position, camera_rotation, distance


def add_light(name, location, radius, energy, light_type='POINT'):
    light_data = bpy.data.lights.new(name=name, type=light_type)
    light_object = bpy.data.objects.new(name, light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = location
    bpy.data.lights[name].energy = energy

    if light_type == 'POINT':
        bpy.data.lights[name].shadow_soft_size = radius
    elif light_type == 'AREA':
        bpy.data.lights[name].shape = 'DISK'
        bpy.data.lights[name].size = radius

    logging.debug('ran "add_light"')


def add_point_lights(asset_size):
    x, y, z = asset_size
    x_light = x / 2 * 1.5
    y_light = y / 2 * 1.5
    z_light = max(x, y, z) * 2.5

    distance_to_center = (x_light ** 2 + y_light ** 2 + (z_light - (z / 2)) ** 2) ** 0.5
    radius = distance_to_center / 6
    energy = distance_to_center * 30

    add_light('back_left_light', (-x_light, y_light, z_light), radius, energy, 'POINT')
    add_light('back_right_light', (x_light, y_light, z_light), radius, energy, 'POINT')
    add_light('front_light', (0, -y_light, z_light), radius, energy / 2, 'POINT')

    logging.debug('ran "add_point_lights"')


def take_picture(folder, image_name):
    folder_path = f'./output/{folder}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    bpy.context.scene.render.filepath = f'//output/{folder}/{image_name}.png'
    bpy.ops.render.render(write_still=True)

    logging.debug('ran "take_picture"')


def define_skip_assets():
    to_skip = [
        'plant_25', 'plant_18', 'plant_16', 'plant_12', 'plant_10', 'decor_20', 'painting_04', 'decor_27',
        'decor_07_01', 'decor_07_02', 'decor_05', 'clock_09', 'clock_08', 'clock_07', 'clock_04_02', 'clock_04_01',
        'lamp_89_02', 'lamp_89_01', 'lamp_88_04', 'lamp_88_03', 'lamp_88_02', 'lamp_88_01', 'lamp_87_02', 'lamp_87_01',
        'lamp_86_02', 'lamp_86_01', 'lamp_85', 'lamp_84', 'lamp_83', 'lamp_82_04', 'lamp_82_03', 'lamp_82_02',
        'lamp_82_01', 'lamp_81_08', 'lamp_81_07', 'lamp_81_06', 'lamp_81_05', 'lamp_81_04', 'lamp_81_03', 'lamp_81_02',
        'lamp_81_01', 'lamp_80', 'lamp_79', 'lamp_78_02', 'lamp_78_01', 'lamp_77', 'lamp_76_02', 'lamp_76_01',
        'lamp_75_05', 'lamp_75_04', 'lamp_75_03', 'lamp_75_02', 'lamp_75_01', 'lamp_74_13', 'lamp_74_12', 'lamp_74_11',
        'lamp_74_10', 'lamp_74_09', 'lamp_74_08', 'lamp_74_07', 'lamp_74_06', 'lamp_74_05', 'lamp_74_04', 'lamp_74_03',
        'lamp_74_02', 'lamp_74_01', 'lamp_73_02', 'lamp_73_01', 'lamp_72', 'lamp_71', 'lamp_70_04', 'lamp_70_03',
        'lamp_70_02', 'lamp_70_01', 'lamp_69', 'lamp_68', 'lamp_67', 'lamp_66', 'lamp_65', 'lamp_47', 'shelf_87_02',
        'shelf_87_01', 'shelf_64_02', 'shelf_64_01', 'shelf_52_08', 'shelf_52_07', 'shelf_52_06', 'shelf_52_05',
        'shelf_52_04', 'shelf_52_03', 'shelf_52_02', 'shelf_52_01', 'shelf_22', 'shelf_20_04', 'shelf_20_03',
        'shelf_20_02', 'shelf_20_01', 'shelf_18_02', 'shelf_18_01', 'shelf_16_02', 'shelf_16_01', 'shelf_04',
        'tableset_05'
    ]

    logging.debug('ran "define_skip_assets"')

    return to_skip


def create_window_wall(
        dead_axis, dead_coord, left, right, z_top, flip, wall_material_name, window_material_name, glass_material_name,
        overlap, randomness):

    windows_random = random.random() if randomness else 0.5
    wall_border_random = random.random() if randomness else 0.5
    window_width_random = random.random() if randomness else 0.5
    is_window_random = random.randint(0, 1) if randomness else 1
    below_window_random = random.random() if randomness else 0.5
    above_window_random = random.random() if randomness else 0.5
    window_border_random = random.random() if randomness else 0.5

    wall_width = right - left
    windows = max(math.floor(windows_random * wall_width), 1)
    wall_border = max((wall_width - windows * 1.5) * wall_border_random, 0.2)
    window_space = (wall_width - wall_border) / windows
    window_width = min(window_space - 0.2, max(0.8, window_space * window_width_random))
    window_side_space = (window_space - window_width) / 2
    border_space = window_side_space + wall_border / 2
    below_window = 0.8 + below_window_random * 0.4 if is_window_random else 0.05
    above_window = 0.1 + above_window_random * 0.4
    window_border = 0.03 + 0.05 * window_border_random

    logging.info(f'wall: {dead_axis} {round(dead_coord, 2)} / width: {round(wall_width, 2)}, windows: {windows} \
border space: {round(border_space, 2)}')

    # border before first and after last window
    create_plane(
        dead_axis, dead_coord, (left - overlap, 0 - overlap), (left + border_space, z_top + overlap),
        wall_material_name
    )
    create_plane(
        dead_axis, dead_coord, (right - border_space, 0 - overlap), (right + overlap, z_top + overlap),
        wall_material_name
    )

    for i in range(0, windows):
        right_window_side = left + border_space + window_width + i * (window_space)
        left_window_side = right_window_side - window_width

        # below window
        create_plane(
            dead_axis,
            dead_coord,
            (left_window_side, 0 - overlap),
            (right_window_side, below_window),
            wall_material_name
        )

        # above window
        create_plane(
            dead_axis,
            dead_coord,
            (left_window_side, z_top - above_window),
            (right_window_side, z_top + overlap),
            wall_material_name
        )

        if dead_axis == 'x':
            dead_border_axis = 'y'
        else:
            dead_border_axis = 'x'

        if flip:
            outside_wall = dead_coord + 0.2
        else:
            outside_wall = dead_coord - 0.2

        wall_middle = (outside_wall + dead_coord) / 2

        # window glass
        create_plane(
            dead_axis,
            wall_middle,
            (left_window_side, below_window),
            (right_window_side, z_top - above_window),
            glass_material_name
        )

        # window vertical
        for coord, inside_coord in zip(
            [left_window_side, right_window_side],
            [left_window_side + window_border, right_window_side - window_border]
        ):

            create_plane(
                dead_border_axis,
                coord,
                (dead_coord, below_window),
                (outside_wall, z_top - above_window),
                wall_material_name
            )

            create_plane(
                dead_border_axis,
                inside_coord,
                (wall_middle - 0.02, below_window),
                (wall_middle + 0.02, z_top - above_window),
                window_material_name
            )

            for window_side in [wall_middle - 0.02, wall_middle + 0.02]:
                create_plane(
                    dead_axis,
                    window_side,
                    (coord, below_window),
                    (inside_coord, z_top - above_window),
                    window_material_name
                )

        # window horizontal
        for coord, inside_coord in zip(
            [below_window, z_top - above_window],
            [below_window + window_border, z_top - above_window - window_border]
        ):
            c1 = (dead_coord, left_window_side)
            c2 = (outside_wall, right_window_side)
            if dead_axis == 'y':
                c1 = (c1[1], c1[0])
                c2 = (c2[1], c2[0])
            create_plane('z', coord, c1, c2, wall_material_name)

            c1 = (wall_middle - 0.02, left_window_side)
            c2 = (wall_middle + 0.02, right_window_side)
            if dead_axis == 'y':
                c1 = (c1[1], c1[0])
                c2 = (c2[1], c2[0])
            create_plane('z', inside_coord, c1, c2, window_material_name)

            for window_side in [wall_middle - 0.02, wall_middle + 0.02]:
                create_plane(
                    dead_axis,
                    window_side,
                    (left_window_side + window_border, coord),
                    (right_window_side - window_border, inside_coord),
                    window_material_name
                )

        # between windows
        if i < windows - 1:
            create_plane(
                dead_axis,
                dead_coord,
                (right_window_side, 0 - overlap),
                (right_window_side + (window_side_space * 2), z_top + overlap),
                wall_material_name
            )

    logging.debug('ran "create_window_wall"')


def create_room(asset_size, camera_position, materials, hdri_name, randomness=True):
    x_left_random = random.random() if randomness else 0.5
    x_right_random = random.random() if randomness else 0.5
    y_behind_random = random.random() if randomness else 0.5
    y_front_random = random.random() if randomness else 0.5
    z_random = random.random() if randomness else 0.5

    z_top = max(asset_size[2] + 0.2, 2) + (z_random * 1.2)
    x_left = (min(-asset_size[0] / 2, camera_position[0]) - 0.4 - (x_left_random * 2))
    x_right = (max(asset_size[0] / 2, camera_position[1]) + 0.4 + (x_right_random * 2))
    y_behind = (asset_size[1] / 2) + 0.05 + (y_behind_random * 0.45)
    y_front = camera_position[1] - 0.2 - (y_front_random * 2.8)

    width = x_right - x_left
    depth = y_behind - y_front

    if x_right - x_left < 1:
        x_left -= (1 - width) / 2
        x_right += (1 - width) / 2

    if y_behind - y_front < 1:
        y_front -= (1 - depth) / 2
        y_behind += (1 - depth) / 2

    width = round(x_right - x_left, 2)
    depth = round(y_behind - y_front, 2)
    height = round(z_top, 2)

    logging.info(f'Room size: width = {width}, depth = {depth}, height = {height}')

    overlap = 0.1

    # floor
    if randomness:
        floor_materials = [material for material, value in materials.items() if 'floor' in value['types']]
        floor_material = materials[floor_materials[random.randint(0, len(floor_materials) - 1)]]
    else:
        floor_material = materials['laminate_floor_02']

    create_texture_plane(
        'z',
        0,
        (x_left - overlap, y_front - overlap),
        (x_right + overlap, y_behind + overlap),
        False,
        floor_material
    )

    # ceiling
    if randomness:
        ceiling_materials = [material for material, value in materials.items() if 'ceiling' in value['types']]
        ceiling_material = materials[ceiling_materials[random.randint(0, len(ceiling_materials) - 1)]]
    else:
        ceiling_material = materials['ceiling_interior']

    create_texture_plane(
        'z',
        z_top,
        (x_left - overlap, y_front - overlap),
        (x_right + overlap, y_behind + overlap),
        True,
        ceiling_material
    )

    # light
    needs_light = [
        'dikhololo_night_4k.exr',
        'hansaplatz_4k.exr',
        'moonless_golf_4k.exr',
        'sandsloot_4k.exr',
        'satara_night_no_lamps_4k.exr',
    ]

    if hdri_name in needs_light:
        x_light = (x_left + x_right) / 2
        y_light = (y_front + y_behind) / 2
        light_radius_random = random.random() if randomness else 0.5
        light_energy_random = random.random() if randomness else 0.5
        light_radius = 0.2 + 0.8 * light_radius_random
        light_energy = 10 + 40 * light_energy_random

        add_light('room_light', (x_light, y_light, z_top - 0.1), light_radius, light_energy, 'AREA')

    # product wall
    if randomness:
        wall_materials = [material for material, value in materials.items() if 'wall' in value['types']]
        wall_material = materials[wall_materials[random.randint(0, len(wall_materials) - 1)]]
    else:
        wall_material = materials['brick_wall_02']

    create_texture_plane(
        'y',
        y_behind,
        (x_left - overlap, 0 - overlap),
        (x_right + overlap, z_top + overlap),
        False,
        wall_material
    )

    # other walls
    wall_material_name = add_and_rename_material(materials, 'sy_white_matte')
    window_material_name = add_and_rename_material(materials, 'sy_lite_shiny')
    glass_material_name = add_and_rename_material(materials, 'window')

    for dead_axis, dead_coord, left, right, flip in zip(
        ['x', 'x', 'y'],
        [x_left, x_right, y_front],
        [y_front, y_front, x_left],
        [y_behind, y_behind, x_right],
        [False, True, False],
    ):
        logging.debug('Just before creating a window wall')
        create_window_wall(
            dead_axis, dead_coord, left, right, z_top, flip, wall_material_name, window_material_name,
            glass_material_name, overlap, randomness
        )

    logging.debug('ran "create_room"')


def connect_nodes(node_tree, from_node, from_socket_name, to_node, to_socket_name):
    for socket in from_node.outputs:
        if socket.name == from_socket_name:
            for to_socket in to_node.inputs:
                if to_socket.name == to_socket_name:
                    link = node_tree.links.new
                    link(socket, to_socket)
                    return


def select_node_by_type(node_tree, node_type):
    selected_node = None
    for node in node_tree.nodes:
        if node.type == node_type:
            selected_node = node
            break

    return selected_node


def add_node_group_to_material(material, node_group_name, output_socket_name):
    node_group = bpy.data.node_groups.get(node_group_name)

    if node_group is None:
        print("Node group not found!")

    node_tree = material.node_tree

    output_node = select_node_by_type(node_tree, 'OUTPUT_MATERIAL')

    if not output_node:
        return

    for link in node_tree.links:
        if link.to_socket.name == "Surface" and link.to_node.type == 'OUTPUT_MATERIAL':
            previous_node_type = link.from_node.type
            previous_socket_name = link.from_socket.name

    group_node = node_tree.nodes.new(type='ShaderNodeGroup')
    group_node.node_tree = node_group
    group_node.location = (output_node.location.x - 300, output_node.location.y)

    connect_nodes(node_tree, group_node, output_socket_name, output_node, "Surface")

    previous_node = select_node_by_type(node_tree, previous_node_type)
    return previous_node, previous_socket_name, output_node


def add_node_group_to_all_materials(node_group_name, output_socket_name):
    for material in bpy.data.materials:
        if material.use_nodes:
            add_node_group_to_material(material, node_group_name, output_socket_name)


def save_metadata(folder, file_name, asset, camera_position, camera_rotation, distance, hdri_name, time_difference):
    folder_path = f'./output/{folder}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = f'./output/{folder}/{file_name}.json'
    metadata = {
        'asset': asset,
        'camera_position': camera_position,
        'camera_rotation': camera_rotation,
        'distance': distance,
        'hdri_name': hdri_name,
        'time_to_compute': time_difference
    }
    with open(file_path, 'w') as outfile:
        json.dump(metadata, outfile)

    logging.debug('ran "save_metadata"')


def set_to_diffuse_rendering():
    bpy.data.scenes["Scene"].use_nodes = True
    bpy.data.scenes["Scene"].view_layers["ViewLayer"].use_pass_diffuse_color = True
    node_tree = bpy.data.scenes["Scene"].node_tree
    connect_nodes(node_tree, node_tree.nodes["Render Layers"], "DiffCol", node_tree.nodes["Composite"], "Image")


def reset_to_image_rendering():
    node_tree = bpy.data.scenes["Scene"].node_tree
    connect_nodes(node_tree, node_tree.nodes["Render Layers"], "Image", node_tree.nodes["Composite"], "Image")


def run_main():

    logging.info("Started Program")
    print(f"Python Version: {sys.version}")
    print(f"Blender Version: {bpy.app.version_string}")

    customize_render_quality(show_background=True, high_quality=True)
    to_skip = define_skip_assets()
    materials = get_materials_info()
    assets = get_assets_info()
    experiment_name = 'experiment_73'

    #  "beds", "cabinets",  "chairs"
    # ["decor", "electronics", "lamps", "plants", "shelves", "sofas", "tables", "tablesets"]
    # assets = {a: v for a, v in assets.items() if v["category"] == category}
    # asset = assets[list(assets.keys())[i]]

    for i in range(30):
        start_time = time.time()
        asset = get_random_asset(assets, nonrandom_asset="cabinet_38_02", randomness=True)
        logging.info(f"Got asset '{asset['name']}' of type '{asset['category']}'")

        if asset["name"] in to_skip:
            continue

        remove_old_objects()
        add_asset(f"//assets/interior_models/{asset['file']}", asset['name'], 0, randomness=True)
        asset_size = get_asset_size(asset['name'])
        if asset_size[2] > 2.6:
            logging.debug('ran "asset skipped because too big"')
            continue

        camera_position, camera_rotation, distance = add_camera(asset_size, randomness=True)
        bpy.data.objects[asset['name']].rotation_euler[2] += radians(-camera_rotation)
        asset_size = get_asset_size(asset['name'])
        logging.debug(f'cam at: {camera_position} with distance {distance}')

        add_world_background("//assets/background/abandoned_slipway_4k.exr", 1, 270, randomness=False)
        logging.debug('added world background')

        add_asset("//assets/custom_planes/plane_03.blend", 'Plane_03', rotation_degrees=0, randomness=False)
        logging.debug('added plane asset')

        add_point_lights(asset_size)
        logging.debug('added point lights')

        take_picture(experiment_name, f'{i}__8')

        # for object in ["Plane_03"]:
        #     bpy.data.objects[object].hide_render = True
        #     bpy.data.objects[object].hide_viewport = True

        # add_asset("//assets/custom_planes/plane_05.blend", 'Plane_05', rotation_degrees=0, randomness=False)
        # logging.debug('added plane asset')

        # take_picture(experiment_name, f'{i}__9')

        # for object in ["Plane_05"]:
        #     bpy.data.objects[object].hide_render = True
        #     bpy.data.objects[object].hide_viewport = True

        # add_asset("//assets/custom_planes/plane_06.blend", 'Plane_06', rotation_degrees=0, randomness=False)
        # logging.debug('added plane asset')

        # take_picture(experiment_name, f'{i}__10')

        # for object in ["Plane_06"]:
        #     bpy.data.objects[object].hide_render = True
        #     bpy.data.objects[object].hide_viewport = True

        # add_asset("//assets/custom_planes/plane_07.blend", 'Plane_07', rotation_degrees=0, randomness=False)
        # logging.debug('added plane asset')

        # take_picture(experiment_name, f'{i}__11')

        # for object in ["Plane_07"]:
        #     bpy.data.objects[object].hide_render = True
        #     bpy.data.objects[object].hide_viewport = True

        # for object in ["Plane_03"]:
        #     bpy.data.objects[object].hide_render = False
        #     bpy.data.objects[object].hide_viewport = False

        # add_asset("//assets/custom_planes/plane_03.blend", 'Plane_03', rotation_degrees=0, randomness=False)
        # logging.debug('added plane asset')

        # add_point_lights(asset_size)
        # logging.debug('added point lights')

        # take_picture(experiment_name, f'{i}__5')

        # for object in ["Plane_03"]:
        #     bpy.data.objects[object].hide_render = True
        #     bpy.data.objects[object].hide_viewport = True

        # for object in ["Plane_05"]:
        #     bpy.data.objects[object].hide_render = False
        #     bpy.data.objects[object].hide_viewport = False

        # add_asset("//assets/custom_planes/plane_05.blend", 'Plane_05', rotation_degrees=0, randomness=False)
        # logging.debug('added plane asset')

        # take_picture(experiment_name, f'{i}__6')

        # for object in ["Plane_05"]:
        #     bpy.data.objects[object].hide_render = True
        #     bpy.data.objects[object].hide_viewport = True

        # append_node_group_from_library("pitch_black.blend", "get_pitch_black")
        # asset_material = bpy.data.objects[asset['name']].active_material
        # previous_node, previous_socket_name, output_node = add_node_group_to_material(
        #     asset_material, "get_pitch_black", 'Value'
        # )

        # add_asset("//assets/custom_planes/plane_04.blend", 'Plane_04', rotation_degrees=0, randomness=False)

        # take_picture(experiment_name, f'{i}__4')

        # connect_nodes(asset_material.node_tree, previous_node, previous_socket_name, output_node, "Surface")

        # take_picture(experiment_name, f'{i}__7')

        # for object in ["Plane_04", "back_left_light", "back_right_light", "front_light"]:
        #     bpy.data.objects[object].hide_render = True
        #     bpy.data.objects[object].hide_viewport = True

        # hdri, hdri_name = get_random_hdri(randomness=True)
        # add_world_background(hdri, 1.0, 90, randomness=True)

        # create_room(asset_size, camera_position, materials, hdri_name, randomness=True)
        # take_picture(experiment_name, f'{i}__1')

        # # set_to_diffuse_rendering()
        # # take_picture(experiment_name, f'{i}__7')
        # # reset_to_image_rendering()

        # # get_image_difference(experiment_name, f'{i}__7', f'{i}__1', f'{i}__8')

        # append_node_group_from_library("normal.blend", "get_normal")
        # add_node_group_to_all_materials("get_normal", 'Emission')
        # take_picture(experiment_name, f'{i}__2')

        # append_node_group_from_library("distance.blend", "get_distance")
        # add_node_group_to_all_materials("get_distance", 'Emission')
        # take_picture(experiment_name, f'{i}__3')

        hdri_name = 'temp wrong #TODO'

        end_time = time.time()
        time_difference = int(end_time - start_time)
        save_metadata(
            experiment_name, f'{i}__0', asset, camera_position, camera_rotation, distance, hdri_name, time_difference
        )

    logging.info('Done!')


run_main()
