import React, { useState } from "react";
import ReconstructionGate from "../components/ReconstructionGate";

const initialSteps = [
  {
    id: 1,
    status: "pending",
    title: "Input reasoning",
    description: "Submit a solution, proof, code explanation, or logical argument for verification.",
  },
  {
    id: 2,
    status: "pending",
    title: "Neural interpretation",
    description: "The reasoning is converted into structured claims and logical steps.",
  },
  {
    id: 3,
    status: "pending",
    title: "Symbolic verification",
    description: "Each claim is checked against deterministic rules and formal constraints.",
  },
  {
    id: 4,
    status: "pending",
    title: "Verdict",
    description: "The system identifies verified steps, contradictions, or unsupported claims.",
  },
];

export default function VerifiedReasoningPage({ isLightMode = false }) {
  const [reasoning, setReasoning] = useState("");
  const [steps, setSteps] = useState(initialSteps);
  const [verifying, setVerifying] = useState(false);
  const [result, setResult] = useState(null);
  const [reconstructionGateOpen, setReconstructionGateOpen] = useState(false);
  const [reconstructionTopic, setReconstructionTopic] = useState("Verified reasoning");
  const [reconstructionProblem, setReconstructionProblem] = useState("");
  const [reconstructionPrompt, setReconstructionPrompt] = useState("");
  const [reconstructionAttempts, setReconstructionAttempts] = useState(0);
  const [reconstructionHint, setReconstructionHint] = useState("");
  const [reconstructionSubmitting, setReconstructionSubmitting] = useState(false);
  const [reconstructionOutcome, setReconstructionOutcome] = useState(null);
  const [nextLearningStep, setNextLearningStep] = useState("");
  const [nextLearningAssessment, setNextLearningAssessment] = useState("");
  const [nextLearningLoading, setNextLearningLoading] = useState(false);
  const [metacognitiveCalibration, setMetacognitiveCalibration] = useState(null);
  const [hintDependencyState, setHintDependencyState] = useState(null);
  const [jolPercent, setJolPercent] = useState(null);

  const theme = isLightMode
    ? {
        page: "#f8fafc",
        surface: "#ffffff",
        surfaceSoft: "#f1f5f9",
        input: "#f8fafc",
        text: "#0f172a",
        muted: "#64748b",
        border: "rgba(15, 23, 42, 0.10)",
      }
    : {
        page: "#08111f",
        surface: "rgba(15, 23, 42, 0.86)",
        surfaceSoft: "rgba(30, 41, 59, 0.42)",
        input: "#07101e",
        text: "#f8fafc",
        muted: "#94a3b8",
        border: "rgba(148, 163, 184, 0.14)",
      };

  const verifyReasoning = async () => {
    if (!reasoning.trim()) return;
    if (jolPercent === null) {
      setResult({
        type: "failed",
        title: "Confidence required",
        message:
          "Select your confidence level before verifying your reasoning.",
        score: 0,
      });
      return;
    }

    setVerifying(true);
    setResult(null);

    setSteps(
      initialSteps.map((step, index) => ({
        ...step,
        status: index === 0 ? "active" : "pending",
      }))
    );

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/verified-reasoning",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            reasoning: reasoning.trim(),
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Verification request failed: ${response.status}`);
      }

      const data = await response.json();

      const isVerified = data.status === "verified";

      const evidenceType = data.evidence?.type || "";

      const failureStageIndex =
        evidenceType === "insufficient_input"
          ? 0
          : evidenceType === "parsing_or_structure"
            ? 1
            : [
                "transition_preservation",
                "domain_restriction",
                "structural_verification",
                "python_syntax",
              ].includes(evidenceType)
              ? 2
              : 3;

      setSteps(
        initialSteps.map((step, index) => ({
          ...step,
          status: isVerified
            ? "verified"
            : index < failureStageIndex
              ? "verified"
              : index === failureStageIndex
                ? "failed"
                : "pending",
        }))
      );


      if (isVerified) {
        setReconstructionProblem(reasoning.trim());
        setReconstructionPrompt(
          "Without copying the verified solution, reconstruct the result independently and explain the key operation that makes your answer valid."
        );
        setReconstructionHint("");
        setReconstructionAttempts(0);
      }

      setResult({
        type: isVerified ? "verified" : "failed",
        title: isVerified
          ? "Reasoning verified"
          : "Reasoning failed verification",
        message: data.hint,
        score: Math.round((data.confidence || 0) * 100),
        evidence: data.evidence || null,
      });
    } catch (error) {
      console.error("Verified reasoning error:", error);

      setResult({
        type: "failed",
        title: "Verification unavailable",
        message:
          "The verification service could not be reached. Make sure the backend is running on port 8000.",
        score: 0,
      });

      setSteps(
        initialSteps.map((step) => ({
          ...step,
          status: "pending",
        }))
      );
    } finally {
      setVerifying(false);
    }
  };

  const startReconstruction = async () => {
    setReconstructionGateOpen(true);

    if (!reconstructionProblem.trim()) {
      setReconstructionHint(
        "The verified reasoning is not available for reconstruction yet."
      );
      return;
    }


    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/reconstruction-gate/start",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            student_id: "demo_student",
            topic: reconstructionTopic,
            reason: "independent_reconstruction_required",
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Reconstruction gate start failed: ${response.status}`);
      }

      const data = await response.json();

      setReconstructionAttempts(data.reconstruction_attempts || 0);

      setReconstructionHint("");
      setReconstructionGateOpen(data.status === "LOCKED");
    } catch (error) {
      console.error("Reconstruction gate start error:", error);
    }
  };

  const generateNextLearningStep = async (studentResponse) => {
    setNextLearningLoading(true);
    setNextLearningStep("");
    setNextLearningAssessment("");

    try {
      const assessmentReport = [
        "F1 verified the student's reasoning.",
        "F2 independent reconstruction passed.",
        `Independent reconstruction: ${studentResponse}`,
        "The student demonstrated independent understanding of the verified reasoning.",
      ].join(" ");

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/adaptive-learning",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: reconstructionTopic,
            assessment_report: assessmentReport,
            current_knowledge:
              "The student independently reconstructed the verified reasoning and passed the reconstruction gate.",
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Adaptive learning request failed: ${response.status}`
        );
      }

      const data = await response.json();
      const report = data.adaptive_learning_report || "";

      const nextStepSection = report.match(
        /6\.\s*Next Learning Step[\s\S]*?(?=7\.\s*Next Assessment)/i
      );

      const nextAssessmentSection = report.match(
        /7\.\s*Next Assessment[\s\S]*$/i
      );

      const nextStepText =
        nextStepSection?.[0]
          ?.replace(/6\.\s*Next Learning Step/i, "")
          ?.replace(/^\s*-\s*/m, "")
          ?.trim();

      const nextAssessmentText =
        nextAssessmentSection?.[0]
          ?.replace(/7\.\s*Next Assessment/i, "")
          ?.replace(/^\s*-\s*/m, "")
          ?.trim();

      setNextLearningStep(
        nextStepText ||
          "Adaptive Learning recommends progressing to the next learning stage."
      );

      setNextLearningAssessment(
        nextAssessmentText ||
          "A new independent assessment should be used to verify the next concept."
      );
    } catch (error) {
      console.error("Next learning step error:", error);

      setNextLearningStep(
        "The reconstruction passed, but the adaptive next-step service could not be reached."
      );

      setNextLearningAssessment(
        "Retry adaptive learning generation before starting the next assessment."
      );
    } finally {
      setNextLearningLoading(false);
    }
  };
  const submitReconstruction = async (studentResponse) => {
    setReconstructionSubmitting(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/reconstruction-gate/evaluate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            student_id: "demo_student",
            topic: reconstructionTopic,
            original_problem: reconstructionProblem,
            student_response: studentResponse,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Reconstruction evaluation failed: ${response.status}`);
      }

      const data = await response.json();

      setReconstructionAttempts(data.reconstruction_attempts || 0);

      // --- F2.11: record real metacognitive evidence ---
      const independentPerformance =
        data.gate_status === "UNLOCKED" ? 1 : 0;
      const usedHint = Boolean(reconstructionHint.trim());

      if (jolPercent !== null) {
        try {
          const calibrationResponse = await fetch(
            "http://127.0.0.1:8000/api/v1/metacognitive/evaluate",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                student_id: "demo_student",
                topic: reconstructionTopic,
                jol: jolPercent / 100,
                independent_performance: independentPerformance,
                hint_count: usedHint ? 1 : 0,
                unassisted: !usedHint,
              }),
            }
          );

          console.info(
            "METACOGNITIVE_CALIBRATION_RESPONSE",
            calibrationResponse.status
          );

          if (calibrationResponse.ok) {
            const calibrationData = await calibrationResponse.json();

            console.info(
              "METACOGNITIVE_CALIBRATION_DATA",
              calibrationData
            );

            setMetacognitiveCalibration(calibrationData);
          } else {
            const errorText = await calibrationResponse.text();

            console.error(
              "METACOGNITIVE_CALIBRATION_FAILED",
              calibrationResponse.status,
              errorText
            );
          }
        } catch (metacognitiveError) {
          console.error(
            "Metacognitive calibration error:",
            metacognitiveError
          );
        }
      }

      try {
        const hintResponse = await fetch(
          "http://127.0.0.1:8000/api/v1/metacognitive/hint-dependency",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              student_id: "demo_student",
              topic: reconstructionTopic,
              used_hint: usedHint,
              independent_check_passed:
                data.gate_status === "UNLOCKED",
            }),
          }
        );

        if (hintResponse.ok) {
          const hintData = await hintResponse.json();
          setHintDependencyState(hintData);
        }
      } catch (hintError) {
        console.error(
          "Hint dependency tracking error:",
          hintError
        );
      }

      console.info(
        "METACOGNITIVE_CALIBRATION_RECORDED",
        {
          jol: jolPercent,
          independentPerformance,
          usedHint,
        }
      );


      if (data.gate_status === "UNLOCKED") {
        setReconstructionOutcome({
          type: "success",
          title: "Independent Reconstruction Verified",
          message: "Your independent reconstruction matches the verified solution. The next learning step is now unlocked.",
          attempts: data.reconstruction_attempts || 0,
        });
        setReconstructionHint("");
        setReconstructionGateOpen(false);
        generateNextLearningStep(studentResponse);
      } else {
        setReconstructionHint(
          data.socratic?.hint ||
          "Reconstruct the reasoning again and identify the first operation that must remain valid."
        );
      }
    } catch (error) {
      console.error("Reconstruction evaluation error:", error);
      setReconstructionHint(
        "The reconstruction service could not be reached. Make sure the backend is running on port 8000."
      );
    } finally {
      setReconstructionSubmitting(false);
    }
  };
  const clearReasoning = () => {
    setReasoning("");
    setResult(null);
    setJolPercent(null);
    setSteps(initialSteps);
  };

  return (
    <div
      style={{
        minHeight: "100%",
        padding: "28px",
        background: isLightMode ? theme.page : "linear-gradient(135deg, #08111f 0%, #0b1729 55%, #101c31 100%)",
        color: theme.text,
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      }}
    >
      <div style={{ maxWidth: "1280px", margin: "0 auto" }}>
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: "24px",
            marginBottom: "28px",
          }}
        >
          <div>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "7px 12px",
                borderRadius: "999px",
                background: "rgba(59, 130, 246, 0.12)",
                border: "1px solid rgba(96, 165, 250, 0.24)",
                color: "#93c5fd",
                fontSize: "12px",
                fontWeight: 700,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              <span
                style={{
                  width: "7px",
                  height: "7px",
                  borderRadius: "50%",
                  background: verifying ? "#f59e0b" : "#22c55e",
                  boxShadow: verifying
                    ? "0 0 12px rgba(245,158,11,.7)"
                    : "0 0 12px rgba(34,197,94,.7)",
                }}
              />
              {verifying ? "Metacognitive Reasoning · Verifying" : "Metacognitive Reasoning"}
            </div>

            <h1
              style={{
                margin: "16px 0 8px",
                fontSize: "32px",
                lineHeight: 1.15,
                fontWeight: 800,
                letterSpacing: "-0.03em",
              }}
            >
              Metacognitive Reasoning
            </h1>

            <p
              style={{
                margin: 0,
                maxWidth: "720px",
                color: theme.muted,
                fontSize: "15px",
                lineHeight: 1.7,
              }}
            >
              Don't just ask whether AI sounds correct. Break the reasoning
              into verifiable steps and identify exactly where an argument,
              calculation, or solution fails.
            </p>
          </div>

          <div
            style={{
              minWidth: "190px",
              padding: "16px",
              borderRadius: "16px",
              background: theme.surfaceSoft,
              border: `1px solid ${theme.border}`,
              boxShadow: "0 16px 40px rgba(0,0,0,.18)",
            }}
          >
            <div
              style={{
                color: "#64748b",
                fontSize: "11px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
              }}
            >
              Learning Control
            </div>
            <div
              style={{
                marginTop: "7px",
                fontSize: "18px",
                fontWeight: 750,
              }}
            >
              Think → Verify → Reconstruct
            </div>
            <div
              style={{
                marginTop: "5px",
                color: "#64748b",
                fontSize: "12px",
              }}
            >
              Confidence, independence, and adaptive progression
            </div>
          </div>
        </header>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "1fr",
            gap: "20px",
            marginBottom: "20px",
          }}
        >
          <div
            style={{
              borderRadius: "20px",
              background: theme.surface,
              border: `1px solid ${theme.border}`,
              boxShadow: "0 20px 50px rgba(0,0,0,.2)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                padding: "20px 22px",
                borderBottom: "1px solid rgba(148,163,184,.1)",
              }}
            >
              <div style={{ fontSize: "16px", fontWeight: 750 }}>
                Reasoning / solution input
              </div>
              <div
                style={{
                  marginTop: "5px",
                  color: "#64748b",
                  fontSize: "12px",
                }}
              >
                Paste the student's complete reasoning, not only the final
                answer.
              </div>
            </div>

            <div style={{ padding: "22px" }}>
              <textarea
                value={reasoning}
                onChange={(event) => setReasoning(event.target.value)}
                placeholder={
                  "Example:\n\nIf 2x + 5 = 15,\n2x = 10,\ntherefore x = 5.\n\nExplain why each step is valid."
                }
                style={{
                  width: "100%",
                  minHeight: "320px",
                  boxSizing: "border-box",
                  resize: "vertical",
                  padding: "17px",
                  borderRadius: "14px",
                  border: `1px solid ${theme.border}`,
                  outline: "none",
                  background: theme.input,
                  color: theme.text,
                  fontSize: "14px",
                  lineHeight: 1.7,
                  fontFamily: "inherit",
                }}
              />

              <div
                style={{
                  marginTop: "16px",
                  padding: "16px",
                  borderRadius: "14px",
                  background: theme.surfaceSoft,
                  border: `1px solid ${theme.border}`,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: "12px",
                  }}
                >
                  <div>
                    <div
                      style={{
                        fontSize: "12px",
                        fontWeight: 800,
                        color: theme.text,
                      }}
                    >
                      Confidence before verification
                    </div>
                    <div
                      style={{
                        marginTop: "4px",
                        fontSize: "11px",
                        color: theme.muted,
                      }}
                    >
                      How confident are you that your reasoning is correct?
                    </div>
                  </div>

                  <div
                    style={{
                      minWidth: "52px",
                      textAlign: "right",
                      fontSize: "16px",
                      fontWeight: 850,
                      color: "#a78bfa",
                    }}
                  >
                    {jolPercent === null ? "Select" : `${jolPercent}%`}
                  </div>
                </div>

                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={jolPercent ?? 0}
                  onChange={(event) =>
                    setJolPercent(Number(event.target.value))
                  }
                  style={{
                    width: "100%",
                    marginTop: "13px",
                    accentColor: "#8b5cf6",
                    cursor: "pointer",
                  }}
                />

                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginTop: "6px",
                    fontSize: "10px",
                    color: theme.muted,
                  }}
                >
                  <span>0% - Not confident</span>
                  <span>100% - Fully confident</span>
                </div>
              </div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginTop: "16px",
                  gap: "12px",
                }}
              >
                
