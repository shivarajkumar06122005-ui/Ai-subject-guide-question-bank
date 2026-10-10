import re

from app.services.generation_service import generate_grounded_content


PEER_ROLES = (
    "explainer",
    "skeptic",
    "exam_peer",
)


def is_topic_relevant(current_topic: str, previous_topic: str) -> bool:
    """
    Check if the previous learning topic is relevant to the current classroom topic.
    Matches case-insensitively via exact match, containment, or key term overlap.
    """
    curr = current_topic.strip().lower()
    prev = previous_topic.strip().lower()
    if not curr or not prev:
        return False
    if curr == prev or curr in prev or prev in curr:
        return True

    stop_words = {
        "the", "and", "for", "with", "from", "into", "about",
        "what", "how", "this", "that", "all", "are", "can",
    }
    curr_tokens = {
        w.rstrip("s")
        for w in re.findall(r"\b[a-z0-9_]{3,}\b", curr)
        if w not in stop_words
    }
    prev_tokens = {
        w.rstrip("s")
        for w in re.findall(r"\b[a-z0-9_]{3,}\b", prev)
        if w not in stop_words
    }
    if bool(curr_tokens & prev_tokens):
        return True

    for c in curr_tokens:
        for p in prev_tokens:
            if len(c) >= 3 and len(p) >= 3 and (c.startswith(p) or p.startswith(c)):
                return True

    return False


def build_synthetic_peer_instruction(
    topic: str,
    student_prompt: str,
    prior_learning_memory: dict | None = None,
) -> str:
    """
    Build the grounded prompt instruction for synthetic peer generation,
    incorporating prior learning memory and personalizing peer challenges.
    """
    prior_session = (
        prior_learning_memory.get("last_session", {})
        if isinstance(prior_learning_memory, dict)
        else {}
    )
    if not isinstance(prior_session, dict):
        prior_session = {}

    prev_topic = str(prior_session.get("topic", "")).strip()
    prev_misconception = str(prior_session.get("misconception", "")).strip()
    prev_final_understanding = str(prior_session.get("final_understanding", "")).strip()
    prev_next_question = str(prior_session.get("next_thinking_question", "")).strip()

    memory_fields = (
        ("topic", "Previous topic"),
        ("misconception", "Previous misconception signal"),
        ("calibration", "Previous confidence calibration"),
        ("debate_result", "Previous debate result"),
        ("final_understanding", "Previous final understanding"),
        ("next_thinking_question", "Previous thinking question"),
    )

    prior_memory_summary = "\n".join(
        f"{label}: {str(prior_session[key])[:350]}"
        for key, label in memory_fields
        if prior_session.get(key) not in (None, "")
    )
    if not prior_memory_summary:
        prior_memory_summary = "No previous learning memory is available."

    topic_matches = is_topic_relevant(topic, prev_topic) if prev_topic else False

    if topic_matches:
        personalization_guidance = f"""PERSONALIZATION GUIDANCE (RELEVANT PREVIOUS TOPIC DETECTED):
- Relevant previous topic matched: "{prev_topic}".
- Historical Learner Signals:
  * Previous Misconception: {prev_misconception or "Not recorded"}
  * Previous Final Understanding: {prev_final_understanding or "Not recorded"}
  * Previous Thinking Question: {prev_next_question or "Not recorded"}
- SKEPTIC PEER CHALLENGE DIRECTIVE:
  * Personalize by proactively challenging the student on their previous misconception ("{prev_misconception or 'None'}") or following up on the unresolved thinking question ("{prev_next_question or 'None'}").
  * All challenges and questions must be strictly grounded in the supplied study material. Do NOT introduce external facts.
- EXPLAINER PEER DIRECTIVE:
  * Clarify and reinforce the core concept, addressing the student's previous misconception or final understanding using only the current study material.
- STRICT GROUNDING: All explanations, challenges, and exam points must remain strictly supported by the current study material."""
    elif prev_topic:
        personalization_guidance = f"""PERSONALIZATION GUIDANCE (DIFFERENT TOPIC):
- Topic Shift Detected: The current topic "{topic}" differs from previous topic "{prev_topic}".
- Context Treatment: Treat the previous learning memory strictly as background learner context.
- STRICT PROHIBITION: Do NOT assume or transfer facts, examples, or rules from "{prev_topic}" into "{topic}".
- STRICT GROUNDING: All peer explanations, challenges, and exam points must be derived EXCLUSIVELY from the current study material."""
    else:
        personalization_guidance = """PERSONALIZATION GUIDANCE (NO PREVIOUS MEMORY):
- No previous learning memory is available.
- Provide a standard, well-rounded peer discussion grounded strictly in the current study material."""

    return f"""You are the Synthetic Peer Classroom Agent for Subject Guide AI.

Create exactly three synthetic student peers discussing the same topic.

Topic:
{topic}

Student Prompt:
{student_prompt or "No specific student prompt was provided."}

Prior Learning Memory (historical learner context, not factual evidence):
{prior_memory_summary}

{personalization_guidance}

Return exactly these three peer sections:

PEER 1 - EXPLAINER PEER
- Explain the topic in simple student-friendly language.
- Use only the supplied study material.
- Give one concise example only when the material supports it.

PEER 2 - SKEPTIC PEER
- Challenge the explanation or reasoning.
- If relevant previous memory was detected above, probe the specific historical misconception or unresolved question, grounded strictly in the supplied study material.
- If no matching memory was detected, identify one possible confusion, missing justification, or weak point supported by the supplied study material.
- Do not invent an error that is not supported by the material.

PEER 3 - EXAM PEER
- Identify the most important exam-relevant points from the material.
- State what a good student answer should include.
- Do not invent marks, facts, or concepts.

Rules:
- Use ONLY the supplied study material.
- Do not use general knowledge.
- Do not invent facts, examples, formulas, or claims.
- Keep each peer response concise.
- Clearly label all three peers.
"""


