import bpy
import math
import json
from pathlib import Path
from mathutils import Vector

# =========================================================
# TEACHING VIDEO TOPIC CONFIGURATION
# =========================================================

CONFIG_FILE = (
    Path(__file__).resolve().parent
    / "topic_config.json"
)

with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    TOPIC_CONFIG = json.load(file)

print("Loaded topic:", TOPIC_CONFIG["topic"])

OUTPUT_DIR = (
    "C:/Users/SHIVARAJKUMAR/Downloads/"
    "subject-guide-ai-updated/backend/"
    "generated_videos/reusable_scene/"
)


def make_material(name, color, metallic=0.0, roughness=0.4):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True

    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness

    return material


def create_text(text, location, size, material,
                rotation=(math.radians(90), 0, 0)):

    bpy.ops.object.text_add(
        location=location,
        rotation=rotation
    )

    obj = bpy.context.object
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.04
    obj.data.bevel_depth = 0.01
    obj.data.materials.append(material)

    return obj


def create_cube(name, location, scale, material):

    bpy.ops.mesh.primitive_cube_add(
        location=location,
        scale=scale
    )

    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)

    bevel = obj.modifiers.new(
        "Rounded Edges",
        "BEVEL"
    )

    bevel.width = 0.15
    bevel.segments = 5

    return obj


def point_camera(camera, target):

    direction = Vector(target) - camera.location

    camera.rotation_euler = (
        direction
        .to_track_quat("-Z", "Y")
        .to_euler()
    )


def create_camera():

    bpy.ops.object.camera_add(
        location=(9.5, -14, 6.5)
    )

    camera = bpy.context.object
    camera.data.lens = 48

    point_camera(
        camera,
        (0, 0, 1.7)
    )

    bpy.context.scene.camera = camera

    return camera


def create_lights():

    bpy.ops.object.light_add(
        type="AREA",
        location=(2, -5, 10)
    )

    key = bpy.context.object
    key.data.energy = 1600
    key.data.shape = "DISK"
    key.data.size = 6

    point_camera(key, (1, 0, 1))

    bpy.ops.object.light_add(
        type="AREA",
        location=(-7, -3, 5)
    )

    fill = bpy.context.object
    fill.data.energy = 900
    fill.data.size = 5

    point_camera(fill, (0, 0, 1.5))

    bpy.ops.object.light_add(
        type="AREA",
        location=(6, 4, 7)
    )

    rim = bpy.context.object
    rim.data.energy = 1200
    rim.data.size = 4

    point_camera(rim, (1, 0, 2))


def setup_world():

    world = bpy.context.scene.world

    world.use_nodes = True

    background = (
        world.node_tree.nodes.get("Background")
    )

    background.inputs["Color"].default_value = (
        0.008,
        0.012,
        0.025,
        1
    )

    background.inputs["Strength"].default_value = 0.25


# =========================================================
# SCENE 1 — INTRODUCTION
# Frames 1–60
# =========================================================

def create_scene_1():

    print("Creating Scene 1 — Introduction")

    white = make_material(
        "Scene1 White",
        (0.9, 0.95, 1.0)
    )

    blue = make_material(
        "Scene1 Blue",
        (0.03, 0.22, 0.75),
        0.25,
        0.25
    )

    floor = make_material(
        "Scene1 Floor",
        (0.035, 0.045, 0.065),
        0.1,
        0.35
    )

    # -----------------------------------------------------
    # SCENE 1 FLOOR
    # -----------------------------------------------------

    bpy.ops.mesh.primitive_plane_add(
        size=20,
        location=(0, 0, 0)
    )

    scene1_floor = bpy.context.object
    scene1_floor.name = "SCENE1_FLOOR"
    scene1_floor.data.materials.append(floor)

    # -----------------------------------------------------
    # INTRODUCTION TITLE
    # -----------------------------------------------------

    title = create_text(
        TOPIC_CONFIG["title"],
        (0, -2.5, 4.8),
        0.7,
        white
    )

    title.name = "SCENE1_TITLE"

    title.scale = (0.01, 0.01, 0.01)

    title.keyframe_insert(
        data_path="scale",
        frame=1
    )

    title.scale = (1, 1, 1)

    title.keyframe_insert(
        data_path="scale",
        frame=20
    )

    # -----------------------------------------------------
    # MEMORY CUBE
    # -----------------------------------------------------

    memory = create_cube(
        "SCENE1_MEMORY",
        (0, 0, 1.2),
        (2.2, 1.4, 1.2),
        blue
    )

    # -----------------------------------------------------
    # MEMORY LABEL
    # -----------------------------------------------------

    memory_label = create_text(
        TOPIC_CONFIG["memory_label"],
        (0, -1.43, 1.3),
        0.6,
        white
    )

    memory_label.name = "SCENE1_MEMORY_LABEL"

        # HARD SCENE 1 CUT

    scene1_objects = [
        scene1_floor,
        title,
        memory,
        memory_label
    ]

    for obj in scene1_objects:

        obj.hide_render = False
        obj.keyframe_insert(
            data_path="hide_render",
            frame=1
        )

        obj.hide_render = False
        obj.keyframe_insert(
            data_path="hide_render",
            frame=59
        )

        obj.hide_render = True
        obj.keyframe_insert(
            data_path="hide_render",
            frame=60
        )

        obj.hide_render = True
        obj.keyframe_insert(
            data_path="hide_render",
            frame=120
        )
