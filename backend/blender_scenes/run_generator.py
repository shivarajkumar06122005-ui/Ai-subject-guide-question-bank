import subprocess
from pathlib import Path


BLENDER_EXE = (
    r"C:\Users\SHIVARAJKUMAR\Downloads"
    r"\blender-5.2.2-windows-x64"
    r"\blender-5.2.2-windows-x64"
    r"\blender.exe"
)

FFMPEG_EXE = "ffmpeg"

SCRIPT = (
    Path(__file__).resolve().parent
    / "scene_generator.py"
)

OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "generated_videos"
    / "reusable_scene"
)

FRAME_PATTERN = OUTPUT_DIR / "frame_%04d.png"

VIDEO_OUTPUT = OUTPUT_DIR / "teaching_video.mp4"


def run_blender_generator():

    print("Starting Blender generator...")

    result = subprocess.run(
        [
            BLENDER_EXE,
            "--background",
            "--python",
            str(SCRIPT),
        ],
        capture_output=True,
        text=True,
    )

    print(result.stdout)

    if result.returncode != 0:
        raise RuntimeError(
            "Blender generation failed:\n"
            + result.stderr
        )

    print("Blender rendering complete.")


def convert_frames_to_video():

    print("Starting FFmpeg video conversion...")

    result = subprocess.run(
        [
            FFMPEG_EXE,
            "-y",
            "-framerate",
            "30",
            "-i",
            str(FRAME_PATTERN),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(VIDEO_OUTPUT),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg conversion failed:\n"
            + result.stderr
        )

    print("MP4 created:")
    print(VIDEO_OUTPUT)


if __name__ == "__main__":

    run_blender_generator()

    convert_frames_to_video()

    print("Teaching video generation finished.")