def generate_synthetic_peers(
    topic: str,
    student_prompt: str,
    study_context: str,
    prior_learning_memory: dict | None = None,
) -> dict:
    """
    F3.1: Synthetic Peer Roles.

    Creates three complementary synthetic classmates:
    - Explainer Peer: explains the concept simply.
    - Skeptic Peer: challenges unsupported or unclear reasoning.
    - Exam Peer: focuses on exam relevance and answer quality.

    All peer responses are grounded in the supplied study material.
    """

    if not topic.strip():
        return {
            "status": "failed",
            "reason": "empty_topic",
            "topic": topic,
            "peers": [],
        }

    if not study_context.strip():
        return {
            "status": "failed",
            "reason": "missing_study_context",
            "topic": topic,
            "peers": [],
        }

    instruction = build_synthetic_peer_instruction(
        topic=topic,
        student_prompt=student_prompt,
        prior_learning_memory=prior_learning_memory,
    )

    combined = generate_grounded_content(
        instruction=instruction,
        context=study_context,
    )

    if not combined.strip():
        return {
            "status": "failed",
            "reason": "empty_generation",
            "topic": topic,
            "peers": [],
        }

    return {
        "status": "generated",
        "topic": topic,
        "student_prompt": student_prompt,
        "peer_roles": list(PEER_ROLES),
        "classroom_discussion": combined,
    }
