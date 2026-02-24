import bpy
import math

# 1. Clean the scene to avoid conflicts
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Create materials
mat_body = bpy.data.materials.new(name="GeoCarBody")
mat_body.use_nodes = True
mat_body.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.1, 0.1, 1)

mat_wheels = bpy.data.materials.new(name="GeoWheels")
mat_wheels.use_nodes = True
mat_wheels.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.05, 0.05, 1)

# 3. Create host object for the Geometry Nodes
bpy.ops.mesh.primitive_cube_add()
car_obj = bpy.context.active_object
car_obj.name = "ProceduralCar"

# 4. Setup Geometry Nodes Modifier & Tree
mod = car_obj.modifiers.new(name="CarBuilder", type='NODES')
node_group = bpy.data.node_groups.new("CarNodeTree", 'GeometryNodeTree')
mod.node_group = node_group

nodes = node_group.nodes
links = node_group.links

# Clear default nodes
for n in nodes: 
    nodes.remove(n)

# Output Node (Handles both Blender 3.x and 4.x+)
out_node = nodes.new('NodeGroupOutput')
if hasattr(node_group, 'interface'):
    node_group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
else:
    node_group.outputs.new('NodeSocketGeometry', "Geometry")

# --- Build Geometry ---

# Body
body = nodes.new('GeometryNodeMeshCube')
body.inputs['Size'].default_value = (4, 2, 1)
mat_node_body = nodes.new('GeometryNodeSetMaterial')
mat_node_body.inputs['Material'].default_value = mat_body
links.new(body.outputs['Mesh'], mat_node_body.inputs['Geometry'])

# Cabin
cabin = nodes.new('GeometryNodeMeshCube')
cabin.inputs['Size'].default_value = (2, 1.8, 1)
cabin_tf = nodes.new('GeometryNodeTransform')
cabin_tf.inputs['Translation'].default_value = (-0.5, 0, 1)
links.new(cabin.outputs['Mesh'], cabin_tf.inputs['Geometry'])

# Wheels Base Setup
wheel = nodes.new('GeometryNodeMeshCylinder')
wheel.inputs['Radius'].default_value = 0.6
wheel.inputs['Depth'].default_value = 0.4
mat_node_wheel = nodes.new('GeometryNodeSetMaterial')
mat_node_wheel.inputs['Material'].default_value = mat_wheels
links.new(wheel.outputs['Mesh'], mat_node_wheel.inputs['Geometry'])

# Join Node
join_node = nodes.new('GeometryNodeJoinGeometry')
links.new(mat_node_body.outputs['Geometry'], join_node.inputs['Geometry'])
links.new(cabin_tf.outputs['Geometry'], join_node.inputs['Geometry'])

# Add 4 wheels via Transform nodes
wheel_positions = [(1.2, 1.2, -0.5), (1.2, -1.2, -0.5), (-1.2, 1.2, -0.5), (-1.2, -1.2, -0.5)]
for pos in wheel_positions:
    w_tf = nodes.new('GeometryNodeTransform')
    w_tf.inputs['Translation'].default_value = pos
    w_tf.inputs['Rotation'].default_value = (math.pi/2, 0, 0)
    links.new(mat_node_wheel.outputs['Geometry'], w_tf.inputs['Geometry'])
    links.new(w_tf.outputs['Geometry'], join_node.inputs['Geometry'])

# --- Animation Transform Node ---
# This single node moves the fully assembled car
anim_tf = nodes.new('GeometryNodeTransform')
links.new(join_node.outputs['Geometry'], anim_tf.inputs['Geometry'])
links.new(anim_tf.outputs['Geometry'], out_node.inputs[0])

# 5. Keyframe the Animation Sequence
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 100

trans_input = anim_tf.inputs['Translation']

def insert_kf(frame, x, y, z):
    trans_input.default_value = (x, y, z)
    trans_input.keyframe_insert(data_path="default_value", frame=frame)

insert_kf(1, 0, 0, 0)       # Start
insert_kf(30, 5, 0, 0)      # Drive forward
insert_kf(37, 6.5, 0, 2)    # First Jump Peak
insert_kf(45, 8, 0, 0)      # First Jump Land
insert_kf(52, 9.5, 0, 2)    # Second Jump Peak
insert_kf(60, 11, 0, 0)     # Second Jump Land
insert_kf(79, 11, 0, 0)     # Hold position
insert_kf(80, 0, 0, 0)      # Snap back to start

# Loop the animation endlessly
if node_group.animation_data and node_group.animation_data.action:
    for fcurve in node_group.animation_data.action.fcurves:
        fcurve.modifiers.new(type='CYCLES')