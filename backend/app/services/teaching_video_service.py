from pathlib import Path

from app.services.document_service import process_pdf
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.generation_service import (
    generate_grounded_content,
    generate_general_answer,
)
from app.services.embedding_service import create_embedding
from app.services.retrieval_service import cosine_similarity


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"


def generate_teaching_video_plan(
    topic: str,
    student_level: str = "",
    lesson_context: str = "",
    learning_goal: str = "",
    study_text: str = "",
) -> str:
    if not topic.strip():
        return ""

    # Case 1: Student directly provides study text
    if study_text.strip():
        context = study_text.strip()

    # Case 2: Use lesson context supplied by another learning agent
    elif lesson_context.strip():
        context = lesson_context.strip()

    # Case 3: Try uploaded PDF first
    else:
        pdf_files = sorted(UPLOAD_DIR.glob("*.pdf"))

        relevant_chunks = []

        if pdf_files:
            pdf_path = max(
                pdf_files,
                key=lambda path: path.stat().st_mtime
            )

            document = process_pdf(str(pdf_path))

            if document.chunks:
                relevant_chunks = retrieve_relevant_chunks(
                    topic,
                    document.chunks,
                    top_k=5
                )

                topic_embedding = create_embedding(topic)

                relevant_chunks = [
                    chunk
                    for chunk in relevant_chunks
                    if cosine_similarity(
                        topic_embedding,
                        create_embedding(chunk.text)
                    ) >= 0.55
                ]

        # If the topic exists in the study material,
        # use the retrieved material as the source.
        if relevant_chunks:
            context = "\n\n".join(
                chunk.text
                for chunk in relevant_chunks
            )

        # If the topic is not available in the study material,
        # use Gemini general knowledge as the fallback source.
        else:
            context = generate_general_answer(
                f"""
Provide accurate educational information about:

{topic}

This information will be used as source material for
an educational teaching video.

Explain the topic clearly for a student.
Include important definitions, concepts, examples,
and key points appropriate for the topic.

Do not mention this instruction.
Do not discuss video generation.
"""
            )

            if not context.strip():
                context = (
                    f"Provide a clear educational explanation "
                    f"of {topic} suitable for a student."
                )

    level = student_level.strip() or "Student level not specified."
    goal = learning_goal.strip() or "Understand the topic clearly."
    extra_context = (
        lesson_context.strip()
        or "No additional lesson context provided."
    )

    prompt = f"""
You are the Teaching Video Agent for Subject Guide AI.

Create a structured teaching-video script and scene plan.

Topic:
{topic}

Student Level:
{level}

Learning Goal:
{goal}

Additional Lesson Context:
{extra_context}

Study Material / Knowledge Context:
{context}

Create the teaching-video plan using this structure:

1. Video Title
- Give the video a clear educational title.

2. Learning Objective
- State what the student should understand after watching the video.

3. Video Overview
- Briefly explain how the lesson will teach the topic.

4. Scene-by-Scene Teaching Script

Create 5 to 8 scenes.

For EACH scene provide exactly:

### Scene [number]: [scene title]

**Duration:**
- Give an approximate duration in seconds.

**Teaching Purpose:**
- Explain what this scene teaches.

**Visual Direction:**
- Describe exactly what should appear on screen.
- Prefer diagrams, flowcharts, labels, highlighted concepts,
  simple animations, or educational illustrations when appropriate.

**On-Screen Text:**
- Give short text that should appear on the screen.
- Keep it concise.

**Teacher Narration:**
- Write the actual words the AI teacher should speak.
- The narration must teach the student directly.
- Explain the concept clearly and naturally.
- Do not merely describe the scene.
- Do not say things like "the video shows".
- Speak as an AI teacher teaching the student.

**Transition:**
- Explain how this scene should transition to the next scene.

5. Teaching Flow

Show the complete teaching sequence:

Introduction
→ Concept Explanation
→ Visual Explanation
→ Example
→ Key Points
→ Recap
→ Understanding Check

6. Worked Example

- Include an example when appropriate.
- Use accurate information.
- Do not invent unsupported technical claims.

7. Recap

Provide the key concepts the AI teacher should verbally recap.

8. Check Your Understanding

Create one short question based on the lesson.

Also provide:

**Teacher Prompt:**
- Write what the AI teacher should say to the student before asking
  the question.

**Expected Answer:**
- Give the expected answer clearly.

9. Video Production Specification

Include:

- Visual style
- Animation style
- Text style
- Diagram style
- Scene transitions
- Approximate total duration
- Voice narration requirement

10. Voice Narration Specification

Define:

- Narration style: friendly AI teacher
- Tone: clear, calm, student-friendly
- Speaking speed: moderate
- Language: English unless the student requests another language
- Narration must match the scene content
- Narration must teach, not simply describe visuals
- Every teaching scene must have narration

11. Source References

Explain whether the lesson was created from:
- Uploaded study material
- Student-provided study text
- Lesson context
- General Gemini knowledge fallback

IMPORTANT:

If relevant study material was available, prioritize it.

If relevant study material was not available, use accurate general
knowledge to create a useful educational lesson.

Do not claim that actual video or audio has already been generated.

Return only the teaching-video plan.

Use Markdown headings and bullets.
"""

    video_plan = generate_grounded_content(
        instruction=prompt,
        context=context
    )

    return video_plan