def continue_synthetic_peer_discussion(
    topic: str,
    student_response: str,
    study_context: str,
    initial_discussion: str,
) -> dict:
    """
    F3.2: Peer-to-peer follow-up discussion.

    Takes the student's response after the initial classroom discussion
    and asks the three synthetic peers to react, challenge, and synthesize.
    """

    if not topic.strip():
        return {
            "status": "failed",
            "reason": "empty_topic",
            "topic": topic,
            "student_response": student_response,
        }

    if not study_context.strip():
        return {
            "status": "failed",
            "reason": "missing_study_context",
            "topic": topic,
            "student_response": student_response,
        }

    if not student_response.strip():
        return {
            "status": "failed",
            "reason": "empty_student_response",
            "topic": topic,
            "student_response": student_response,
        }

    instruction = f"""
You are continuing a Synthetic Peer Classroom session for Subject Guide AI.

Topic:
{topic}

Original Study Material:
{study_context}

Initial Peer Discussion:
{initial_discussion or "No initial peer discussion was provided."}

Student's New Response:
{student_response}

Now create the next classroom turn.

Return exactly these four sections:

PEER 1 - EXPLAINER FOLLOW-UP
- Respond directly to the student's answer.
- Identify what the student understood correctly.
- Clarify one point if the student's explanation is incomplete.
- Stay grounded in the study material.

PEER 2 - SKEPTIC FOLLOW-UP
- Challenge the student's reasoning constructively.
- Identify one assumption, gap, ambiguity, or possible misconception.
- Ask one focused question that makes the student think further.
- Do not invent an error that is unsupported by the study material.

PEER 3 - EXAM FOLLOW-UP
- Evaluate whether the student's response would be strong in an exam.
- Identify one important point that should be added, corrected, or emphasized.
- Do not invent marks or unsupported facts.

PEER SYNTHESIS
- Combine the useful points from the three peers.
- State the strongest corrected understanding of the topic.
- End with one concise question for the student to answer next.

Rules:
- Use ONLY the supplied study material.
- Do not use outside knowledge.
- Do not invent facts, formulas, examples, or claims.
- Respect the student's actual response.
- Keep the discussion concise but meaningful.
"""

    combined = generate_grounded_content(
        instruction=instruction,
        context=study_context,
    )

    if not combined.strip():
        return {
            "status": "failed",
            "reason": "empty_generation",
            "topic": topic,
            "student_response": student_response,
        }

    return {
        "status": "generated",
        "topic": topic,
        "student_response": student_response,
        "peer_roles": list(PEER_ROLES),
        "followup_discussion": combined,
    }
def detect_peer_misconception(
    topic: str,
    student_response: str,
    study_context: str,
) -> dict:
    """
    F3.3: Grounded misconception detection.

    Checks the student's response against the supplied study material and
    identifies a supported misconception, missing idea, or aligned
    understanding.
    """

    if not topic.strip():
        return {
            "status": "failed",
            "reason": "empty_topic",
            "topic": topic,
            "student_response": student_response,
        }

    if not study_context.strip():
        return {
            "status": "failed",
            "reason": "missing_study_context",
            "topic": topic,
            "student_response": student_response,
        }

    if not student_response.strip():
        return {
            "status": "failed",
            "reason": "empty_student_response",
            "topic": topic,
            "student_response": student_response,
        }

    instruction = f"""
You are the Misconception Detection Agent inside Subject Guide AI's
Synthetic Peer Classroom.

Topic:
{topic}

Study Material:
{study_context}

Student Response:
{student_response}

Analyze the student's response strictly against the supplied study material.

Return exactly these sections:

MISCONCEPTION STATUS
- Write exactly one of:
  ALIGNED
  MISCONCEPTION DETECTED
  INSUFFICIENT EVIDENCE

MISCONCEPTION / UNDERSTANDING
- Explain what the student got right or what is incorrect.
- If a misconception exists, describe only the misconception supported by
  the study material.
- Do not invent an error.

EVIDENCE FROM STUDY MATERIAL
- Quote or closely identify the specific idea from the supplied material
  that supports the judgment.
- Do not use outside knowledge.

PEER CORRECTION
- Give one concise correction or clarification grounded in the material.
- If the response is aligned, reinforce the correct understanding instead.

NEXT THINKING QUESTION
- Ask one focused question that helps the student reconsider, verify, or
  deepen the idea.

Rules:
- Use ONLY the supplied study material.
- Never use outside knowledge.
- Do not invent facts, formulas, examples, or claims.
- Distinguish between a real misconception and information that is simply
  missing from the short study material.
- Keep the analysis concise and student-friendly.
"""

    analysis = generate_grounded_content(
        instruction=instruction,
        context=study_context,
    )

    if not analysis.strip():
        return {
            "status": "failed",
            "reason": "empty_generation",
            "topic": topic,
            "student_response": student_response,
        }

    return {
        "status": "generated",
        "topic": topic,
        "student_response": student_response,
        "misconception_analysis": analysis,
    }
