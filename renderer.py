import bpy

bpy.ops.mesh.primitive_cube_add()
so = bpy.context.active_object

so.rotation_euler[0] = 5

mod_subsurf = so.modifiers.new("My Modifier", "SUBSURF")
mod_subsurf.levels = 3

bpy.ops.object.shade_smooth()

mod_displace = so.modifiers.new("Displacement", "DISPLACE")
mod_displace.strength = 0.3

new_tex = bpy.data.textures.new("texture", "DISTORTED_NOISE")
new_tex.noise_scale = 0.5

mod_displace.texture = new_tex

# add material
new_material = bpy.data.materials.new(name = "My Material")
so.data.materials.append(new_material)

new_material.use_nodes = True
nodes = new_material.node_tree.nodes

material_output = nodes.get("Material Output")
node_emission = nodes.new(type='ShaderNodeEmission')

node_emission.inputs[0].default_value = (0.0, 0.3, 1.0, 1)
node_emission.inputs[1].default_value = 500.0

links = new_material.node_tree.links
new_link = links.new(node_emission.outputs[0], material_output.inputs[0])