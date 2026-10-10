import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";

function SyntheticPeerClassroomPage() {
  const [topic, setTopic] = useState("");
  const [studyContext, setStudyContext] = useState("");
  const [studentPrompt, setStudentPrompt] = useState("");
  const [studentResponse, setStudentResponse] = useState("");

  const [classroom, setClassroom] = useState(null);
  const [followup, setFollowup] = useState(null);

  const [loading, setLoading] = useState(false);
  const [followupLoading, setFollowupLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [misconception, setMisconception] = useState(null);
  const [misconceptionLoading, setMisconceptionLoading] = useState(false);
  const [confidenceScore, setConfidenceScore] = useState(50);
  const [confidenceResult, setConfidenceResult] = useState(null);
  const [agreementLoading, setAgreementLoading] = useState(false);
  const [agreementResult, setAgreementResult] = useState(null);
  const [revisedClaim, setRevisedClaim] = useState("");
  const [debateLoading, setDebateLoading] = useState(false);
  const [debateResult, setDebateResult] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryResult, setSummaryResult] = useState(null);
  const [studentId, setStudentId] = useState(null);

  useEffect(() => {
    let mounted = true;

    async function loadAuthenticatedUser() {
      const { data, error } = await supabase.auth.getUser();

      if (error) {
        if (mounted) setMessage("Unable to identify the logged-in student.");
        return;
      }

      if (mounted) {
        setStudentId(data.user?.id || null);
      }
    }

    loadAuthenticatedUser();

    return () => {
      mounted = false;
    };
  }, []);

  async function startClassroom() {
    if (!topic.trim()) {
      setMessage("Enter a topic first.");
      return;
    }

    if (!studyContext.trim()) {
      setMessage("Provide study material before starting the classroom.");
      return;
    }

    setLoading(true);
    setMessage("");
    setClassroom(null);
    setFollowup(null);
    setStudentResponse("");

    try {
      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession();

      if (sessionError || !session?.access_token) {
        throw new Error("Please log in again to start the peer classroom.");
      }

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/synthetic-peer",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({
            topic: topic.trim(),
            student_prompt: studentPrompt.trim(),
            study_context: studyContext.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to start synthetic peer classroom."
        );
      }

      if (data.status !== "generated") {
        throw new Error(
          data.reason || "Synthetic peer classroom could not be generated."
        );
      }

      setClassroom(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function continueClassroom() {
    if (!classroom) {
      setMessage("Start the peer classroom first.");
      return;
    }

    if (!studentResponse.trim()) {
      setMessage("Write your response before continuing.");
      return;
    }

    setFollowupLoading(true);
    setMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/synthetic-peer/followup",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: topic.trim(),
            student_response: studentResponse.trim(),
            study_context: studyContext.trim(),
            initial_discussion:
              classroom.classroom_discussion || "",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to continue the peer classroom."
        );
      }

      if (data.status !== "generated") {
        throw new Error(
          data.reason || "Peer follow-up could not be generated."
        );
      }

      setFollowup(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setFollowupLoading(false);
    }
  }

  async function analyzeMisconception() {
    if (!followup) {
      setMessage("Complete the peer discussion first.");
      return;
    }

    if (!studentResponse.trim()) {
      setMessage("Write your response before analyzing it.");
      return;
    }

    setMisconceptionLoading(true);
    setMessage("");
    setMisconception(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/synthetic-peer/misconception",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: topic.trim(),
            student_response: studentResponse.trim(),
            study_context: studyContext.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to analyze the student response."
        );
      }

      if (data.status !== "generated") {
        throw new Error(
          data.reason || "Misconception analysis could not be generated."
        );
      }

      setMisconception(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setMisconceptionLoading(false);
    }
  }
  async function analyzeConfidence() {
    if (!misconception) {
      setMessage("Run misconception analysis first.");
      return;
    }

    setMessage("");
    setConfidenceResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/synthetic-peer/confidence",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: topic.trim(),
            student_response: studentResponse.trim(),
            confidence_score: Number(confidenceScore),
            misconception_analysis:
              misconception.misconception_analysis || "",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to analyze confidence."
        );
      }

      if (data.status !== "generated") {
        throw new Error(
          data.reason || "Confidence analysis could not be generated."
        );
      }

      setConfidenceResult(data);
    } catch (error) {
      setMessage(error.message);
    }
  }
  async function analyzeAgreement() {
    if (!followup) {
      setMessage("Complete the peer discussion first.");
      return;
    }

    setAgreementLoading(true);
    setAgreementResult(null);
    setMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/synthetic-peer/agreement",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: topic.trim(),
            peer_discussion:
              followup.followup_discussion || "",
            study_context: studyContext.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to analyze peer agreement."
        );
      }

      if (data.status !== "generated") {
        throw new Error(
          data.reason || "Peer agreement analysis could not be generated."
        );
      }

      setAgreementResult(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setAgreementLoading(false);
    }
  }
  async function runPeerDebate() {
    if (!revisedClaim.trim()) {
      setMessage("Write your revised claim before starting the debate.");
      return;
    }

    setDebateLoading(true);
    setDebateResult(null);
    setMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/synthetic-peer/debate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: topic.trim(),
            revised_claim: revisedClaim.trim(),
            study_context: studyContext.trim(),
            peer_discussion: followup?.followup_discussion || "",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to run peer debate."
        );
      }

      if (data.status !== "generated") {
        throw new Error(
          data.reason || "Peer debate could not be generated."
        );
      }

      setDebateResult(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setDebateLoading(false);
    }
  }
  async function generateLearningSummary() {
    if (!studentResponse.trim()) {
      setMessage("Complete the classroom response before generating the summary.");
      return;
    }

    setSummaryLoading(true);
    setSummaryResult(null);
    setMessage("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/synthetic-peer/summary",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: topic.trim(),
            study_context: studyContext.trim(),
            initial_student_response: studentResponse.trim(),
            misconception_analysis:
              misconception?.misconception_analysis || "",
            confidence_analysis: confidenceResult
              ? [
                  `YOUR CONFIDENCE: ${confidenceResult.confidence_score}%`,
                  `UNDERSTANDING: ${confidenceResult.understanding_status}`,
                  `CALIBRATION: ${confidenceResult.calibration}`,
                  `INTERPRETATION: ${confidenceResult.interpretation}`,
                ].join("\n")
              : "",
            agreement_analysis:
              agreementResult?.peer_agreement || "",
            revised_claim: revisedClaim.trim(),
            debate_result:
              debateResult?.debate_result || "",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to generate the classroom summary."
        );
      }

      if (data.status !== "generated") {
        throw new Error(
          data.reason || "Classroom summary could not be generated."
        );
      }

      if (!studentId) {
        throw new Error("Unable to identify the logged-in student.");
      }

      const {
        data: { session },
        error: sessionError,
      } = await supabase.auth.getSession();

      if (sessionError || !session?.access_token) {
        throw new Error("Please log in again to save your learning memory.");
      }

      const compactText = (value, maxLength = 300) =>
        typeof value === "string"
          ? value.replace(/\s+/g, " ").trim().slice(0, maxLength)
          : "";

      const extractSignal = (text, heading, fallback = "") => {
        if (typeof text !== "string") return fallback;

        const labelIndex = text.toLowerCase().indexOf(heading.toLowerCase());
        if (labelIndex < 0) return fallback;

        const followingText = text.slice(labelIndex + heading.length);
        const line = followingText
          .split(/\r?\n/)
          .map((item) => item.replace(/^[-•]\s*/, "").trim())
          .find(Boolean);

        return line || fallback;
      };

      const learningMemory = {
        last_session: {
          topic: compactText(topic, 100),
          initial_understanding: compactText(studentResponse, 300),
          misconception: extractSignal(
            misconception?.misconception_analysis || "",
            "MISCONCEPTION STATUS",
            "NOT RECORDED"
          ),
          confidence: confidenceResult?.confidence_score ?? null,
          calibration: compactText(confidenceResult?.calibration || "", 60),
          peer_agreement: extractSignal(
            agreementResult?.peer_agreement || "",
            "CONSENSUS LEVEL",
            "NOT RECORDED"
          ),
          revised_claim: compactText(revisedClaim, 300),
          debate_result: extractSignal(
            debateResult?.debate_result || "",
            "DEBATE OUTCOME",
            "NOT RECORDED"
          ),
          final_understanding: compactText(
            extractSignal(
              data.learning_summary || "",
              "FINAL UNDERSTANDING",
              ""
            ),
            500
          ),
          next_thinking_question: compactText(
            extractSignal(
              data.learning_summary || "",
              "NEXT THINKING QUESTION",
              ""
            ),
            200
          ),
        },
        updated_at: new Date().toISOString(),
      };

      const profileUrl = `http://127.0.0.1:8000/api/v1/students/${studentId}/profile`;

      const profileResponse = await fetch(profileUrl, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      });

      const profileData = await profileResponse.json();

      if (!profileResponse.ok) {
        throw new Error(
          profileData.detail || "Student profile could not be created."
        );
      }

      const memoryResponse = await fetch(
        profileUrl,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({
            learning_memory: learningMemory,
          }),
        }
      );

      const memoryData = await memoryResponse.json();

      if (!memoryResponse.ok) {
        throw new Error(
          memoryData.detail || "Learning memory could not be saved."
        );
      }

      setSummaryResult(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSummaryLoading(false);
    }
  }
  const fieldStyle = {
    width: "100%",
    boxSizing: "border-box",
    border: "1px solid rgba(130,145,255,0.18)",
    borderRadius: "14px",
    background: "rgba(5,8,20,0.72)",
    color: "#e8ecff",
    padding: "14px 16px",
    outline: "none",
    fontFamily: "inherit",
    fontSize: "15px",
    lineHeight: 1.5,
  };

  return (
    <section
      className="page-content"
      style={{
        width: "100%",
        maxWidth: "1180px",
        margin: "0 auto",
        boxSizing: "border-box",
      }}
    >
      <div
        className="question-card"
        style={{
          width: "100%",
          maxWidth: "none",
          boxSizing: "border-box",
          padding: "30px",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "28px" }}>
          <span className="eyebrow">
            F3 - SYNTHETIC PEER CLASSROOM
          </span>

          <h1 style={{ marginTop: "10px", marginBottom: "10px" }}>
            Learn through AI classmates.
          </h1>

          <p
            className="muted"
            style={{
              maxWidth: "760px",
              margin: "0 auto",
              lineHeight: 1.6,
            }}
          >
            Explain your thinking, face peer challenges, and refine your
            understanding through discussion.
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "18px",
            marginBottom: "18px",
          }}
        >
          <div>
            <label>
              <span className="eyebrow">TOPIC</span>
              <input
                type="text"
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                placeholder="Example: C Pointers"
                style={{
                  ...fieldStyle,
                  marginTop: "8px",
                }}
              />
            </label>
          </div>

          <div>
            <label>
              <span className="eyebrow">YOUR PROMPT</span>
              <textarea
                rows={3}
                value={studentPrompt}
                onChange={(event) =>
                  setStudentPrompt(event.target.value)
                }
                placeholder="Example: Explain pointers and challenge my understanding."
                style={{
                  ...fieldStyle,
                  marginTop: "8px",
                  resize: "vertical",
                }}
              />
            </label>
          </div>
        </div>

        <div>
          <label>
            <span className="eyebrow">STUDY MATERIAL</span>
            <textarea
              rows={8}
              value={studyContext}
              onChange={(event) =>
                setStudyContext(event.target.value)
              }
              placeholder="Paste your notes, textbook content, or study material here..."
              style={{
                ...fieldStyle,
                marginTop: "8px",
                minHeight: "190px",
                resize: "vertical",
              }}
            />
          </label>
        </div>

        <button
          type="button"
          className="login-submit"
          onClick={startClassroom}
          disabled={loading}
          style={{
            width: "100%",
            marginTop: "20px",
          }}
        >
          <span>
            {loading
              ? "STARTING PEER CLASSROOM..."
              : "START PEER CLASSROOM"}
          </span>
          <b>&gt;</b>
        </button>

        {message && (
          <div
            className="login-message"
            style={{
              marginTop: "16px",
              textAlign: "center",
            }}
          >
            {message}
          </div>
        )}
      </div>

      {classroom && (
        <>
          <div
            className="question-card"
            style={{
              width: "100%",
              maxWidth: "none",
              boxSizing: "border-box",
              marginTop: "24px",
              padding: "28px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "14px",
                flexWrap: "wrap",
                marginBottom: "18px",
              }}
            >
              <div>
                <span className="eyebrow">
                  CLASSROOM ROUND 01
                </span>
                <h2 style={{ marginTop: "8px", marginBottom: 0 }}>
                  Initial peer discussion
                </h2>
              </div>

              <div
                style={{
                  display: "flex",
                  gap: "8px",
                  flexWrap: "wrap",
                }}
              >
                {classroom.peer_roles?.map((role) => (
                  <span className="question-type" key={role}>
                    {role.replace("_", " ").toUpperCase()}
                  </span>
                ))}
              </div>
            </div>

            <div
              style={{
                padding: "22px",
                borderRadius: "16px",
                background: "rgba(5,8,20,0.72)",
                border: "1px solid rgba(130,145,255,0.16)",
              }}
            >
              <pre
                style={{
                  margin: 0,
                  whiteSpace: "pre-wrap",
                  lineHeight: 1.7,
                  fontFamily: "inherit",
                  fontSize: "15px",
                  color: "#e8ecff",
                }}
              >
                {classroom.classroom_discussion}
              </pre>
            </div>
          </div>

          <div
            className="question-card"
            style={{
              width: "100%",
              maxWidth: "none",
              boxSizing: "border-box",
              marginTop: "24px",
              padding: "28px",
            }}
          >
            <span className="eyebrow">
              STUDENT TURN
            </span>

            <h2 style={{ marginTop: "8px" }}>
              Defend your understanding
            </h2>

            <p className="muted">
              Answer the peers in your own words. The next round will
              challenge and evaluate your reasoning.
            </p>

            <textarea
              rows={7}
              value={studentResponse}
              onChange={(event) =>
                setStudentResponse(event.target.value)
              }
              placeholder="Write your explanation or answer here..."
              style={{
                ...fieldStyle,
                marginTop: "12px",
                minHeight: "160px",
                resize: "vertical",
              }}
            />

            <div
              style={{
                marginTop: "18px",
                padding: "18px",
                borderRadius: "16px",
                background: "rgba(5,8,20,0.52)",
                border: "1px solid rgba(130,145,255,0.14)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: "12px",
                  marginBottom: "10px",
                }}
              >
                <div>
                  <span className="eyebrow">
                    SELF-CONFIDENCE
                  </span>
                  <div
                    className="muted"
                    style={{ marginTop: "5px" }}
                  >
                    How confident are you in your answer?
                  </div>
                </div>

                <strong style={{ fontSize: "24px" }}>
                  {confidenceScore}%
                </strong>
              </div>

              <input
                type="range"
                min="0"
                max="100"
                step="10"
                value={confidenceScore}
                onChange={(event) =>
                  setConfidenceScore(Number(event.target.value))
                }
                style={{
                  width: "100%",
                  accentColor: "#8f9cff",
                  cursor: "pointer",
                }}
              />

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginTop: "6px",
                  fontSize: "12px",
                  opacity: 0.65,
                }}
              >
                <span>Not confident</span>
                <span>Very confident</span>
              </div>
            </div>
            <button
              type="button"
              className="login-submit"
              onClick={continueClassroom}
              disabled={followupLoading}
              style={{
                width: "100%",
                marginTop: "16px",
              }}
            >
              <span>
                {followupLoading
                  ? "PEERS ARE RESPONDING..."
                  : "CONTINUE PEER DISCUSSION"}
              </span>
              <b>&gt;</b>
            </button>
          </div>
        </>
      )}

      {followup && (
        <div
          className="question-card"
          style={{
            width: "100%",
            maxWidth: "none",
            boxSizing: "border-box",
            marginTop: "24px",
            padding: "28px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "14px",
              flexWrap: "wrap",
              marginBottom: "18px",
            }}
          >
            <div>
              <span className="eyebrow">
                CLASSROOM ROUND 02
              </span>
              <h2 style={{ marginTop: "8px", marginBottom: 0 }}>
                Peer challenge and synthesis
              </h2>
            </div>

            <span className="question-type">
              PEER SYNTHESIS
            </span>
          </div>

          <div
            style={{
              padding: "22px",
              borderRadius: "16px",
              background: "rgba(5,8,20,0.72)",
              border: "1px solid rgba(130,145,255,0.16)",
            }}
          >
            <pre
              style={{
                margin: 0,
                whiteSpace: "pre-wrap",
                lineHeight: 1.7,
                fontFamily: "inherit",
                fontSize: "15px",
                color: "#e8ecff",
              }}
            >
              {followup.followup_discussion}
            </pre>
          </div>
        </div>
      )}
      {followup && (
        <div
          className="question-card"
          style={{
            width: "100%",
            maxWidth: "none",
            boxSizing: "border-box",
            marginTop: "24px",
            padding: "28px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "14px",
              flexWrap: "wrap",
              marginBottom: "16px",
            }}
          >
            <div>
              <span className="eyebrow">
                ROUND 03 - MISCONCEPTION CHECK
              </span>
              <h2 style={{ marginTop: "8px", marginBottom: 0 }}>
                Check your understanding
              </h2>
            </div>

            <span className="question-type">
              GROUNDED ANALYSIS
            </span>
          </div>

          <p className="muted">
            The system compares your response only with the supplied study
            material and identifies a supported misconception, missing idea,
            or aligned understanding.
          </p>

          <button
            type="button"
            className="login-submit"
            onClick={analyzeMisconception}
            disabled={misconceptionLoading}
            style={{
              width: "100%",
              marginTop: "16px",
            }}
          >
            <span>
              {misconceptionLoading
                ? "ANALYZING YOUR UNDERSTANDING..."
                : "ANALYZE MY UNDERSTANDING"}
            </span>
            <b>&gt;</b>
          </button>

          {misconception && (
            <div
              style={{
                marginTop: "20px",
                padding: "22px",
                borderRadius: "16px",
                background: "rgba(5,8,20,0.72)",
                border: "1px solid rgba(130,145,255,0.16)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: "12px",
                  flexWrap: "wrap",
                  marginBottom: "14px",
                }}
              >
                <div>
                  <span className="eyebrow">
                    MISCONCEPTION ANALYSIS
                  </span>
                  <h3 style={{ marginTop: "6px", marginBottom: 0 }}>
                    Peer learning signal
                  </h3>
                </div>

                <span className="question-type">
                  {misconception.status === "generated"
                    ? "ANALYZED"
                    : "REVIEW"}
                </span>
              </div>

              <pre
                style={{
                  margin: 0,
                  whiteSpace: "pre-wrap",
                  lineHeight: 1.7,
                  fontFamily: "inherit",
                  fontSize: "15px",
                  color: "#e8ecff",
                }}
              >
                {misconception.misconception_analysis}
              </pre>
            </div>
          )}
        </div>
      )}
      {misconception && (
        <div
          className="question-card"
          style={{
            width: "100%",
            maxWidth: "none",
            boxSizing: "border-box",
            marginTop: "24px",
            padding: "28px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "14px",
              flexWrap: "wrap",
              marginBottom: "16px",
            }}
          >
            <div>
              <span className="eyebrow">
                CONFIDENCE & CALIBRATION
              </span>
              <h2 style={{ marginTop: "8px", marginBottom: 0 }}>
                Does your confidence match your understanding?
              </h2>
            </div>

            <span className="question-type">
              F3.4
            </span>
          </div>

          <p className="muted">
            Your self-confidence is compared with the grounded misconception
            analysis to identify whether your confidence is calibrated.
          </p>

          <button
            type="button"
            className="login-submit"
            onClick={analyzeConfidence}
            disabled={!misconception}
            style={{
              width: "100%",
              marginTop: "16px",
            }}
          >
            <span>ANALYZE CONFIDENCE & CALIBRATION</span>
            <b>&gt;</b>
          </button>

          {confidenceResult && (
            <div
              style={{
                marginTop: "20px",
                padding: "22px",
                borderRadius: "16px",
                background: "rgba(5,8,20,0.72)",
                border: "1px solid rgba(130,145,255,0.16)",
              }}
            >
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(190px, 1fr))",
                  gap: "12px",
                  marginBottom: "18px",
                }}
              >
                <div
                  style={{
                    padding: "16px",
                    borderRadius: "14px",
                    background: "rgba(130,145,255,0.07)",
                  }}
                >
                  <span className="eyebrow">YOUR CONFIDENCE</span>
                  <strong
                    style={{
                      display: "block",
                      marginTop: "6px",
                      fontSize: "26px",
                    }}
                  >
                    {confidenceResult.confidence_score}%
                  </strong>
                </div>

                <div
                  style={{
                    padding: "16px",
                    borderRadius: "14px",
                    background: "rgba(130,145,255,0.07)",
                  }}
                >
                  <span className="eyebrow">UNDERSTANDING</span>
                  <strong
                    style={{
                      display: "block",
                      marginTop: "6px",
                      fontSize: "15px",
                    }}
                  >
                    {confidenceResult.understanding_status}
                  </strong>
                </div>

                <div
                  style={{
                    padding: "16px",
                    borderRadius: "14px",
                    background: "rgba(130,145,255,0.07)",
                  }}
                >
                  <span className="eyebrow">CALIBRATION</span>
                  <strong
                    style={{
                      display: "block",
                      marginTop: "6px",
                      fontSize: "15px",
                    }}
                  >
                    {confidenceResult.calibration}
                  </strong>
                </div>
              </div>

              <div>
                <span className="eyebrow">INTERPRETATION</span>
                <p
                  className="muted"
                  style={{
                    marginTop: "8px",
                    lineHeight: 1.6,
                  }}
                >
                  {confidenceResult.interpretation}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
      {followup && (
        <div
          className="question-card"
          style={{
            width: "100%",
            maxWidth: "none",
            boxSizing: "border-box",
            marginTop: "24px",
            padding: "28px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "16px",
              flexWrap: "wrap",
            }}
          >
            <div>
              <span className="eyebrow">
                PEER AGREEMENT & CONSENSUS
              </span>
              <h2 style={{ marginTop: "8px", marginBottom: 0 }}>
                What do the peers agree on?
              </h2>
            </div>

            <span className="question-type">
              F3.5
            </span>
          </div>

          <p className="muted">
            Compare the Explainer, Skeptic, and Exam peers to identify
            shared understanding, viewpoint differences, and the final
            learning signal.
          </p>

          <button
            type="button"
            className="login-submit"
            onClick={analyzeAgreement}
            disabled={agreementLoading}
            style={{
              width: "100%",
              marginTop: "16px",
            }}
          >
            <span>
              {agreementLoading
                ? "ANALYZING PEER AGREEMENT..."
                : "ANALYZE PEER AGREEMENT & CONSENSUS"}
            </span>
            <b>&gt;</b>
          </button>

          {agreementResult && (
            <div
              style={{
                marginTop: "20px",
                padding: "22px",
                borderRadius: "16px",
                background: "rgba(5,8,20,0.72)",
                border: "1px solid rgba(130,145,255,0.16)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "12px",
                  marginBottom: "16px",
                }}
              >
                <span className="eyebrow">
                  CONSENSUS ANALYSIS
                </span>

                <span className="question-type">
                  ANALYZED
                </span>
              </div>

              <pre
                style={{
                  margin: 0,
                  whiteSpace: "pre-wrap",
                  fontSize: "15px",
                  lineHeight: 1.65,
                  color: "#e8ecff",
                  fontFamily: "inherit",
                }}
              >
                {agreementResult.peer_agreement}
              </pre>
            </div>
          )}
        </div>
      )}
      {followup && (
        <div
          className="question-card"
          style={{
            width: "100%",
            maxWidth: "none",
            boxSizing: "border-box",
            marginTop: "24px",
            padding: "28px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "16px",
              flexWrap: "wrap",
            }}
          >
            <div>
              <span className="eyebrow">
                PEER DEBATE & COUNTERARGUMENT
              </span>
              <h2 style={{ marginTop: "8px", marginBottom: 0 }}>
                Defend your revised understanding
              </h2>
            </div>

            <span className="question-type">
              F3.6
            </span>
          </div>

          <p className="muted">
            Submit your revised claim after peer feedback. The Explainer,
            Skeptic, and Exam peers will debate it using only the study material.
          </p>

          <textarea
            value={revisedClaim}
            onChange={(event) => setRevisedClaim(event.target.value)}
            placeholder="Write your corrected understanding or revised claim here..."
            style={{
              width: "100%",
              boxSizing: "border-box",
              minHeight: "140px",
              marginTop: "16px",
              padding: "14px",
              borderRadius: "12px",
              resize: "vertical",
            }}
          />

          <button
            type="button"
            className="login-submit"
            onClick={runPeerDebate}
            disabled={debateLoading}
            style={{
              width: "100%",
              marginTop: "16px",
            }}
          >
            <span>
              {debateLoading
                ? "RUNNING PEER DEBATE..."
                : "RUN PEER DEBATE & COUNTERARGUMENT"}
            </span>
            <b>&gt;</b>
          </button>

          {debateResult && (
            <div
              style={{
                marginTop: "20px",
                padding: "22px",
                borderRadius: "16px",
                background: "rgba(5,8,20,0.72)",
                border: "1px solid rgba(130,145,255,0.16)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "12px",
                  marginBottom: "16px",
                }}
              >
                <span className="eyebrow">
                  DEBATE ANALYSIS
                </span>

                <span className="question-type">
                  ANALYZED
                </span>
              </div>

              <pre
                style={{
                  margin: 0,
                  whiteSpace: "pre-wrap",
                  fontSize: "15px",
                  lineHeight: 1.65,
                  color: "#e8ecff",
                  fontFamily: "inherit",
                }}
              >
                {debateResult.debate_result}
              </pre>
            </div>
          )}
        </div>
      )}
      {followup && (
        <div
          className="question-card"
          style={{
            width: "100%",
            maxWidth: "none",
            boxSizing: "border-box",
            marginTop: "24px",
            padding: "28px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "16px",
              flexWrap: "wrap",
            }}
          >
            <div>
              <span className="eyebrow">
                CLASSROOM LEARNING SUMMARY
              </span>
              <h2 style={{ marginTop: "8px", marginBottom: 0 }}>
                Your complete learning cycle
              </h2>
            </div>

            <span className="question-type">
              F3.7
            </span>
          </div>

          <p className="muted">
            Combine the peer discussion, misconception analysis, confidence
            calibration, consensus, and debate into one final learning signal.
          </p>

          <button
            type="button"
            className="login-submit"
            onClick={generateLearningSummary}
            disabled={summaryLoading}
            style={{
              width: "100%",
              marginTop: "16px",
            }}
          >
            <span>
              {summaryLoading
                ? "GENERATING LEARNING SUMMARY..."
                : "GENERATE CLASSROOM LEARNING SUMMARY"}
            </span>
            <b>&gt;</b>
          </button>

          {summaryResult && (
            <div
              style={{
                marginTop: "20px",
                padding: "22px",
                borderRadius: "16px",
                background: "rgba(5,8,20,0.72)",
                border: "1px solid rgba(130,145,255,0.16)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "12px",
                  marginBottom: "16px",
                }}
              >
                <span className="eyebrow">
                  FINAL LEARNING SIGNAL
                </span>

                <span className="question-type">
                  ANALYZED
                </span>
              </div>

              <pre
                style={{
                  margin: 0,
                  whiteSpace: "pre-wrap",
                  fontSize: "15px",
                  lineHeight: 1.65,
                  color: "#e8ecff",
                  fontFamily: "inherit",
                }}
              >
                {summaryResult.learning_summary}
              </pre>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

export default SyntheticPeerClassroomPage;