def analyze_peer_confidence(
    topic: str,
    student_response: str,
    confidence_score: int,
    misconception_analysis: str,
) -> dict:
    """
    F3.4: Confidence and agreement tracking.

    Compares the student's self-reported confidence with the grounded
    misconception signal produced by F3.3.
    """

    if not topic.strip():
        return {
            "status": "failed",
            "reason": "empty_topic",
            "topic": topic,
        }

    if not student_response.strip():
        return {
            "status": "failed",
            "reason": "empty_student_response",
            "topic": topic,
        }

    if confidence_score < 0 or confidence_score > 100:
        return {
            "status": "failed",
            "reason": "invalid_confidence_score",
            "topic": topic,
            "confidence_score": confidence_score,
        }

    analysis_text = misconception_analysis.upper()

    if "MISCONCEPTION DETECTED" in analysis_text:
        understanding_status = "MISCONCEPTION DETECTED"
    elif "ALIGNED" in analysis_text:
        understanding_status = "ALIGNED"
    else:
        understanding_status = "INSUFFICIENT EVIDENCE"

    if understanding_status == "MISCONCEPTION DETECTED":
        if confidence_score >= 70:
            calibration = "OVERCONFIDENT"
            interpretation = (
                "Confidence is high while the grounded analysis "
                "shows a misconception."
            )
        elif confidence_score < 50:
            calibration = "APPROPRIATELY CAUTIOUS"
            interpretation = (
                "Confidence is low and the grounded analysis "
                "also shows a misconception."
            )
        else:
            calibration = "PARTIALLY CALIBRATED"
            interpretation = (
                "Confidence and the detected misconception show "
                "a moderate calibration gap."
            )

    elif understanding_status == "ALIGNED":
        if confidence_score >= 70:
            calibration = "WELL CALIBRATED"
            interpretation = (
                "Confidence is high and the grounded analysis "
                "supports the student's understanding."
            )
        elif confidence_score < 50:
            calibration = "UNDERCONFIDENT"
            interpretation = (
                "The grounded analysis supports the response, "
                "but self-confidence is low."
            )
        else:
            calibration = "PARTIALLY CALIBRATED"
            interpretation = (
                "Understanding is aligned, but confidence is moderate."
            )

    else:
        calibration = "INSUFFICIENT EVIDENCE"
        interpretation = (
            "The supplied evidence is not sufficient to classify "
            "the student's confidence accurately."
        )

    return {
        "status": "generated",
        "topic": topic,
        "student_response": student_response,
        "confidence_score": confidence_score,
        "understanding_status": understanding_status,
        "calibration": calibration,
        "interpretation": interpretation,
    }


