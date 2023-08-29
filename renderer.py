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

def create_glowing_material():
    new_material = bpy.data.materials.new(name = "GlowingMaterial")

    new_material.use_nodes = True
    nodes = new_material.node_tree.nodes

    material_output = nodes.get("Material Output")
    node_emission = nodes.new(type='ShaderNodeEmission')

    node_emission.inputs[0].default_value = (0.0, 0.3, 1.0, 1)
    node_emission.inputs[1].default_value = 500.0

    links = new_material.node_tree.links
    new_link = links.new(node_emission.outputs[0], material_output.inputs[0])
    
    return new_material

def create_glowing_object(material, size = 1, location = (0, 0, 0)):
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

# add base plane
def create_base_plane():
    bpy.ops.mesh.primitive_plane_add(size=250, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    plane = bpy.context.active_object

    mat = bpy.data.materials.new(name="GlossyWhite")

    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    glossy_shader = nodes.new(type='ShaderNodeBsdfGlossy')
    glossy_shader.location = (0,0)

    glossy_shader.inputs["Color"].default_value = (1, 1, 1, 1)  # RGB + Alpha
    glossy_shader.inputs["Roughness"].default_value = 0.1  # Adjust as needed

    # Add a Material Output node and connect the Glossy shader to it
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (400,0)
    mat.node_tree.links.new(glossy_shader.outputs["BSDF"], material_output.inputs["Surface"])

    # Assign the material to the plane
    plane.data.materials.append(mat)

if __name__ == '__main__':
    remove_old_objects()
    
    glowing_material = create_glowing_material()
    
    for i in range(20):
        x = random.random() * 100 - 50
        y = random.random() * 100 - 50
        
        create_glowing_object(glowing_material, 1, (x, y, 2))
    
    create_base_plane()
