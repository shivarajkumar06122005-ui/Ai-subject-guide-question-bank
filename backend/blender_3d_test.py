import bpy
import math
from mathutils import Vector

print("3D EDUCATIONAL SCENE STARTED")

# --------------------------------------------------
# CLEAR SCENE
# --------------------------------------------------

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# --------------------------------------------------
# MATERIAL HELPER
# --------------------------------------------------

def make_material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)

    mat.use_nodes = True

    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness

    return mat


# Materials
floor_mat = make_material(
    "Floor",
    (0.035, 0.045, 0.065),
    0.1,
    0.35
)

memory_mat = make_material(
    "Memory Blue",
    (0.03, 0.22, 0.75),
    0.25,
    0.25
)

value_mat = make_material(
    "Value Gold",
    (1.0, 0.45, 0.05),
    0.15,
    0.25
)

white_mat = make_material(
    "White",
    (0.9, 0.95, 1.0),
    0.0,
    0.3
)

arrow_mat = make_material(
    "Arrow",
    (0.1, 0.8, 1.0),
    0.25,
    0.2
)

# --------------------------------------------------
# FLOOR
# --------------------------------------------------

bpy.ops.mesh.primitive_plane_add(
    size=20,
    location=(0, 0, 0)
)

floor = bpy.context.object
floor.name = "3D_CLASSROOM_FLOOR"
floor.data.materials.append(floor_mat)

# --------------------------------------------------
# MEMORY BLOCK
# --------------------------------------------------

bpy.ops.mesh.primitive_cube_add(
    location=(1.5, 0, 2.0),
    scale=(2.2, 1.4, 1.6)
)

memory = bpy.context.object
memory.name = "MEMORY_BLOCK"
memory.data.materials.append(memory_mat)

# Rounded edges
bevel = memory.modifiers.new(
    "Rounded Edges",
    "BEVEL"
)

bevel.width = 0.18
bevel.segments = 5

# --------------------------------------------------
# VALUE BLOCK
# --------------------------------------------------

bpy.ops.mesh.primitive_cube_add(
    location=(-3.5, 0, 1.2),
    scale=(1.0, 1.0, 1.0)
)

value = bpy.context.object
value.name = "VALUE_21"
value.data.materials.append(value_mat)

bevel = value.modifiers.new(
    "Rounded Value",
    "BEVEL"
)

bevel.width = 0.15
bevel.segments = 5

# --------------------------------------------------
# TEXT HELPER
# --------------------------------------------------

def create_text(
    text,
    location,
    size,
    material,
    extrude=0.03
):
    bpy.ops.object.text_add(
        location=location,
        rotation=(math.radians(90), 0, 0)
    )

    obj = bpy.context.object
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"

    obj.data.size = size
    obj.data.extrude = extrude
    obj.data.bevel_depth = 0.01

    obj.data.materials.append(material)

    return obj


# --------------------------------------------------
# MEMORY LABEL
# --------------------------------------------------

create_text(
    "MEMORY",
    (1.5, -1.43, 2.1),
    0.75,
    white_mat,
    0.05
)

# --------------------------------------------------
# VARIABLE LABEL
# --------------------------------------------------

create_text(
    "VARIABLE",
    (1.5, -1.43, 1.25),
    0.45,
    white_mat,
    0.03
)

# --------------------------------------------------
# VALUE LABEL
# --------------------------------------------------

create_text(
    "21",
    (-3.5, -1.02, 1.15),
    0.9,
    white_mat,
    0.05
)

# --------------------------------------------------
# ARROW
# --------------------------------------------------

bpy.ops.mesh.primitive_cone_add(
    vertices=32,
    radius1=0.45,
    radius2=0,
    depth=1.0,
    location=(-1.15, 0, 1.2),
    rotation=(0, math.radians(90), 0)
)

arrow_head = bpy.context.object
arrow_head.name = "VALUE_ARROW_HEAD"
arrow_head.data.materials.append(arrow_mat)

bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=0.22,
    depth=2.0,
    location=(-2.0, 0, 1.2),
    rotation=(0, math.radians(90), 0)
)

arrow_body = bpy.context.object
arrow_body.name = "VALUE_ARROW_BODY"
arrow_body.data.materials.append(arrow_mat)

# --------------------------------------------------
# SMALL MEMORY CELLS
# --------------------------------------------------