def extract_teacher_narration(video_plan: str) -> str:
    if not video_plan.strip():
        return ""

    lines = video_plan.splitlines()
    narration_lines = []
    capturing = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("**Teacher Narration:**"):
            capturing = True
            continue

        if capturing:
            if stripped.startswith("**Transition:**"):
                capturing = False
                continue

            if stripped.startswith("### Scene"):
                capturing = False
                continue

            if stripped:
                narration_lines.append(stripped)

    return "\n".join(
    line.lstrip("- ").strip()
    for line in narration_lines
).strip()

def create_teaching_video(
    narration_audio_path: str,
    output_filename: str = "teaching_video.mp4",
    topic: str = "Teaching Lesson",
    video_plan: str = "",
) -> str:
    import re
    import shutil
    import subprocess
    from pathlib import Path

    from PIL import Image, ImageDraw, ImageFont

    backend_dir = Path(__file__).resolve().parents[2]
    frames_dir = backend_dir / "teaching_video_frames"
    output_dir = backend_dir / "generated_videos"

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / output_filename

    try:
        print("========================================")
        print("TEACHING VIDEO ENGINE STARTED")
        print(f"TOPIC: {topic}")
        print(f"AUDIO: {narration_audio_path}")
        print("========================================")

        audio_path = Path(narration_audio_path)

        if not audio_path.exists():
            raise RuntimeError(
                f"Narration audio file not found: {audio_path}"
            )

        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")

        if not ffmpeg:
            raise RuntimeError(
                "FFmpeg was not found on PATH."
            )

        if not ffprobe:
            raise RuntimeError(
                "FFprobe was not found on PATH."
            )

        # -------------------------------------------------
        # Get narration duration
        # -------------------------------------------------

        probe_command = [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ]

        probe_result = subprocess.run(
            probe_command,
            capture_output=True,
            text=True,
        )

        if probe_result.returncode != 0:
            raise RuntimeError(
                "Could not read narration duration.\n"
                + probe_result.stderr
            )

        try:
            duration = float(probe_result.stdout.strip())
        except ValueError:
            duration = 30.0

        duration = max(duration, 8.0)

        print(f"NARRATION DURATION: {duration:.2f} seconds")

        # -------------------------------------------------
        # Extract Gemini scenes
        # -------------------------------------------------

        scenes = []

        scene_matches = re.findall(
            r"###\s*Scene\s*\d+\s*:\s*(.+)",
            video_plan,
            flags=re.IGNORECASE,
        )

        on_screen_matches = re.findall(
            r"\*\*On-Screen Text:\*\*\s*(.*?)(?=\n\s*\*\*|\n###|\Z)",
            video_plan,
            flags=re.IGNORECASE | re.DOTALL,
        )

        for index, title in enumerate(scene_matches):
            clean_title = re.sub(
                r"[*#]",
                "",
                title,
            ).strip()

            subtitle = ""

            if index < len(on_screen_matches):
                subtitle = re.sub(
                    r"\s+",
                    " ",
                    on_screen_matches[index],
                ).strip()

            if clean_title:
                scenes.append(
                    {
                        "title": clean_title[:70],
                        "subtitle": subtitle[:120],
                    }
                )

        # -------------------------------------------------
        # Fallback scenes
        # -------------------------------------------------

        if not scenes:
            scenes = [
                {
                    "title": topic,
                    "subtitle": "Introduction and key idea",
                },
                {
                    "title": f"Understanding {topic}",
                    "subtitle": "Core concept explained clearly",
                },
                {
                    "title": "Key Concepts",
                    "subtitle": "Important points to remember",
                },
                {
                    "title": "Real-World Understanding",
                    "subtitle": "How the concept applies",
                },
                {
                    "title": "Lesson Recap",
                    "subtitle": "Review the most important ideas",
                },
            ]

        # At least 5 scenes
        while len(scenes) < 5:
            scenes.append(
                {
                    "title": "Key Takeaway",
                    "subtitle": f"Remember the main ideas about {topic}",
                }
            )

        # Maximum 8 scenes
        scenes = scenes[:8]

        print(f"SCENES FOUND: {len(scenes)}")

        for i, scene_data in enumerate(scenes, start=1):
            print(
                f"Scene {i}: "
                f"{scene_data['title']} | "
                f"{scene_data['subtitle']}"
            )

        # -------------------------------------------------
        # Render settings
        # -------------------------------------------------

        width = 1280
        height = 720
        fps = 30

        scene_duration = duration / len(scenes)

        frames_dir.mkdir(parents=True, exist_ok=True)

        for old_frame in frames_dir.glob("frame_*.png"):
            try:
                old_frame.unlink()
            except OSError:
                pass

        font_paths = [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
        ]

        bold_font_paths = [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
        ]

        normal_font = None
        bold_font = None

        for path in font_paths:
            if Path(path).exists():
                normal_font = ImageFont.truetype(path, 28)
                break

        for path in bold_font_paths:
            if Path(path).exists():
                bold_font = ImageFont.truetype(path, 52)
                break

        if normal_font is None:
            normal_font = ImageFont.load_default()

        if bold_font is None:
            bold_font = ImageFont.load_default()

        small_font = (
            ImageFont.truetype(
                font_paths[0],
                22,
            )
            if Path(font_paths[0]).exists()
            else ImageFont.load_default()
        )

        # -------------------------------------------------
        # Create frames
        # -------------------------------------------------

        total_frames = int(duration * fps)

        for frame_number in range(total_frames):

            current_time = frame_number / fps

            scene_index = min(
                int(current_time / scene_duration),
                len(scenes) - 1,
            )

            scene_data = scenes[scene_index]

            local_time = (
                current_time
                - scene_index * scene_duration
            )

            progress = min(
                local_time / max(scene_duration, 0.1),
                1.0,
            )

            image = Image.new(
                "RGB",
                (width, height),
                (7, 12, 25),
            )

            draw = ImageDraw.Draw(image)

            # Background grid
            for x in range(0, width, 80):
                draw.line(
                    (x, 0, x, height),
                    fill=(14, 23, 42),
                    width=1,
                )

            for y in range(0, height, 80):
                draw.line(
                    (0, y, width, y),
                    fill=(14, 23, 42),
                    width=1,
                )

            # Header
            draw.text(
                (65, 45),
                "SUBJECT GUIDE AI",
                font=small_font,
                fill=(80, 190, 255),
            )

            draw.text(
                (65, 90),
                topic[:60],
                font=bold_font,
                fill=(240, 246, 255),
            )

            # Main card
            card_left = 100
            card_top = 210
            card_right = 1180
            card_bottom = 520

            draw.rounded_rectangle(
                (
                    card_left,
                    card_top,
                    card_right,
                    card_bottom,
                ),
                radius=28,
                fill=(18, 29, 52),
                outline=(55, 105, 170),
                width=3,
            )

            # Scene title
            title = scene_data["title"]

            title_box = draw.textbbox(
                (0, 0),
                title,
                font=bold_font,
            )

            title_width = (
                title_box[2] - title_box[0]
            )

            title_x = (
                width - title_width
            ) / 2

            draw.text(
                (title_x, 270),
                title,
                font=bold_font,
                fill=(245, 250, 255),
            )

            # Subtitle
            subtitle = scene_data["subtitle"]

            if not subtitle:
                subtitle = (
                    f"Learn the key ideas of {topic}"
                )

            subtitle = subtitle[:150]

            sub_box = draw.textbbox(
                (0, 0),
                subtitle,
                font=normal_font,
            )

            subtitle_width = (
                sub_box[2] - sub_box[0]
            )

            subtitle_x = (
                width - subtitle_width
            ) / 2

            draw.text(
                (subtitle_x, 350),
                subtitle,
                font=normal_font,
                fill=(165, 185, 215),
            )

            # Learning progress indicator
            bar_left = 300
            bar_right = 980
            bar_y = 450

            draw.rounded_rectangle(
                (
                    bar_left,
                    bar_y,
                    bar_right,
                    bar_y + 10,
                ),
                radius=5,
                fill=(35, 50, 78),
            )

            progress_width = int(
                (bar_right - bar_left) * progress
            )

            if progress_width > 0:
                draw.rounded_rectangle(
                    (
                        bar_left,
                        bar_y,
                        bar_left + progress_width,
                        bar_y + 10,
                    ),
                    radius=5,
                    fill=(55, 200, 255),
                )

            # Scene number
            scene_label = (
                f"SCENE {scene_index + 1} / {len(scenes)}"
            )

            draw.text(
                (width - 300, 90),
                scene_label,
                font=small_font,
                fill=(130, 155, 190),
            )

            # Footer
            draw.text(
                (65, 650),
                "AI TEACHER  •  2D EDUCATIONAL LESSON",
                font=small_font,
                fill=(105, 125, 155),
            )

            frame_path = (
                frames_dir
                / f"frame_{frame_number:06d}.png"
            )

            image.save(
                frame_path,
                "PNG",
            )

        print("FRAMES CREATED SUCCESSFULLY")

        # -------------------------------------------------
        # Encode video
        # -------------------------------------------------

        if output_path.exists():
            output_path.unlink()

        encode_command = [
            ffmpeg,
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frames_dir / "frame_%06d.png"),
            "-i",
            str(audio_path),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "144k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(output_path),
        ]

        print("ENCODING TEACHING VIDEO...")

        result = subprocess.run(
            encode_command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(result.stderr)
            raise RuntimeError(
                "FFmpeg video encoding failed."
            )

        if not output_path.exists():
            raise RuntimeError(
                "FFmpeg completed but the video file was not created."
            )

        print("========================================")
        print(
            f"TEACHING VIDEO CREATED: {output_path}"
        )
        print("========================================")

        return str(output_path)

    except Exception as exc:
        import traceback

        print("========================================")
        print("TEACHING VIDEO CREATION FAILED")
        print(f"ERROR: {exc}")
        traceback.print_exc()
        print("========================================")

        raise

