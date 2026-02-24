import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes["Principled BSDF"].inputs[0].default_value = color
    return mat

# Materials
red_mat = create_material("CarBody", (0.8, 0.1, 0.1, 1))
black_mat = create_material("Wheels", (0.05, 0.05, 0.05, 1))

# Create Body
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
body = bpy.context.active_object
body.scale = (2, 1, 0.5)
body.data.materials.append(red_mat)

# Create Cabin
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.2, 0, 1.75))
cabin = bpy.context.active_object
cabin.scale = (1, 0.8, 0.5)
cabin.data.materials.append(red_mat)

# Create Wheels
wheel_locations = [
    (1.2, 1.1, 0.5), (1.2, -1.1, 0.5), 
    (-1.2, 1.1, 0.5), (-1.2, -1.1, 0.5)
]

for loc in wheel_locations:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.3, location=loc)
    wheel = bpy.context.active_object
    wheel.rotation_euler[0] = 1.5708  # Rotate 90 degrees
    wheel.data.materials.append(black_mat)