# =========================================================
# SCENE 2 — VARIABLE CONCEPT
# Frames 61–120
# =========================================================

def create_scene_2():

    print("Creating Scene 2 — Cinematic Variable Concept")

    # -----------------------------------------------------
    # FORCE SCENE 1 TO DISAPPEAR BEFORE SCENE 2
    # -----------------------------------------------------

    scene1_names = [
        "SCENE1_FLOOR",
        "SCENE1_TITLE",
        "SCENE1_MEMORY",
        "SCENE1_MEMORY_LABEL",
    ]

    for name in scene1_names:

        obj = bpy.data.objects.get(name)

        if obj:

            obj.hide_render = False
            obj.keyframe_insert(
                data_path="hide_render",
                frame=59
            )

            obj.hide_render = True
            obj.keyframe_insert(
                data_path="hide_render",
                frame=60
            )

            obj.hide_render = True
            obj.keyframe_insert(
                data_path="hide_render",
                frame=61
            )

    white = make_material(
        "Scene2 White",
        (0.92, 0.96, 1.0),
        0.0,
        0.25
    )

    blue = make_material(
        "Scene2 Memory Blue",
        (0.025, 0.12, 0.55),
        0.35,
        0.18
    )

    blue_inner = make_material(
        "Scene2 Memory Inner",
        (0.04, 0.25, 0.85),
        0.25,
        0.2
    )

    gold = make_material(
        "Scene2 Value Gold",
        (1.0, 0.32, 0.02),
        0.3,
        0.18
    )

    cyan = make_material(
        "Scene2 Energy Cyan",
        (0.02, 0.75, 1.0),
        0.4,
        0.15
    )

    dark = make_material(
        "Scene2 Cell Dark",
        (0.008, 0.015, 0.04),
        0.1,
        0.3
    )

    # -----------------------------------------------------
    # MEMORY CONTAINER
    # -----------------------------------------------------

    memory = create_cube(
        "SCENE2_MEMORY",
        (1.8, 0, 2.1),
        (2.6, 1.7, 1.8),
        blue
    )

    # Inner memory panel
    inner = create_cube(
        "MEMORY_INNER",
        (1.8, -1.74, 2.1),
        (2.25, 0.05, 1.35),
        blue_inner
    )

    # -----------------------------------------------------
    # MEMORY CELLS
    # -----------------------------------------------------

    cell_positions = [
        (0.45, -1.84, 2.9),
        (1.35, -1.84, 2.9),
        (2.25, -1.84, 2.9),
        (3.15, -1.84, 2.9),

        (0.45, -1.84, 2.1),
        (1.35, -1.84, 2.1),
        (2.25, -1.84, 2.1),
        (3.15, -1.84, 2.1),

        (0.45, -1.84, 1.3),
        (1.35, -1.84, 1.3),
        (2.25, -1.84, 1.3),
        (3.15, -1.84, 1.3),
    ]

    for index, position in enumerate(cell_positions):

        cell = create_cube(
            f"MEMORY_CELL_{index}",
            position,
            (0.32, 0.08, 0.25),
            dark
        )

        cell.scale = (0.01, 0.01, 0.01)

        cell.keyframe_insert(
            data_path="scale",
            frame=61
        )

        cell.scale = (1, 1, 1)

        cell.keyframe_insert(
            data_path="scale",
            frame=72
        )

    # -----------------------------------------------------
    # MEMORY LABEL
    # -----------------------------------------------------

    memory_label = create_text(
        TOPIC_CONFIG["memory_label"],
        (1.8, -1.95, 4.35),
        0.7,
        white
    )

    variable_label = create_text(
        TOPIC_CONFIG["variable_label"],
        (1.8, -1.95, 0.55),
        0.48,
        white
    )

    # -----------------------------------------------------
    # VALUE CUBE
    # -----------------------------------------------------

    value = create_cube(
        "VALUE_21",
        (-4.5, 0, 1.7),
        (0.95, 0.95, 0.95),
        gold
    )

    value_text = create_text(
        TOPIC_CONFIG["value"],
        (-4.5, -1.0, 1.65),
        0.85,
        white
    )

    # -----------------------------------------------------
    # VALUE GLOW / SECONDARY CUBE
    # -----------------------------------------------------

    glow = create_cube(
        "VALUE_GLOW",
        (-4.5, 0, 1.7),
        (1.15, 1.15, 1.15),
        cyan
    )

    glow.scale = (0.01, 0.01, 0.01)

    glow.keyframe_insert(
        data_path="scale",
        frame=61
    )

    glow.scale = (1, 1, 1)

    glow.keyframe_insert(
        data_path="scale",
        frame=78
    )

    # -----------------------------------------------------
    # ANIMATED ENERGY LINE
    # -----------------------------------------------------

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=0.12,
        depth=2.5,
        location=(-2.5, 0, 1.7),
        rotation=(0, math.radians(90), 0)
    )

    energy = bpy.context.object
    energy.name = "ENERGY_CONNECTION"
    energy.data.materials.append(cyan)

    energy.scale = (0.01, 0.01, 0.01)

    energy.keyframe_insert(
        data_path="scale",
        frame=61
    )

    energy.scale = (1, 1, 1)

    energy.keyframe_insert(
        data_path="scale",
        frame=85
    )

    # -----------------------------------------------------
    # VALUE MOVEMENT
    # -----------------------------------------------------

    value.location = (-4.5, 0, 1.7)

    value.keyframe_insert(
        data_path="location",
        frame=61
    )

    value.location = (-1.8, 0, 1.7)

    value.keyframe_insert(
        data_path="location",
        frame=88
    )

    value.location = (1.8, -1.0, 2.1)

    value.keyframe_insert(
        data_path="location",
        frame=105
    )

    # -----------------------------------------------------
    # VALUE LABEL MOVEMENT
    # -----------------------------------------------------

    value_text.location = (-4.5, -1.0, 1.65)

    value_text.keyframe_insert(
        data_path="location",
        frame=61
    )

    value_text.location = (-1.8, -1.0, 1.65)

    value_text.keyframe_insert(
        data_path="location",
        frame=88
    )

    value_text.location = (1.8, -2.0, 2.1)

    value_text.keyframe_insert(
        data_path="location",
        frame=105
    )

    # -----------------------------------------------------
    # TEACHING MESSAGE
    # -----------------------------------------------------

    teaching = create_text(
        TOPIC_CONFIG["teaching_message"],
        (0.5, -3.2, 0.15),
        0.34,
        white
    )

    teaching.scale = (0.01, 0.01, 0.01)

    teaching.keyframe_insert(
        data_path="scale",
        frame=61
    )

    teaching.keyframe_insert(
        data_path="scale",
        frame=92
    )

    teaching.scale = (1, 1, 1)

    teaching.keyframe_insert(
        data_path="scale",
        frame=105
    )

    # -----------------------------------------------------
    # CINEMATIC CAMERA MOVEMENT
    # -----------------------------------------------------

    camera = bpy.context.scene.camera

    camera.location = (10.5, -15.5, 7.0)

    point_camera(
        camera,
        (0, 0, 1.8)
    )

    camera.keyframe_insert(
        data_path="location",
        frame=61
    )

    camera.keyframe_insert(
        data_path="rotation_euler",
        frame=61
    )

    camera.location = (8.0, -12.0, 5.8)

    point_camera(
        camera,
        (0.5, 0, 2.0)
    )

    camera.keyframe_insert(
        data_path="location",
        frame=90
    )

    camera.keyframe_insert(
        data_path="rotation_euler",
        frame=90
    )

    camera.location = (6.5, -10.0, 5.0)

    point_camera(
        camera,
        (1.2, -0.3, 2.0)
    )

    camera.keyframe_insert(
        data_path="location",
        frame=120
    )

    camera.keyframe_insert(
        data_path="rotation_euler",
        frame=120
    )

# =========================================================
# RENDER SETTINGS
# =========================================================

def setup_render():

    scene = bpy.context.scene

    scene.render.engine = "BLENDER_EEVEE"

    # FAST MODE
    scene.render.resolution_x = 640
    scene.render.resolution_y = 360
    scene.render.resolution_percentage = 100

    scene.render.fps = 15

    scene.frame_start = 1
    scene.frame_end = 75

    scene.render.image_settings.file_format = "PNG"

    # Reduce render workload
    scene.render.image_settings.color_mode = "RGB"

    print("FAST RENDER MODE: 640x360 | 15 FPS | 75 frames")


# =========================================================
# MAIN
# =========================================================

print("SUBJECT GUIDE AI 3D GENERATOR STARTED")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

setup_world()
setup_render()

camera = create_camera()
create_lights()

create_scene_1()
create_scene_2()

bpy.context.scene.frame_set(1)

bpy.context.scene.render.filepath = (
    OUTPUT_DIR + "frame_"
)

print("RENDERING REUSABLE SCENE...")

bpy.ops.render.render(
    animation=True
)

print("REUSABLE SCENE COMPLETE")