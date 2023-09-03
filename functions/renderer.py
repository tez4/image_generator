import os
import bpy
import uuid
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


logging = SimpleLogger(level=SimpleLogger.INFO)


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


def create_glowing_material():
    new_material = bpy.data.materials.new(name="GlowingMaterial")

    new_material.use_nodes = True
    nodes = new_material.node_tree.nodes

    material_output = nodes.get("Material Output")
    node_emission = nodes.new(type='ShaderNodeEmission')

    node_emission.inputs[0].default_value = (0.0, 0.3, 1.0, 1)
    node_emission.inputs[1].default_value = 500.0

    links = new_material.node_tree.links
    links.new(node_emission.outputs[0], material_output.inputs[0])

    return new_material


def create_glowing_object(material, size=1, location=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    so = bpy.context.active_object

    so.rotation_euler[0] = 5

    mod_subsurf = so.modifiers.new("My Modifier", "SUBSURF")
    mod_subsurf.levels = 5
    mod_subsurf.render_levels = 5

    bpy.ops.object.shade_smooth()

    mod_displace = so.modifiers.new("Displacement", "DISPLACE")
    mod_displace.strength = 0.03 * size

    new_tex = bpy.data.textures.new("texture", "DISTORTED_NOISE")
    new_tex.noise_scale = 0.05 * size

    mod_displace.texture = new_tex

    # add material
    so.data.materials.append(material)


def find_assets(blend_file_path="//assets/interior_models/1000_plants_bundle.blend"):
    assets = []

    # Read the .blend file
    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, _):
        for value in data_from.objects:
            assets.append(value)

    return assets


def add_asset(
        filepath="./assets/interior_models/1000_plants_bundle.blend/Object/", name='plant_24', rotation_degrees=0.0,
        randomness=False):

    rotation_degrees = random.random() * 360 if randomness else rotation_degrees
    bpy.ops.wm.append(directory=filepath, filename=name)
    obj = bpy.data.objects[name]
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, radians(rotation_degrees))


def append_material_from_library(blend_path, material_name):
    # Define the path to the material inside the .blend file
    material_path = f"./assets/materials/{blend_path}/{blend_path}/Material/"

    # Append the material
    bpy.ops.wm.append(filename=material_name, directory=material_path)


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

    return materials


def assign_material_to_object(obj_name, material_name):
    obj = bpy.data.objects[obj_name]
    mat = bpy.data.materials[material_name]

    # Check if object has a material slot, if not, create one
    if not obj.material_slots:
        bpy.ops.object.material_slot_add({'object': obj})

    # Assign the material to the object's first material slot
    obj.material_slots[0].material = mat


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

    return coords


def create_plane_from_coords(dead_axis, dead_coord, bottom_left, top_right, flip, material, has_texture=True):
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

    # bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')

    # subdivision modifier
    mod_subsurf = obj.modifiers.new("Subdivision Modifier", "SUBSURF")
    mod_subsurf.subdivision_type = 'SIMPLE'
    mod_subsurf.levels = 6
    mod_subsurf.render_levels = 6

    # add material from library
    append_material_from_library(material['file'], material['name'])
    bpy.data.materials[material['name']].name = material_name
    assign_material_to_object(obj_name, material_name)

    if has_texture:
        mat = bpy.data.materials[material_name]
        nodes = mat.node_tree.nodes

        if flip:
            nodes['Displacement'].inputs[2].default_value = -nodes['Displacement'].inputs[2].default_value


def create_base_plane():
    # add base plane
    bpy.ops.mesh.primitive_plane_add(
        size=250, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    plane = bpy.context.active_object

    mat = bpy.data.materials.new(name="GlossyWhite")

    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    glossy_shader = nodes.new(type='ShaderNodeBsdfGlossy')
    glossy_shader.location = (0, 0)

    glossy_shader.inputs["Color"].default_value = (1, 1, 1, 1)  # RGB + Alpha
    glossy_shader.inputs["Roughness"].default_value = 0.1  # Adjust as needed

    # Add a Material Output node and connect the Glossy shader to it
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (400, 0)
    mat.node_tree.links.new(
        glossy_shader.outputs["BSDF"], material_output.inputs["Surface"])

    # Assign the material to the plane
    plane.data.materials.append(mat)


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


def get_asset_size(obj_name='plant_24'):

    obj = bpy.data.objects[obj_name]

    bpy.context.view_layer.update()

    global_bbox_corners = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]

    x_values = [coord.x for coord in global_bbox_corners]
    y_values = [coord.y for coord in global_bbox_corners]
    z_values = [coord.z for coord in global_bbox_corners]

    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    min_z, max_z = min(z_values), max(z_values)

    return (max_x - min_x, max_y - min_y, max_z - min_z)


def customize_render_quality(show_background=False, high_quality=True, image_size=1024):
    if 'Scene' not in bpy.data.scenes:
        logging.critical('Error! No scene named "Scene". Error happened in customize_render_quality()')
    bpy.data.scenes['Scene'].render.resolution_x = image_size
    bpy.data.scenes['Scene'].render.resolution_y = image_size

    if high_quality:
        bpy.data.scenes['Scene'].render.engine = 'CYCLES'
        bpy.data.scenes['Scene'].cycles.device = 'GPU'
        bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
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


def angle_of_vectors(a, b):
    a_x, a_y = a
    b_x, b_y = b
    dot_product = a_x * b_x + a_y * b_y
    mod = sqrt(a_x * a_x + a_y * a_y) * sqrt(b_x * b_x + b_y * b_y)
    if mod == 0:
        logging.critical('Error! Angle of vectors is zero!')
    return acos(min(1, max(-1, dot_product / mod)))