def analyze_peer_agreement(
    topic: str,
    peer_discussion: str,
    study_context: str,
) -> dict:
    """
    F3.5: Peer Agreement and Consensus Analysis.

    Compares the synthetic peer viewpoints and identifies:
    - shared agreement
    - differences in viewpoint
    - overall consensus
    - final learning signal

    Analysis remains grounded in the supplied study material.
    """

    if not topic.strip():
        return {
            "status": "failed",
            "reason": "empty_topic",
            "topic": topic,
            "peer_agreement": "",
        }

    if not study_context.strip():
        return {
            "status": "failed",
            "reason": "missing_study_context",
            "topic": topic,
            "peer_agreement": "",
        }

    if not peer_discussion.strip():
        return {
            "status": "failed",
            "reason": "missing_peer_discussion",
            "topic": topic,
            "peer_agreement": "",
        }

    instruction = f"""
You are the Peer Agreement and Consensus Agent inside Subject Guide AI.

Your task is to compare the three synthetic peer viewpoints from a
Synthetic Peer Classroom session.

Topic:
{topic}

Study Material:
{study_context}

Peer Discussion:
{peer_discussion}

Use ONLY the supplied study material and peer discussion.
Do not introduce outside facts.
Do not invent claims that are unsupported by the study material.

Return exactly these sections:

PEER AGREEMENT
- Identify the main point all or most peers agree on.
- State the agreement clearly and concisely.

VIEWPOINT DIFFERENCES
- Identify meaningful differences in emphasis, challenge, or interpretation
  between the Explainer, Skeptic, and Exam peers.
- Do not invent disagreement where none exists.

CONSENSUS LEVEL
- Write exactly one:
  STRONG CONSENSUS
  PARTIAL CONSENSUS
  CONFLICTING VIEWS

CONSENSUS EXPLANATION
- Explain why that consensus level was selected using the supplied material.

FINAL LEARNING SIGNAL
- State the strongest understanding the student should retain.
- Keep it concise and grounded in the study material.

Keep the analysis student-friendly.
"""

    combined = generate_grounded_content(
        instruction=instruction,
        context=f"Topic:\n{topic}\n\nStudy Material:\n{study_context}\n\nPeer Discussion:\n{peer_discussion}",
    )

    if not combined.strip():
        return {
            "status": "failed",
            "reason": "empty_generation",
            "topic": topic,
            "peer_agreement": "",
        }

    return {
        "status": "generated",
        "topic": topic,
        "peer_agreement": combined,
    }


def run_peer_debate(
    topic: str,
    revised_claim: str,
    study_context: str,
    peer_discussion: str = "",
) -> dict:
    """
    F3.6: Peer Debate and Counterargument Round.

    Lets the student submit a revised claim after peer feedback.
    The three synthetic peers independently challenge, clarify,
    or evaluate that claim using only the supplied study material.
    """

    if not topic.strip():
        return {
            "status": "failed",
            "reason": "empty_topic",
            "topic": topic,
            "debate_result": "",
        }

    if not revised_claim.strip():
        return {
            "status": "failed",
            "reason": "missing_revised_claim",
            "topic": topic,
            "debate_result": "",
        }

    if not study_context.strip():
        return {
            "status": "failed",
            "reason": "missing_study_context",
            "topic": topic,
            "debate_result": "",
        }

    instruction = f"""
You are the Peer Debate Agent inside Subject Guide AI's
Synthetic Peer Classroom.

Topic:
{topic}

Study Material:
{study_context}

Earlier Peer Discussion:
{peer_discussion or "No earlier peer discussion was provided."}

Student's Revised Claim:
{revised_claim}

Use ONLY the supplied study material.
Do not introduce outside facts.
Do not invent examples, formulas, claims, or corrections unsupported by
the supplied material.

Return exactly these sections:

PEER 1 - EXPLAINER DEBATE
- State whether the revised claim is supported by the study material.
- Clarify the claim using the material.
- Mention one important point the student should retain.

PEER 2 - SKEPTIC COUNTERARGUMENT
- Challenge the revised claim constructively.
- Identify one supported weakness, ambiguity, contradiction, or missing idea.
- Do not invent a problem if the claim is fully supported.

PEER 3 - EXAM EVALUATION
- Judge whether the revised claim would make a strong exam answer.
- Identify one point that should be corrected, added, or emphasized.
- Stay strictly grounded in the material.

DEBATE OUTCOME
- Write exactly one:
  CLAIM SUPPORTED
  CLAIM PARTIALLY SUPPORTED
  CLAIM NOT SUPPORTED

OUTCOME EXPLANATION
- Explain the result using only the study material.

REFINED UNDERSTANDING
- Give the strongest concise version of the student's understanding
  after the debate.
- Preserve the terminology used in the study material.

FINAL THINKING QUESTION
- Ask one concise question that encourages the student to reason
  from the supplied material.
"""

    combined = generate_grounded_content(
        instruction=instruction,
        context=(
            f"Topic:\n{topic}\n\n"
            f"Study Material:\n{study_context}\n\n"
            f"Earlier Peer Discussion:\n"
            f"{peer_discussion or 'None'}\n\n"
            f"Student Revised Claim:\n{revised_claim}"
        ),
    )

    if not combined.strip():
        return {
            "status": "failed",
            "reason": "empty_generation",
            "topic": topic,
            "debate_result": "",
        }

    return {
        "status": "generated",
        "topic": topic,
        "revised_claim": revised_claim,
        "debate_result": combined,
    }