for i in range(4):

    x = 0.0 + i * 1.0

    bpy.ops.mesh.primitive_cube_add(
        location=(x, 1.5, 0.7),
        scale=(0.35, 0.25, 0.25)
    )

    cell = bpy.context.object
    cell.name = f"MEMORY_CELL_{i}"
    cell.data.materials.append(arrow_mat)

    bevel = cell.modifiers.new(
        "Cell Bevel",
        "BEVEL"
    )

    bevel.width = 0.08
    bevel.segments = 3

# --------------------------------------------------
# CAMERA
# --------------------------------------------------

bpy.ops.object.camera_add(
    location=(10, -13, 8)
)

camera = bpy.context.object
bpy.context.scene.camera = camera

target = Vector((0, 0, 1.7))

direction = target - camera.location

camera.rotation_euler = direction.to_track_quat(
    "-Z",
    "Y"
).to_euler()

camera.data.lens = 48

# --------------------------------------------------
# KEY LIGHT
# --------------------------------------------------

bpy.ops.object.light_add(
    type="AREA",
    location=(2, -5, 10)
)

key_light = bpy.context.object
key_light.name = "KEY_LIGHT"

key_light.data.energy = 1600
key_light.data.shape = "DISK"
key_light.data.size = 6

direction = Vector((1, 0, 1)) - key_light.location

key_light.rotation_euler = direction.to_track_quat(
    "-Z",
    "Y"
).to_euler()

# --------------------------------------------------
# FILL LIGHT
# --------------------------------------------------

bpy.ops.object.light_add(
    type="AREA",
    location=(-7, -3, 5)
)

fill = bpy.context.object
fill.data.energy = 900
fill.data.size = 5

direction = Vector((0, 0, 1.5)) - fill.location

fill.rotation_euler = direction.to_track_quat(
    "-Z",
    "Y"
).to_euler()

# --------------------------------------------------
# RIM LIGHT
# --------------------------------------------------

bpy.ops.object.light_add(
    type="AREA",
    location=(6, 4, 7)
)

rim = bpy.context.object
rim.data.energy = 1200
rim.data.size = 4

direction = Vector((1, 0, 2)) - rim.location

rim.rotation_euler = direction.to_track_quat(
    "-Z",
    "Y"
).to_euler()

# --------------------------------------------------
# WORLD LIGHT
# --------------------------------------------------

world = bpy.context.scene.world

world.use_nodes = True

background = world.node_tree.nodes.get(
    "Background"
)

background.inputs["Color"].default_value = (
    0.008,
    0.012,
    0.025,
    1
)

background.inputs["Strength"].default_value = 0.25

# --------------------------------------------------
# RENDER SETTINGS
# --------------------------------------------------

scene = bpy.context.scene

scene.render.engine = "BLENDER_EEVEE"

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

scene.render.image_settings.file_format = "PNG"

scene.render.filepath = (
    "C:/Users/SHIVARAJKUMAR/Downloads/"
    "subject-guide-ai-updated/backend/"
    "generated_videos/variable_3d_scene.png"
)

# --------------------------------------------------
# ANIMATION
# --------------------------------------------------

scene.frame_start = 1
scene.frame_end = 120
scene.render.fps = 30

# Value starts outside memory
value.location = (-3.5, 0, 1.2)
value.keyframe_insert(
    data_path="location",
    frame=1
)

# Move toward memory
value.location = (-0.8, 0, 1.2)
value.keyframe_insert(
    data_path="location",
    frame=55
)

# Enter memory
value.location = (0.7, 0, 1.8)
value.keyframe_insert(
    data_path="location",
    frame=75
)

# Shrink as it enters memory
value.scale = (1, 1, 1)
value.keyframe_insert(
    data_path="scale",
    frame=55
)

value.scale = (0.15, 0.15, 0.15)
value.keyframe_insert(
    data_path="scale",
    frame=80
)

# --------------------------------------------------
# STORED VALUE "21"
# --------------------------------------------------

stored_value = create_text(
    "21",
    (1.5, -1.47, 1.95),
    0.8,
    value_mat,
    0.05
)

# Hidden at beginning
stored_value.scale = (0.01, 0.01, 0.01)
stored_value.keyframe_insert(
    data_path="scale",
    frame=1
)

stored_value.keyframe_insert(
    data_path="scale",
    frame=75
)

# Appear after value enters memory
stored_value.scale = (1, 1, 1)
stored_value.keyframe_insert(
    data_path="scale",
    frame=90
)

# --------------------------------------------------
# MEMORY HIGHLIGHT EFFECT
# --------------------------------------------------

