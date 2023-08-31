import bpy
import uuid
import random
from math import radians


def remove_old_objects():
    # Ensure we're in Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Delete all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

    # Delete all textures
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture)

    # Armatures and Bone Groups
    for armature in bpy.data.armatures:
        bpy.data.armatures.remove(armature)

    # Particles
    for particle in bpy.data.particles:
        bpy.data.particles.remove(particle)

    # Worlds
    for world in bpy.data.worlds:
        bpy.data.worlds.remove(world)

    # Grease Pencils
    for pencil in bpy.data.grease_pencils:
        bpy.data.grease_pencils.remove(pencil)

    # Cameras
    for camera in bpy.data.cameras:
        bpy.data.cameras.remove(camera)

    # Lamps/Lights
    for light in bpy.data.lights:
        bpy.data.lights.remove(light)

    # Meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

    # Images
    for image in bpy.data.images:
        bpy.data.images.remove(image)


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


def find_assets():
    blend_file_path = "//assets/interior_models/1000_plants_bundle.blend"

    # Read the .blend file
    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, _):
        for value in data_from.objects:
            print(value)


def add_asset():
    name = 'plant_24'
    filepath = "./assets/interior_models/1000_plants_bundle.blend/Object/"
    bpy.ops.wm.append(directory=filepath, filename=name)
    bpy.data.objects[name].location = (0, 2, 0)


def append_material_from_library(blend_path, material_name):
    # Define the path to the material inside the .blend file
    material_path = f"./assets/materials/{blend_path}/{blend_path}/Material/"

    # Append the material
    bpy.ops.wm.append(filename=material_name, directory=material_path)


def get_materials_dictionary():
    materials = {
        'brick_wall_02_4k.blend': 'brick_wall_02',
        'concrete_wall_008_4k.blend': 'concrete_wall_008',
        'laminate_floor_02_4k.blend': 'laminate_floor_02',
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


def create_floor(material_key):
    object_id = uuid.uuid4().int
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    bpy.data.objects['Plane'].name = f'Plane_{object_id}'
    # so.scale = (3, 7, 1)

    # bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0), scale=(7, 7, 0.3))
    # assign_material_to_object(so, material)


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


def create_plane_from_coords(dead_axis, dead_coord, bottom_left, top_right, material_key, material_value):
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
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')

    # add material from library
    append_material_from_library(material_key, material_value)
    bpy.data.materials[material_value].name = material_name
    assign_material_to_object(obj_name, material_name)

    mat = bpy.data.materials[material_name]
    nodes = mat.node_tree.nodes
    mapping_node = nodes.get('Mapping')
    x_scale = abs(top_right[0] - bottom_left[0])
    y_scale = abs(top_right[1] - bottom_left[1])
    mapping_node.inputs['Scale'].default_value = (x_scale, y_scale, 1.0)


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


def add_world_background(exr_file_path):

    # Load the image into Blender
    image = bpy.data.images.load(exr_file_path)

    # Check if the image is loaded correctly
    if not image:
        print("Failed to load the image!")
        exit()

    scene = bpy.context.scene
    if not scene.world:
        new_world = bpy.data.worlds.new(name="NewWorld")
        scene.world = new_world

    # Ensure the world uses nodes
    scene.world.use_nodes = True

    # Get the node tree of the world
    node_tree = scene.world.node_tree

    # Check for an existing Environment Texture node
    environment_texture_node = next(
        (node for node in node_tree.nodes if node.type == 'TEX_ENVIRONMENT'), None)

    # If not found, create one
    if not environment_texture_node:
        environment_texture_node = node_tree.nodes.new(
            type='ShaderNodeTexEnvironment')

    # Set the image to the node
    environment_texture_node.image = image

    # Check for an existing Background node
    background_node = next(
        (node for node in node_tree.nodes if node.type == 'BACKGROUND'), None)

    # If not found, create one
    if not background_node:
        background_node = node_tree.nodes.new(type='ShaderNodeBackground')

    # Connect the Environment Texture node to the Background node if not connected
    if not environment_texture_node.outputs["Color"].links:
        node_tree.links.new(
            environment_texture_node.outputs["Color"],
            background_node.inputs["Color"]
        )

    # Check for the Output node (World Output)
    world_output_node = next(
        (node for node in node_tree.nodes if node.type == 'OUTPUT_WORLD'), None)

    # If not found, create one
    if not world_output_node:
        world_output_node = node_tree.nodes.new(type='ShaderNodeOutputWorld')

    # Connect the Background node to the World Output node if not connected
    if not background_node.outputs["Background"].links:
        node_tree.links.new(
            background_node.outputs["Background"],
            world_output_node.inputs["Surface"]
        )


def customize_render_quality(show_background=False):

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


def add_camera():
    bpy.ops.object.camera_add(location=(0, 0, 1), rotation=(radians(70), radians(0), radians(0)))
    bpy.context.active_object.name = "ProductCamera"
    # bpy.context.active_object.data.dof.use_dof = True
    # bpy.context.active_object.data.dof.focus_distance = 2
    # bpy.context.active_object.data.dof.aperture_fstop = 0.8


def take_picture():
    output_folder = '//output/'
    bpy.context.scene.render.filepath = output_folder + "rendered_image.png"
    bpy.ops.render.render(write_still=True)


def run_main():
    remove_old_objects()

    # glowing_material = create_glowing_material()

    # for i in range(20):
    #     z = random.random() * 0.2 + 0.2
    #     x = random.random() - 0.5
    #     y = random.random() + 1.5

    #     create_glowing_object(glowing_material, 0.1, (x, y, z))

    # find_assets()
    add_asset()

    mats = get_materials_dictionary()

    create_plane_from_coords('z', 0, (-1, 0), (1, 3), list(mats.keys())[2], mats[list(mats.keys())[2]])
    create_plane_from_coords('y', 3, (-1, 0), (1, 2), list(mats.keys())[1], mats[list(mats.keys())[1]])
    create_plane_from_coords('x', -1, (0, 0), (3, 2), list(mats.keys())[0], mats[list(mats.keys())[0]])
    # create_floor(list(available_materials.values())[2])

    add_camera()
    # create_base_plane()
    add_world_background("//assets/background/abandoned_slipway_4k.exr")
    customize_render_quality(show_background=False)

    take_picture()


run_main()
