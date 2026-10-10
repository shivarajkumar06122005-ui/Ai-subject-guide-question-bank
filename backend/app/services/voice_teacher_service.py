import os
import wave
import base64
import subprocess

from dotenv import load_dotenv
from google import genai

from pathlib import Path

from app.services.document_service import process_pdf
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.generation_service import generate_grounded_content
from app.services.embedding_service import create_embedding
from app.services.retrieval_service import cosine_similarity


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured.")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

TTS_MODEL = "gemini-2.5-flash-preview-tts"

AUDIO_DIR = Path(__file__).resolve().parents[2] / "generated_audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def generate_teacher_audio(
    transcript: str,
    filename: str = "teacher_voice.wav",
) -> str:
    if not transcript.strip():
        return ""

    output_path = AUDIO_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # PRIMARY: Gemini TTS
    # ---------------------------------------------------------
    try:
        response = gemini_client.models.generate_content(
            model=TTS_MODEL,
            contents=(
                "Read the following transcript aloud exactly as written. "
                "Do not generate, modify, summarize, or add any text.\n\n"
                "Transcript:\n"
                f"{transcript}"
            ),
            config={
                "response_modalities": ["AUDIO"],
            },
        )

        audio_part = response.candidates[0].content.parts[0].inline_data
        audio_data = audio_part.data

        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(audio_data)

        print("========================================")
        print("Gemini TTS audio generated successfully:")
        print(output_path)
        print("========================================")

        return str(output_path)

    except Exception as exc:
        print("========================================")
        print("Gemini TTS failed.")
        print(f"Reason: {exc}")
        print("Switching to Windows offline TTS fallback...")
        print("========================================")

    # ---------------------------------------------------------
    # FALLBACK: Windows built-in SAPI TTS
    # ---------------------------------------------------------
    try:
        encoded_text = base64.b64encode(
            transcript.encode("utf-8")
        ).decode("ascii")

        encoded_path = base64.b64encode(
            str(output_path).encode("utf-8")
        ).decode("ascii")

        powershell_script = f"""
Add-Type -AssemblyName System.Speech

$textBytes = [Convert]::FromBase64String("{encoded_text}")
$text = [System.Text.Encoding]::UTF8.GetString($textBytes)

$pathBytes = [Convert]::FromBase64String("{encoded_path}")
$outputPath = [System.Text.Encoding]::UTF8.GetString($pathBytes)

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

$synth.Rate = -1
$synth.Volume = 100

$synth.SetOutputToWaveFile($outputPath)
$synth.Speak($text)

$synth.SetOutputToNull()
$synth.Dispose()
"""

        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell_script,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        if not output_path.exists():
            raise RuntimeError(
                "Windows TTS completed but the WAV file was not created."
            )

        print("========================================")
        print("Windows offline TTS audio generated:")
        print(output_path)
        print("========================================")

        return str(output_path)

    except Exception as fallback_exc:
        print("========================================")
        print("Windows TTS fallback also failed.")
        print(f"Reason: {fallback_exc}")
        print("========================================")

        return ""
def generate_voice_teacher_script(
    topic: str,
    student_level: str = "",
    learning_goal: str = "",
    lesson_context: str = "",
    study_text: str = "",
) -> str:
    if not topic.strip():
        return ""

    context = ""

    # ---------------------------------------------------------
    # 1. STUDENT-PROVIDED STUDY MATERIAL
    # ---------------------------------------------------------
    if study_text.strip():
        context = study_text.strip()

    else:
        # -----------------------------------------------------
        # 2. TRY RELEVANT UPLOADED PDF MATERIAL
        # -----------------------------------------------------
        pdf_files = sorted(UPLOAD_DIR.glob("*.pdf"))

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

                if relevant_chunks:
                    topic_embedding = create_embedding(topic)

                    relevant_chunks = [
                        chunk
                        for chunk in relevant_chunks
                        if cosine_similarity(
                            topic_embedding,
                            create_embedding(chunk.text)
                        ) >= 0.55
                    ]

                    if relevant_chunks:
                        context = "\n\n".join(
                            chunk.text
                            for chunk in relevant_chunks
                        )

    level = (
        student_level.strip()
        or "Student level not specified."
    )

    goal = (
        learning_goal.strip()
        or "Understand the topic clearly."
    )

    extra_context = (
        lesson_context.strip()
        or "No additional lesson context provided."
    )

    # ---------------------------------------------------------
    # 3. GROUNDED MODE
    # ---------------------------------------------------------
    if context.strip():

        instruction = f"""
You are the Voice Teacher Agent for Subject Guide AI.

Create a voice-ready teaching script for an AI teacher.

Topic:
{topic}

Student Level:
{level}

Learning Goal:
{goal}

Additional Lesson Context:
{extra_context}

Study Material:
{context}

Create the voice teaching script using this structure:

1. Voice Introduction
- Start naturally and introduce the topic.

2. Learning Objective
- Tell the student what they will learn.

3. Teaching Explanation
- Explain the topic clearly using natural spoken language.
- Use ONLY information supported by the study material.

4. Guided Interaction
- Ask short questions that can be spoken naturally.
- Questions must be based only on the study material.

5. Explanation / Example
- Include an example only when the study material provides enough information.
- Do not invent examples, values, facts, formulas, or definitions.

6. Student Check
- Ask one short spoken question to check understanding.

7. Recap
- Give a concise spoken summary.

8. Closing
- End with a short encouraging educational statement.

VOICE STYLE:
- Natural conversational English.
- Moderate speaking pace.
- Short sentences.
- Natural pauses.
- Avoid complex formatting.

STRICT GROUNDING:
- Use ONLY information supported by the study material.
- Do not use general knowledge.
- Do not invent facts or examples.
- Return only the voice teacher script.
"""

        return generate_grounded_content(
            instruction=instruction,
            context=context
        )

    # ---------------------------------------------------------
    # 4. GENERAL KNOWLEDGE FALLBACK
    # ---------------------------------------------------------
    from app.services.generation_service import generate_general_answer

    instruction = f"""
You are the Voice Teacher Agent for Subject Guide AI.

Create a voice-ready teaching lesson using established general knowledge.

Topic:
{topic}

Student Level:
{level}

Learning Goal:
{goal}

Additional Lesson Context:
{extra_context}

Create the voice teaching script using this structure:

1. Voice Introduction
- Start naturally and introduce the topic.

2. Learning Objective
- Tell the student what they will learn.

3. Teaching Explanation
- Explain the topic clearly and accurately.
- Adapt the explanation to the student's level.
- Use simple examples where useful.

4. Guided Interaction
- Ask short questions that can be spoken naturally.

5. Explanation / Example
- Give a clear example when useful.

6. Student Check
- Ask one short spoken question.

7. Recap
- Give a concise spoken summary.

8. Closing
- End with a short encouraging educational statement.

VOICE STYLE:
- Natural conversational English.
- Moderate speaking pace.
- Short sentences suitable for text-to-speech.
- Natural pauses.
- Do not claim the information came from uploaded study material.

Return only the voice teacher script.
"""

    return generate_general_answer(instruction)
