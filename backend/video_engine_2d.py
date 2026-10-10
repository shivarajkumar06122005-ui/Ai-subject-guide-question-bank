"""
Reusable 2D Educational Video Engine
====================================

Windows requirements:
    Python 3.x
    Pillow
    FFmpeg

Run:
    python video_engine_2d.py

Output:
    binary_search_2d.mp4
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import shutil
import subprocess
from pathlib import Path
import os
import wave
from dotenv import load_dotenv
from google import genai

# ============================================================
# CONFIGURATION
# ============================================================

WIDTH = 1280
HEIGHT = 720
FPS = 30
DURATION = 10
FRAMES = FPS * DURATION

ROOT = Path(__file__).resolve().parent

FRAMES_DIR = ROOT / "video_frames_2d"
OUTPUT = ROOT / "binary_search_2d.mp4"
# ============================================================
# GEMINI AI VOICE
# ============================================================

PROJECT_ROOT = ROOT.parent
load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found in the project .env file."
    )

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)

VOICE_STYLE = """
Speak slowly and clearly like a patient university teacher.
Use a calm educational tone.
Pause naturally between sentences.
Do not rush.
Explain each concept at a comfortable learning pace.
"""

VOICE_MODEL = "gemini-2.5-flash-preview-tts"

VOICE_TEXT = """
Binary search is an efficient searching algorithm for sorted data.

First, we look at the middle element.

Our target is 42, while the middle value is 31.
Because 42 is greater than 31, we can ignore the entire left half.

Next, we compare 42 with 57.
Because 42 is smaller than 57, we keep the left part of the remaining search space.

Finally, we reach 42.

The target is found.

