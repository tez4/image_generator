import bpy
import random


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

    bpy.ops.object.shade_smooth()

    mod_displace = so.modifiers.new("Displacement", "DISPLACE")
    mod_displace.strength = 0.3

    new_tex = bpy.data.textures.new("texture", "DISTORTED_NOISE")
    new_tex.noise_scale = 0.5

    mod_displace.texture = new_tex

    # add material
    so.data.materials.append(material)


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


def run_main():
    remove_old_objects()

    glowing_material = create_glowing_material()

    for i in range(20):
        x = random.random() * 100 - 50
        y = random.random() * 100 - 50

        create_glowing_object(glowing_material, 1, (x, y, 2))

    create_base_plane()
    add_world_background("//assets/resting_place_4k.exr")


run_main()