# Create a duplicate transparent-looking highlight shell
bpy.ops.mesh.primitive_cube_add(
    location=(1.5, 0, 2.0),
    scale=(2.3, 1.5, 1.7)
)

memory_glow = bpy.context.object
memory_glow.name = "MEMORY_HIGHLIGHT"

glow_mat = make_material(
    "Memory Highlight",
    (0.05, 0.65, 1.0),
    0.1,
    0.15
)

memory_glow.data.materials.append(glow_mat)

# Make the shell slightly larger
bevel = memory_glow.modifiers.new(
    "Highlight Bevel",
    "BEVEL"
)

bevel.width = 0.2
bevel.segments = 5

# Hide at beginning
memory_glow.scale = (0.01, 0.01, 0.01)

memory_glow.keyframe_insert(
    data_path="scale",
    frame=1
)

# Grow when 21 reaches memory
memory_glow.scale = (0.01, 0.01, 0.01)

memory_glow.keyframe_insert(
    data_path="scale",
    frame=70
)

memory_glow.scale = (1, 1, 1)

memory_glow.keyframe_insert(
    data_path="scale",
    frame=82
)

# Hold highlight
memory_glow.keyframe_insert(
    data_path="scale",
    frame=120
)

# --------------------------------------------------
# TEACHING MESSAGE
# --------------------------------------------------

teaching_text = create_text(
    "A VARIABLE STORES A VALUE",
    (0.5, -2.0, 0.8),
    0.42,
    white_mat,
    0.04
)

# Start hidden
teaching_text.scale = (0.01, 0.01, 0.01)

teaching_text.keyframe_insert(
    data_path="scale",
    frame=1
)

teaching_text.keyframe_insert(
    data_path="scale",
    frame=88
)

# Appear after value is stored
teaching_text.scale = (1, 1, 1)

teaching_text.keyframe_insert(
    data_path="scale",
    frame=105
)

# Hold until end
teaching_text.keyframe_insert(
    data_path="scale",
    frame=120
)

# --------------------------------------------------
# SAFE CINEMATIC CAMERA ANIMATION
# --------------------------------------------------

# Frame 1 — wide establishing shot
camera.location = (9.5, -14, 6.5)

direction = Vector((0.0, 0.0, 1.7)) - camera.location
camera.rotation_euler = direction.to_track_quat(
    "-Z", "Y"
).to_euler()

camera.keyframe_insert(
    data_path="location",
    frame=1
)

camera.keyframe_insert(
    data_path="rotation_euler",
    frame=1
)


# Frame 60 — move closer, still centered
camera.location = (8.0, -12, 5.8)

direction = Vector((0.0, 0.0, 1.7)) - camera.location
camera.rotation_euler = direction.to_track_quat(
    "-Z", "Y"
).to_euler()

camera.keyframe_insert(
    data_path="location",
    frame=60
)

camera.keyframe_insert(
    data_path="rotation_euler",
    frame=60
)


# Frame 120 — gentle zoom toward MEMORY
camera.location = (7.0, -10.5, 5.0)

direction = Vector((0.8, 0.0, 1.8)) - camera.location
camera.rotation_euler = direction.to_track_quat(
    "-Z", "Y"
).to_euler()

camera.keyframe_insert(
    data_path="location",
    frame=120
)

camera.keyframe_insert(
    data_path="rotation_euler",
    frame=120
)

# --------------------------------------------------
# VIDEO OUTPUT
# --------------------------------------------------

scene.render.image_settings.file_format = "PNG"

scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"

scene.render.filepath = (
    "C:/Users/SHIVARAJKUMAR/Downloads/"
    "subject-guide-ai-updated/backend/"
    "generated_videos/variable_animation/frame_"
)

print("RENDERING 3D ANIMATION...")

# --------------------------------------------------
# RENDER
# --------------------------------------------------

print("RENDERING 3D VARIABLE SCENE...")

bpy.ops.render.render(
    animation=True
)

print("RENDER COMPLETE")

# --------------------------------------------------
# SAVE BLEND FILE
# --------------------------------------------------

bpy.ops.wm.save_as_mainfile(
    filepath=(
        "C:/Users/SHIVARAJKUMAR/Downloads/"
        "subject-guide-ai-updated/backend/"
        "generated_videos/variable_3d_scene.blend"
    )
)

print("BLENDER FILE SAVED")
print("3D VARIABLE SCENE COMPLETE")