The key idea is simple:
binary search repeatedly eliminates half of the remaining search space.
"""

# ============================================================
# FONTS
# ============================================================

def get_font(size, bold=False):

    if bold:
        candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
        ]
    else:
        candidates = [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
        ]

    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


FONT_TITLE = get_font(52, True)
FONT_SUBTITLE = get_font(25)
FONT_CARD = get_font(34, True)
FONT_SMALL = get_font(23)
FONT_BIG = get_font(46, True)
FONT_TINY = get_font(18)


# ============================================================
# COLORS
# ============================================================

BG = (8, 12, 25)

PANEL = (16, 23, 43)
PANEL_2 = (21, 30, 55)

WHITE = (238, 245, 255)
MUTED = (151, 169, 198)

BLUE = (48, 116, 255)
CYAN = (42, 218, 255)
GREEN = (58, 225, 137)
ORANGE = (255, 151, 56)
RED = (255, 83, 102)


# ============================================================
# MATH / ANIMATION HELPERS
# ============================================================

def clamp(value, minimum=0.0, maximum=1.0):
    return max(minimum, min(maximum, value))


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


# ============================================================
# DRAWING HELPERS
# ============================================================

def rounded(draw, box, radius, fill, outline=None, width=1):

    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )


def centered(draw, xy, text, font, fill):

    box = draw.textbbox((0, 0), text, font=font)

    text_width = box[2] - box[0]
    text_height = box[3] - box[1]

    draw.text(
        (
            xy[0] - text_width / 2,
            xy[1] - text_height / 2,
        ),
        text,
        font=font,
        fill=fill,
    )


def glow_layer(base, box, color, radius=24, alpha=100):

    layer = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0),
    )

    draw = ImageDraw.Draw(layer)

    x1, y1, x2, y2 = box

    draw.rounded_rectangle(
        (
            x1 - 5,
            y1 - 5,
            x2 + 5,
            y2 + 5,
        ),
        radius=radius,
        fill=(*color, alpha),
    )

    layer = layer.filter(
        ImageFilter.GaussianBlur(18)
    )

    base.alpha_composite(layer)


# ============================================================
# BACKGROUND
# ============================================================

def draw_background(image, progress):

    draw = ImageDraw.Draw(image)

    # Grid
    for x in range(0, WIDTH, 80):

        draw.line(
            (x, 0, x, HEIGHT),
            fill=(13, 20, 38),
            width=1,
        )

    for y in range(0, HEIGHT, 80):

        draw.line(
            (0, y, WIDTH, y),
            fill=(13, 20, 38),
            width=1,
        )

    # Moving blue light
    cx = int(
        WIDTH * (
            0.15 + 0.7 * progress
        )
    )

    cy = 130

    for radius in range(240, 20, -30):

        alpha = int(
            25 * (1 - radius / 260)
        )

        draw.ellipse(
            (
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
            ),
            fill=(18, 47, 95, alpha),
        )


# ============================================================
# HEADER
# ============================================================

def draw_header(draw, title, subtitle):

    draw.text(
        (64, 48),
        title,
        font=FONT_TITLE,
        fill=WHITE,
    )

    draw.text(
        (66, 112),
        subtitle,
        font=FONT_SUBTITLE,
        fill=MUTED,
    )


# ============================================================
# ARRAY VISUALIZATION
# ============================================================

def draw_array(
    image,
    values,
    start_x,
    y,
    cell_width,
    cell_height,
    active_left,
    active_right,
    middle,
    found=False,
):

    draw = ImageDraw.Draw(image)

    gap = 12

    for index, value in enumerate(values):

        x = start_x + index * (
            cell_width + gap
        )

        y1 = y
        y2 = y + cell_height

        in_range = (
            active_left
            <= index
            <= active_right
        )

        is_middle = index == middle

        is_found = (
            found
            and is_middle
        )

        fill = PANEL_2
        outline = (55, 73, 110)

        if not in_range:

            fill = (13, 18, 32)
            outline = (28, 38, 60)

        if is_middle:

            fill = ORANGE
            outline = (255, 202, 118)

        if is_found:

            fill = GREEN
            outline = (174, 255, 213)

        box = (
            x,
            y1,
            x + cell_width,
            y2,
        )

        if is_middle or is_found:

            glow_layer(
                image,
                box,
                GREEN if is_found else ORANGE,
                radius=18,
                alpha=110,
            )

        rounded(
            draw,
            box,
            18,
            fill=fill,
            outline=outline,
            width=2,
        )

        centered(
            draw,
            (
                x + cell_width / 2,
                y1 + cell_height / 2,
            ),
            str(value),
            FONT_CARD,
            BG if (
                is_middle or is_found
            ) else WHITE,
        )

        centered(
            draw,
            (
                x + cell_width / 2,
                y2 + 34,
            ),
            str(index),
            FONT_TINY,
            MUTED,
        )


# ============================================================
# BINARY SEARCH SCENE
# ============================================================

def create_scene(frame):

    time = frame / FPS

    image = Image.new(
        "RGBA",
        (WIDTH, HEIGHT),
        (*BG, 255),
    )

    draw_background(
        image,
        frame / max(1, FRAMES - 1),
    )

    draw = ImageDraw.Draw(image)


    # ========================================================
    # SCENE 1 — INTRO
    # ========================================================

    if time < 2:

        progress = ease_out(
            time / 1.0
        )

        title_y = lerp(
            270,
            250,
            progress,
        )

        centered(
            draw,
            (WIDTH / 2, title_y),
            "BINARY SEARCH",
            FONT_TITLE,
            WHITE,
        )

        centered(
            draw,
            (WIDTH / 2, 330),
            "Find a value by repeatedly halving the search space",
            FONT_SUBTITLE,
            MUTED,
        )

        bar_x1 = 320
        bar_x2 = 960
        bar_y = 410

        draw.line(
            (
                bar_x1,
                bar_y,
                bar_x2,
                bar_y,
            ),
            fill=(41, 59, 90),
            width=8,
        )

        pulse = (
            0.5
            + 0.5
            * math.sin(
                time * math.pi * 4
            )
        )

        draw.ellipse(
            (
                600 - 12 - pulse * 4,
                bar_y - 12 - pulse * 4,
                600 + 12 + pulse * 4,
                bar_y + 12 + pulse * 4,
            ),
            fill=CYAN,
        )

        return image.convert("RGB")


    # ========================================================
    # DATA
    # ========================================================

    values = [
        10,
        18,
        25,
        31,
        42,
        57,
        81,
    ]


    # ========================================================
    # SCENE 2 — SORTED ARRAY
    # ========================================================

    if time < 4:

        draw_header(
            draw,
            "BINARY SEARCH",
            "Step 1  •  Start with a sorted array",
        )

        draw_array(
            image,
            values,
            245,
            300,
            105,
            95,
            0,
            6,
            3,
        )

        centered(
            draw,
            (WIDTH / 2, 515),
            "TARGET = 42",
            FONT_BIG,
            CYAN,
        )

        return image.convert("RGB")


    # ========================================================
    # SCENE 3 — SEARCH
    # ========================================================

    if time < 7:

        progress = ease_in_out(
            (time - 4) / 3
        )

        draw_header(
            draw,
            "BINARY SEARCH",
            "Step 2  •  Compare the middle value",
        )

        phase = int(
            clamp(progress * 2.99)
        )

        ranges = [
            (0, 6, 3),
            (4, 6, 5),
            (4, 4, 4),
        ]

        left, right, middle = ranges[
            phase
        ]

        draw_array(
            image,
            values,
            245,
            270,
            105,
            95,
            left,
            right,
            middle,
            found=(
                phase == 2
            ),
        )


        if phase == 0:

            message = (
                "42 > 31  →  search the RIGHT half"
            )

            color = ORANGE


        elif phase == 1:

            message = (
                "42 < 57  →  search the LEFT half"
            )

            color = BLUE


        else:

            message = (
                "42 = 42  →  FOUND"
            )

            color = GREEN


        rounded(
            draw,
            (
                245,
                470,
                1035,
                560,
            ),
            22,
            fill=PANEL,
            outline=color,
            width=2,
        )

        centered(
            draw,
            (WIDTH / 2, 515),
            message,
            FONT_CARD,
            WHITE,
        )


        # Search range bracket

        x1 = (
            245
            + left * 117
        )

        x2 = (
            245
            + right * 117
            + 105
        )

        draw.line(
            (
                x1,
                590,
                x2,
                590,
            ),
            fill=color,
            width=6,
        )

        draw.line(
            (
                x1,
                575,
                x1,
                605,
            ),
            fill=color,
            width=6,
        )

        draw.line(
            (
                x2,
                575,
                x2,
                605,
            ),
            fill=color,
            width=6,
        )

        return image.convert("RGB")


    # ========================================================
    # SCENE 4 — RESULT
    # ========================================================

    progress = ease_in_out(
        (time - 7) / 3
    )

    draw_header(
        draw,
        "BINARY SEARCH",
        "Step 3  •  Result",
    )

    scale = ease_out(
        min(
            1,
            progress * 1.6,
        )
    )

    box_width = 460 * scale
    box_height = 190 * scale

    center_x = WIDTH / 2
    center_y = 305

    box = (
        center_x - box_width / 2,
        center_y - box_height / 2,
        center_x + box_width / 2,
        center_y + box_height / 2,
    )

    glow_layer(
        image,
        box,
        GREEN,
        radius=30,
        alpha=100,
    )

    rounded(
        draw,
        box,
        30,
        fill=PANEL_2,
        outline=GREEN,
        width=3,
    )

    if scale > 0.65:

        centered(
            draw,
            (
                center_x,
                280,
            ),
            "42",
            FONT_TITLE,
            GREEN,
        )

        centered(
            draw,
            (
                center_x,
                345,
            ),
            "FOUND",
            FONT_CARD,
            WHITE,
        )


    # Recap

    bullets = [
        "Sorted data is required",
        "Check the middle element",
        "Eliminate half each step",
    ]

    start_y = 470

    for index, text in enumerate(
        bullets
    ):

        progress_value = clamp(
            (
                progress
                - index * 0.15
            ) / 0.45
        )

        x = lerp(
            -250,
            210,
            ease_out(
                progress_value
            ),
        )

        draw.ellipse(
            (
                x,
                start_y + index * 52,
                x + 14,
                start_y
                + index * 52
                + 14,
            ),
            fill=CYAN,
        )

        draw.text(
            (
                x + 30,
                start_y
                + index * 52
                - 8,
            ),
            text,
            font=FONT_SMALL,
            fill=WHITE,
        )


    return image.convert("RGB")

# ============================================================
# GENERATE GEMINI AI VOICE
# ============================================================

def generate_ai_voice():

    audio_output = ROOT / "binary_search_voice.wav"

    print("Generating Gemini AI voice...")

    response = gemini_client.models.generate_content(
        model=VOICE_MODEL,
        contents=VOICE_STYLE + "\n\n" + VOICE_TEXT,
        config={
            "response_modalities": ["AUDIO"],
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": "Kore"
                    }
                }
            }
        }
    )

    audio_data = response.candidates[0].content.parts[0].inline_data.data

    # Gemini returns PCM audio.
    # Save as standard 24 kHz / mono / 16-bit WAV.
    with wave.open(
        str(audio_output),
        "wb"
    ) as wav_file:

        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)
        wav_file.writeframes(audio_data)

    print(
        f"AI VOICE CREATED: {audio_output}"
    )

    return audio_output


# ============================================================
# RENDER FRAMES
# ============================================================

def render_frames():

    if FRAMES_DIR.exists():

        shutil.rmtree(
            FRAMES_DIR
        )

    FRAMES_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"Rendering {FRAMES} frames..."
    )

    for frame in range(
        FRAMES
    ):

        image = create_scene(
            frame
        )

        image.save(
            FRAMES_DIR
            / f"frame_{frame:05d}.png"
        )

        if frame % FPS == 0:

            print(
                f"  {frame / FPS:.0f}s / {DURATION}s"
            )

    print(
        "Frames complete."
    )


# ============================================================
# CREATE MP4
# ============================================================

def make_video(audio_file):

    print("Encoding final MP4 with AI voice...")

    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise RuntimeError(
            "FFmpeg was not found in PATH."
        )

    command = [
        ffmpeg,
        "-y",

        # Video frames
        "-framerate", str(FPS),
        "-i", str(FRAMES_DIR / "frame_%05d.png"),

        # Gemini AI voice
        "-i", str(audio_file),

        # Video
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",

        # Audio
        "-c:a", "aac",
        "-b:a", "192k",

        # Use both streams
        "-map", "0:v:0",
        "-map", "1:a:0",

        # Finish when the shorter stream ends
        "-shortest",

        "-movflags", "+faststart",

        str(OUTPUT),
    ]

    subprocess.run(
        command,
        check=True
    )

    print(
        f"VIDEO WITH AI VOICE CREATED: {OUTPUT}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    render_frames()

    audio_file = generate_ai_voice()

    make_video(audio_file)

    print("2D educational video with Gemini AI voice finished.")