def add_camera(asset_size, randomness=True):
    x, y, z = asset_size
    y_camera_random = random.random() if randomness else 0.5
    z_camera_random = random.random() if randomness else 0.5
    y_camera = -((y / 2) + (max(x, z) * (1 + y_camera_random * 2)))
    z_camera = min(max((z * 0.2) + (z_camera_random * z * 1.3), 0.3), 1.8)
    angle = atan2(abs(y_camera), z_camera - (z / 2))
    distance = (abs(y_camera) ** 2 + (z_camera - (z / 2)) ** 2) ** 0.5

    camera_position = (0.0, round(y_camera, 6), round(z_camera, 6))

    logging.info(f'cam position and angle: { camera_position} {angle}')
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
    bpy.data.cameras['Camera'].angle = fov_angle * 2
    # bpy.context.active_object.data.dof.use_dof = True
    # bpy.context.active_object.data.dof.focus_distance = 2
    # bpy.context.active_object.data.dof.aperture_fstop = 0.8

    return camera_position, distance


def add_point_light(name, location, radius, energy):
    light_data = bpy.data.lights.new(name=name, type='POINT')
    light_object = bpy.data.objects.new(name, light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = location
    bpy.data.lights[name].energy = energy
    bpy.data.lights[name].shadow_soft_size = radius


def add_point_lights(asset_size):
    x, y, z = asset_size
    x_light = x / 2 * 1.5
    y_light = y / 2 * 1.5
    z_light = z * 2.5

    distance_to_center = (x_light ** 2 + y_light ** 2 + (z_light - (z / 2)) ** 2) ** 0.5
    radius = distance_to_center / 6
    energy = distance_to_center * 30

    add_point_light('back_left_light', (-x_light, y_light, z_light), radius, energy)
    add_point_light('back_right_light', (x_light, y_light, z_light), radius, energy)
    add_point_light('front_light', (0, -y_light, z_light), radius, energy / 2)


def take_picture(folder, image_name):
    folder_path = f'./output/{folder}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    bpy.context.scene.render.filepath = f'//output/{folder}/{image_name}.png'
    bpy.ops.render.render(write_still=True)
    # bpy.data.images.remove(bpy.data.images['Render Result'])


def define_skip_assets():
    to_skip = [
        'plant_25',
        'plant_18',
        'plant_16',
        'plant_12',
        'plant_10',
    ]

    return to_skip


def run_main():
    logging.info("Started Program")

    customize_render_quality(show_background=True, high_quality=False)
    to_skip = define_skip_assets()
    materials = get_materials_info()
    experiment_name = 'experiment_26'

    assets = find_assets("//assets/interior_models/1000_plants_bundle.blend")
    for i, asset in enumerate(assets):
        if i > 1:
            break
        if asset in to_skip:
            continue

        remove_old_objects()
        logging.debug('Removed objects')
        add_asset("./assets/interior_models/1000_plants_bundle.blend/Object/", asset, 0, randomness=True)
        logging.debug('Added asset')
        asset_size = get_asset_size(asset)
        logging.info(asset_size)
        if asset_size[2] > 2.6:
            continue

        camera_position, distance = add_camera(asset_size, randomness=True)
        logging.debug(f'cam at: {camera_position} with distance {distance}')
        logging.debug('Added camera')

        add_asset("./assets/custom_planes/plane_01.blend/Object/", 'Plane_01', rotation_degrees=0, randomness=False)

        add_world_background("//assets/background/abandoned_slipway_4k.exr", 0.5, 270, randomness=False)
        logging.debug('Added background')
        add_point_lights(asset_size)

        take_picture(experiment_name, f'{i}__2_{asset}')

        for object in ["Plane_01", "back_left_light", "back_right_light", "front_light"]:
            bpy.data.objects[object].hide_render = True
            bpy.data.objects[object].hide_viewport = True

        create_plane_from_coords('z', 0, (-1, -2), (1, 1), False, materials['laminate_floor_02'])
        create_plane_from_coords('z', 2, (-1, -2), (1, 1), True, materials['ceiling_interior'])
        create_plane_from_coords('y', 1, (-1, 0), (1, 2), False, materials['brick_wall_02'])
        create_plane_from_coords('x', -1, (-2, 0), (1, 2), False, materials['concrete_wall_008'])
        create_plane_from_coords('x', 1, (0, 0), (1, 2), True, materials['brick_wall_006'])

        # create_base_plane()
        # hdri = ['cloudy_vondelpark_4k', 'abandoned_slipway_4k']
        add_world_background("//assets/background/dreifaltigkeitsberg_4k.exr", 1.0, 90, randomness=True)
        logging.debug('Added background')

        take_picture(experiment_name, f'{i}__1_{asset}')
        logging.debug('Took picture')

    logging.info('Done!')

    # for i, material in enumerate(materials.keys()):
    #     if len(materials[material]['types']) > 0:
    #         remove_old_objects()
    #         add_camera((1.5, 1.5, 1.5), False)

    #         create_plane_from_coords('z', 0, (-1, -2), (1, 1), False, materials[material])
    #         create_plane_from_coords('z', 2, (-1, -2), (1, 1), True, materials[material])
    #         create_plane_from_coords('y', 1, (-1, 0), (1, 2), False, materials[material])
    #         create_plane_from_coords('x', -1, (-2, 0), (1, 2), False, materials[material])
    #         create_plane_from_coords('x', 1, (-2, 0), (1, 2), True, materials[material])

    #         add_world_background("//assets/background/abandoned_slipway_4k.exr", 1.0)

    #         take_picture(experiment_name, f'{i}____{material}')

    # logging.info('Done!')


run_main()