<button
                  type="button"
                  onClick={clearReasoning}
                  style={{
                    border: `1px solid ${theme.border}`,
                    background: "transparent",
                    color: theme.muted,
                    borderRadius: "11px",
                    padding: "11px 16px",
                    cursor: "pointer",
                    fontWeight: 650,
                  }}
                >
                  Clear
                </button>

                <button
                  type="button"
                  onClick={verifyReasoning}
                  disabled={verifying || !reasoning.trim() || jolPercent === null}
                  style={{
                    border: "none",
                    background:
                      verifying || !reasoning.trim()
                        ? "#1e3a5f"
                        : "linear-gradient(135deg, #2563eb, #4f46e5)",
                    color: "#fff",
                    borderRadius: "11px",
                    padding: "12px 22px",
                    cursor:
                      verifying || !reasoning.trim()
                        ? "not-allowed"
                        : "pointer",
                    fontWeight: 750,
                    boxShadow:
                      verifying || !reasoning.trim()
                        ? "none"
                        : "0 10px 24px rgba(37,99,235,.25)",
                  }}
                >
                  {verifying ? "Verifying..." : "Verify Reasoning"}
                </button>
              </div>
            </div>
          </div>

          <div
            style={{
              borderRadius: "20px",
              background: theme.surface,
              border: `1px solid ${theme.border}`,
              padding: "22px",
            }}
          >
            <div style={{ fontSize: "16px", fontWeight: 750 }}>
              Verification philosophy
            </div>

            <div
              style={{
                marginTop: "18px",
                display: "grid",
                gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
                gap: "12px",
              }}
            >
              {[
                ["01", "Interpret", "Understand the student's reasoning."],
                ["02", "Formalize", "Convert claims into checkable structures."],
                ["03", "Verify", "Use deterministic rules where possible."],
                ["04", "Explain", "Return evidence instead of a blind verdict."],
              ].map(([number, title, description]) => (
                <div
                  key={number}
                  style={{
                    display: "flex",
                    gap: "13px",
                    padding: "13px",
                    borderRadius: "13px",
                    background: theme.surfaceSoft,
                  }}
                >
                  <div
                    style={{
                      width: "30px",
                      height: "30px",
                      flexShrink: 0,
                      display: "grid",
                      placeItems: "center",
                      borderRadius: "9px",
                      background: "rgba(59,130,246,.12)",
                      color: "#60a5fa",
                      fontSize: "11px",
                      fontWeight: 800,
                    }}
                  >
                    {number}
                  </div>

                  <div>
                    <div style={{ fontSize: "13px", fontWeight: 700 }}>
                      {title}
                    </div>
                    <div
                      style={{
                        marginTop: "3px",
                        color: "#64748b",
                        fontSize: "12px",
                        lineHeight: 1.5,
                      }}
                    >
                      {description}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section
          style={{
            borderRadius: "20px",
            background: theme.surface,
            border: `1px solid ${theme.border}`,
            padding: "22px",
            marginBottom: "20px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "22px",
            }}
          >
            <div>
              <div style={{ fontSize: "16px", fontWeight: 750 }}>
                Verification flow
              </div>
              <div
                style={{
                  marginTop: "4px",
                  color: "#64748b",
                  fontSize: "12px",
                }}
              >
                Every reasoning submission passes through the same pipeline.
              </div>
            </div>

            <div
              style={{
                color: verifying ? "#f59e0b" : "#64748b",
                fontSize: "12px",
                fontWeight: 700,
              }}
            >
              {verifying ? "PROCESSING" : "READY"}
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
              gap: "12px",
            }}
          >
            {steps.map((step, index) => {
              const isVerified = step.status === "verified";
              const isActive = step.status === "active";
              const isFailed = step.status === "failed";

              return (
                <React.Fragment key={step.id}>
                  <div
                    style={{
                      padding: "17px",
                      borderRadius: "15px",
                      background: isVerified
                        ? "rgba(34,197,94,.07)"
                        : isFailed
                        ? "rgba(239,68,68,.07)"
                        : isActive
                        ? "rgba(245,158,11,.07)"
                        : "rgba(30,41,59,.42)",
                      border: `1px solid ${
                        isVerified
                          ? "rgba(34,197,94,.2)"
                          : isFailed
                          ? "rgba(239,68,68,.2)"
                          : isActive
                          ? "rgba(245,158,11,.2)"
                          : "rgba(148,163,184,.1)"
                      }`,
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <span
                        style={{
                          width: "28px",
                          height: "28px",
                          display: "grid",
                          placeItems: "center",
                          borderRadius: "50%",
                          background: isVerified
                            ? "rgba(34,197,94,.14)"
                            : isFailed
                            ? "rgba(239,68,68,.14)"
                            : isActive
                            ? "rgba(245,158,11,.14)"
                            : "rgba(100,116,139,.12)",
                          color: isVerified
                            ? "#4ade80"
                            : isFailed
                            ? "#f87171"
                            : isActive
                            ? "#fbbf24"
                            : "#64748b",
                          fontSize: "12px",
                          fontWeight: 800,
                        }}
                      >
                        {isVerified ? String.fromCharCode(10003) : isFailed ? String.fromCharCode(10005) : step.id}
                      </span>

                      <span
                        style={{
                          fontSize: "10px",
                          color: isVerified
                            ? "#4ade80"
                            : isFailed
                            ? "#f87171"
                            : isActive
                            ? "#fbbf24"
                            : "#475569",
                          fontWeight: 750,
                          textTransform: "uppercase",
                        }}
                      >
                        {step.status}
                      </span>
                    </div>

                    <div
                      style={{
                        marginTop: "14px",
                        fontSize: "13px",
                        fontWeight: 750,
                      }}
                    >
                      {step.title}
                    </div>

                    <div
                      style={{
                        marginTop: "6px",
                        color: "#64748b",
                        fontSize: "11px",
                        lineHeight: 1.55,
                      }}
                    >
                      {step.description}
                    </div>
                  </div>

                  {index < steps.length - 1 && (
                    <div
                      style={{
                        display: "none",
                      }}
                    />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </section>

        {result && (
          <>
            <section
            style={{
              borderRadius: "20px",
              background: theme.surface,
              border: "1px solid rgba(34,197,94,.18)",
              padding: "22px",
              boxShadow: "0 18px 45px rgba(0,0,0,.18)",
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr auto",
                gap: "20px",
                alignItems: "center",
              }}
            >
              <div>
                <div
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "7px",
                    color: "#4ade80",
                    fontSize: "11px",
                    fontWeight: 800,
                    textTransform: "uppercase",
                    letterSpacing: ".08em",
                  }}
                >
                  <span>{String.fromCharCode(10003)}</span>
                  Verification result
                </div>

                <h2
                  style={{
                    margin: "9px 0 7px",
                    fontSize: "20px",
                  }}
                >
                  {result.title}
                </h2>

                <p
                  style={{
                    margin: 0,
                    maxWidth: "780px",
                    color: theme.muted,
                    fontSize: "13px",
                    lineHeight: 1.65,
                  }}
                >
                  {result.message}
                </p>

                {result.type === "verified" && (
                  <button
                    type="button"
                    onClick={startReconstruction}
                    style={{
                      marginTop: "16px",
                      border: "1px solid rgba(245,158,11,.28)",
                      background: "rgba(245,158,11,.09)",
                      color: "#fbbf24",
                      borderRadius: "11px",
                      padding: "11px 16px",
                      cursor: "pointer",
                      fontWeight: 750,
                    }}
                  >
                    Start Independent Reconstruction
                  </button>
                )}
              </div>

              <div
                style={{
                  width: "92px",
                  height: "92px",
                  borderRadius: "50%",
                  display: "grid",
                  placeItems: "center",
                  background: "rgba(34,197,94,.08)",
                  border: "1px solid rgba(34,197,94,.2)",
                }}
              >
                <div style={{ textAlign: "center" }}>
                  <div
                    style={{
                      fontSize: "25px",
                      fontWeight: 800,
                      color: "#4ade80",
                    }}
                  >
                    {result.score}%
                  </div>
                  <div
                    style={{
                      marginTop: "2px",
                      color: "#64748b",
                      fontSize: "9px",
                      fontWeight: 700,
                      textTransform: "uppercase",
                    }}
                  >
                    confidence
                  </div>
                </div>
              </div>
            </div>
          </section>

          {result.evidence && (
            <section
              style={{
                marginTop: "14px",
                borderRadius: "16px",
                background: theme.surfaceSoft,
                border: `1px solid ${theme.border}`,
                padding: "18px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "12px",
                  marginBottom: "10px",
                }}
              >
                <div
                  style={{
                    color: theme.text,
                    fontSize: "12px",
                    fontWeight: 800,
                    textTransform: "uppercase",
                    letterSpacing: ".08em",
                  }}
                >
                  Verification evidence
                </div>

                <span
                  style={{
                    padding: "4px 9px",
                    borderRadius: "999px",
                    background:
                      result.evidence.level === "high"
                        ? "rgba(34,197,94,.10)"
                        : "rgba(245,158,11,.10)",
                    color:
                      result.evidence.level === "high"
                        ? "#4ade80"
                        : "#fbbf24",
                    fontSize: "10px",
                    fontWeight: 800,
                    textTransform: "uppercase",
                  }}
                >
                  {result.evidence.level} confidence
                </span>
              </div>

              <div
                style={{
                  color: theme.text,
                  fontSize: "13px",
                  fontWeight: 700,
                  marginBottom: "6px",
                }}
              >
                {result.evidence.type.replaceAll("_", " ")}
              </div>

              <p
                style={{
                  margin: 0,
                  color: theme.muted,
                  fontSize: "12px",
                  lineHeight: 1.6,
                }}
              >
                {result.evidence.summary}
              </p>
            </section>
          )}
          </>
        )}
      {reconstructionOutcome && (
        <section
          style={{
            marginTop: "16px",
            marginBottom: "16px",
            padding: "18px 20px",
            borderRadius: "16px",
            background: "rgba(34,197,94,.08)",
            border: "1px solid rgba(34,197,94,.20)",
          }}
        >
          <div
            style={{
              color: "#4ade80",
              fontSize: "12px",
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: ".08em",
            }}
          >
            {String.fromCharCode(10003)} {reconstructionOutcome.title}
          </div>

          <div
            style={{
              marginTop: "8px",
              color: theme.text,
              fontSize: "13px",
              lineHeight: 1.6,
            }}
          >
            {reconstructionOutcome.message}
          </div>

          <div
            style={{
              marginTop: "8px",
              color: "#64748b",
              fontSize: "11px",
            }}
          >
            Reconstruction attempts: {reconstructionOutcome.attempts}
          </div>
        </section>
      )}
      {(nextLearningLoading || nextLearningStep) && (
        <section
          style={{
            marginTop: "16px",
            marginBottom: "16px",
            padding: "20px",
            borderRadius: "18px",
            background: theme.surface,
            border: "1px solid rgba(59,130,246,.20)",
            boxShadow: "0 16px 36px rgba(0,0,0,.12)",
          }}
        >
          <div
            style={{
              color: "#60a5fa",
              fontSize: "11px",
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: ".08em",
            }}
          >
            Adaptive Learning Decision
          </div>

          <h3
            style={{
              margin: "9px 0 8px",
              fontSize: "18px",
            }}
          >
            {nextLearningLoading
              ? "Selecting your next learning step..."
              : "Next Learning Step"}
          </h3>

          {!nextLearningLoading && (
            <>
              <p
                style={{
                  margin: 0,
                  color: theme.text,
                  fontSize: "13px",
                  lineHeight: 1.7,
                }}
              >
                {nextLearningStep}
              </p>

              {nextLearningAssessment && (
                <div
                  style={{
                    marginTop: "14px",
                    padding: "13px 15px",
                    borderRadius: "13px",
                    background: theme.surfaceSoft,
                    color: theme.muted,
                    fontSize: "12px",
                    lineHeight: 1.6,
                  }}
                >
                  <strong style={{ color: theme.text }}>
                    Next Assessment:
                  </strong>{" "}
                  {nextLearningAssessment}
                </div>
              )}
            </>
          )}
        </section>
      )}
      <section
        style={{
          marginTop: "16px",
          marginBottom: "16px",
          padding: "20px",
          borderRadius: "18px",
          background: theme.surface,
          border: `1px solid ${theme.border}`,
          boxShadow: "0 16px 36px rgba(0,0,0,.10)",
        }}
      >
        <div
          style={{
            color: "#a78bfa",
            fontSize: "11px",
            fontWeight: 800,
            textTransform: "uppercase",
            letterSpacing: ".08em",
          }}
        >
          Metacognitive Learning Evidence
        </div>

        <h3
          style={{
            margin: "9px 0 6px",
            fontSize: "18px",
          }}
        >
          Learning Control Status
        </h3>

        <p
          style={{
            margin: 0,
            color: theme.muted,
            fontSize: "12px",
            lineHeight: 1.6,
          }}
        >
          Evidence collected from verified reasoning, independent
          reconstruction, gate control, and adaptive progression.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
            gap: "12px",
            marginTop: "16px",
          }}
        >
          <div
            style={{
              padding: "14px",
              borderRadius: "14px",
              background: theme.surfaceSoft,
              border: `1px solid ${theme.border}`,
            }}
          >
            <div
              style={{
                color: "#64748b",
                fontSize: "10px",
                fontWeight: 800,
                textTransform: "uppercase",
              }}
            >
              Reasoning
            </div>
            <div
              style={{
                marginTop: "7px",
                color: result?.type === "verified" ? "#4ade80" : "#fbbf24",
                fontSize: "13px",
                fontWeight: 800,
              }}
            >
              {result?.type === "verified" ? "Verified" : "Pending"}
            </div>
          </div>

          <div
            style={{
              padding: "14px",
              borderRadius: "14px",
              background: theme.surfaceSoft,
              border: `1px solid ${theme.border}`,
            }}
          >
            <div
              style={{
                color: "#64748b",
                fontSize: "10px",
                fontWeight: 800,
                textTransform: "uppercase",
              }}
            >
              Reconstruction
            </div>
            <div
              style={{
                marginTop: "7px",
                color: reconstructionOutcome
                  ? "#4ade80"
                  : reconstructionGateOpen
                    ? "#fbbf24"
                    : "#64748b",
                fontSize: "13px",
                fontWeight: 800,
              }}
            >
              {reconstructionOutcome
                ? "Verified"
                : reconstructionGateOpen
                  ? "Required"
                  : "Not started"}
            </div>
          </div>

          <div
            style={{
              padding: "14px",
              borderRadius: "14px",
              background: theme.surfaceSoft,
              border: `1px solid ${theme.border}`,
            }}
          >
            <div
              style={{
                color: "#64748b",
                fontSize: "10px",
                fontWeight: 800,
                textTransform: "uppercase",
              }}
            >
              Attempts
            </div>
            <div
              style={{
                marginTop: "7px",
                color: theme.text,
                fontSize: "13px",
                fontWeight: 800,
              }}
            >
              {reconstructionOutcome?.attempts ?? reconstructionAttempts}
            </div>
          </div>

          <div
            style={{
              padding: "14px",
              borderRadius: "14px",
              background: theme.surfaceSoft,
              border: `1px solid ${theme.border}`,
            }}
          >
            <div
              style={{
                color: "#64748b",
                fontSize: "10px",
                fontWeight: 800,
                textTransform: "uppercase",
              }}
            >
              Progression
            </div>
            <div
              style={{
                marginTop: "7px",
                color: nextLearningStep ? "#4ade80" : "#fbbf24",
                fontSize: "13px",
                fontWeight: 800,
              }}
            >
              {nextLearningStep ? "Ready" : "Waiting"}
            </div>
          </div>
        </div>

        <div
          style={{
            marginTop: "14px",
            padding: "15px 16px",
            borderRadius: "14px",
            background: "rgba(167,139,250,.07)",
            border: "1px solid rgba(167,139,250,.16)",
          }}
        >
              <div
              style={{
                marginTop: "14px",
                padding: "15px 16px",
                borderRadius: "14px",
                background: theme.surfaceSoft,
                border: `1px solid ${theme.border}`,
              }}
            >
              <div
                style={{
                  color: "#a78bfa",
                  fontSize: "10px",
                  fontWeight: 800,
                  textTransform: "uppercase",
                  letterSpacing: ".06em",
                }}
              >
                Metacognitive Signals
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
                  gap: "10px",
                  marginTop: "11px",
                }}
              >
                <div>
                  <div
                    style={{
                      color: "#64748b",
                      fontSize: "10px",
                      fontWeight: 800,
                      textTransform: "uppercase",
                    }}
                  >
                    JOL
                  </div>
                  <div
                    style={{
                      marginTop: "5px",
                      fontSize: "13px",
                      fontWeight: 800,
                    }}
                  >
                    {jolPercent === null ? "Pending" : `${jolPercent}%`}
                  </div>
                </div>

                <div>
                  <div
                    style={{
                      color: "#64748b",
                      fontSize: "10px",
                      fontWeight: 800,
                      textTransform: "uppercase",
                    }}
                  >
                    Independent
                  </div>
                  <div
                    style={{
                      marginTop: "5px",
                      fontSize: "13px",
                      fontWeight: 800,
                    }}
                  >
                    {reconstructionOutcome ? "100%" : "Pending"}
                  </div>
                </div>

                <div>
                  <div
                    style={{
                      color: "#64748b",
                      fontSize: "10px",
                      fontWeight: 800,
                      textTransform: "uppercase",
                    }}
                  >
                    Calibration
                  </div>
                  <div
                    style={{
                      marginTop: "5px",
                      fontSize: "13px",
                      fontWeight: 800,
                      color:
                        metacognitiveCalibration?.status === "overconfident"
                          ? "#fbbf24"
                          : metacognitiveCalibration?.status ===
                              "underconfident"
                            ? "#60a5fa"
                            : metacognitiveCalibration?.status ===
                                "well_calibrated"
                              ? "#4ade80"
                              : theme.text,
                    }}
                  >
                    {metacognitiveCalibration?.status
                      ? metacognitiveCalibration.status.replace("_", " ")
                      : "Pending"}
                  </div>
                </div>

                <div>
                  <div
                    style={{
                      color: "#64748b",
                      fontSize: "10px",
                      fontWeight: 800,
                      textTransform: "uppercase",
                    }}
                  >
                    Hint dependency
                  </div>
                  <div
                    style={{
                      marginTop: "5px",
                      fontSize: "13px",
                      fontWeight: 800,
                    }}
                  >
                    {hintDependencyState
                      ? `${hintDependencyState.consecutive_hint_attempts} consecutive`
                      : "Pending"}
                  </div>
                </div>
              </div>

              <div
                style={{
                  marginTop: "11px",
                  padding: "9px 11px",
                  borderRadius: "10px",
                  background: "rgba(15,23,42,.05)",
                  fontSize: "11px",
                  color: theme.muted,
                }}
              >
                Calibration gap:{" "}
                {metacognitiveCalibration?.calibration_gap == null
                  ? "Pending"
                  : `${metacognitiveCalibration.calibration_gap > 0 ? "+" : ""}${Math.round(
                      metacognitiveCalibration.calibration_gap * 100
                    )}%`}
                {" · "}
                Alert:{" "}
                {metacognitiveCalibration?.miscalibration_alert ||
                hintDependencyState?.hint_dependency_alert
                  ? "Review required"
                  : metacognitiveCalibration || hintDependencyState
                    ? "No alert"
                    : "Pending"}
              </div>
            </div>

        <div
            style={{
              color: "#a78bfa",
              fontSize: "10px",
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: ".06em",
            }}
          >
            Evidence Chain
          </div>

          <div
            style={{
              marginTop: "9px",
              display: "grid",
              gap: "7px",
              color: theme.muted,
              fontSize: "12px",
              lineHeight: 1.5,
            }}
          >
            <div>
              {String.fromCharCode(10003)} Verified reasoning established.
            </div>
            <div>
              {reconstructionOutcome
                ? `${String.fromCharCode(10003)} Independent reconstruction verified.`
                : reconstructionGateOpen
                  ? "� Independent reconstruction required."
                  : String.fromCharCode(8226) + " Independent reconstruction not started."}
            </div>
            <div>
              {nextLearningStep
                ? `${String.fromCharCode(10003)} Adaptive progression selected.`
                : String.fromCharCode(8226) + " Adaptive progression pending."}
            </div>
          </div>
        </div>
      </section>
      <ReconstructionGate
        isOpen={reconstructionGateOpen}
        isLightMode={isLightMode}
        topic={reconstructionTopic}
        prompt={reconstructionPrompt}
        attempts={reconstructionAttempts}
        hint={reconstructionHint}
        submitting={reconstructionSubmitting}
        onSubmit={submitReconstruction}
      />
    </div>
    </div>
  );
}