def summarize_peer_classroom(
    topic: str,
    study_context: str,
    initial_student_response: str,
    misconception_analysis: str = "",
    confidence_analysis: str = "",
    agreement_analysis: str = "",
    revised_claim: str = "",
    debate_result: str = "",
) -> dict:
    """
    F3.7: Complete Synthetic Peer Classroom Learning Summary.

    Combines the learning signals from F3.1-F3.6 into one grounded
    classroom summary without introducing outside information.
    """

    if not topic.strip():
        return {
            "status": "failed",
            "reason": "empty_topic",
            "topic": topic,
            "learning_summary": "",
        }

    if not study_context.strip():
        return {
            "status": "failed",
            "reason": "missing_study_context",
            "topic": topic,
            "learning_summary": "",
        }

    if not initial_student_response.strip():
        return {
            "status": "failed",
            "reason": "missing_initial_student_response",
            "topic": topic,
            "learning_summary": "",
        }

    instruction = f"""
You are the Final Classroom Learning Summary Agent inside
Subject Guide AI's Synthetic Peer Classroom.

Create one concise final learning summary from the completed
peer-learning session.

Topic:
{topic}

Study Material:
{study_context}

Initial Student Response:
{initial_student_response}

Misconception Analysis:
{misconception_analysis or "Not available."}

Confidence and Calibration:
{confidence_analysis or "Not available."}

Peer Agreement and Consensus:
{agreement_analysis or "Not available."}

Revised Claim:
{revised_claim or "Not available."}

Peer Debate Result:
{debate_result or "Not available."}

Use ONLY the supplied study material and supplied classroom outputs.
Do not introduce outside facts.
Do not invent claims.
Do not silently correct or replace the supplied evidence.

Return exactly these sections:

INITIAL UNDERSTANDING
- Summarize what the student originally understood or claimed.

MISCONCEPTION FOUND
- State the supported misconception, or state that no supported
  misconception was identified.

PEER CONSENSUS
- Summarize what the peers agreed on.

CONFIDENCE & CALIBRATION
- State the confidence/calibration signal from the supplied analysis.
- Do not invent a calibration result if none is supplied.

DEBATE RESULT
- State the debate outcome from the supplied debate analysis.

FINAL UNDERSTANDING
- Give the strongest refined understanding supported by the material
  and the classroom discussion.

NEXT THINKING QUESTION
- Ask exactly one concise question that encourages continued reasoning
  from the supplied study material.

Keep the summary student-friendly and concise.
"""

    combined = generate_grounded_content(
        instruction=instruction,
        context=(
            f"Topic:\n{topic}\n\n"
            f"Study Material:\n{study_context}\n\n"
            f"Initial Student Response:\n{initial_student_response}\n\n"
            f"Misconception Analysis:\n{misconception_analysis or 'Not available.'}\n\n"
            f"Confidence and Calibration:\n{confidence_analysis or 'Not available.'}\n\n"
            f"Peer Agreement and Consensus:\n{agreement_analysis or 'Not available.'}\n\n"
            f"Revised Claim:\n{revised_claim or 'Not available.'}\n\n"
            f"Peer Debate Result:\n{debate_result or 'Not available.'}"
        ),
    )

    if not combined.strip():
        return {
            "status": "failed",
            "reason": "empty_generation",
            "topic": topic,
            "learning_summary": "",
        }

    return {
        "status": "generated",
        "topic": topic,
        "learning_summary": combined,
    }
