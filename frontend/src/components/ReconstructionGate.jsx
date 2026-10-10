import React, { useState } from "react";

export default function ReconstructionGate({
  isOpen,
  isLightMode = false,
  topic = "Current topic",
  prompt = "Reconstruct the reasoning in your own words before continuing.",
  attempts = 0,
  hint = "",
  submitting = false,
  onSubmit,
}) {
  const [response, setResponse] = useState("");

  if (!isOpen) return null;

  const theme = isLightMode
    ? {
        overlay: "rgba(15, 23, 42, 0.42)",
        panel: "#ffffff",
        text: "#0f172a",
        muted: "#64748b",
        border: "rgba(15, 23, 42, 0.10)",
        input: "#f8fafc",
      }
    : {
        overlay: "rgba(2, 6, 23, 0.72)",
        panel: "rgba(15, 23, 42, 0.96)",
        text: "#f8fafc",
        muted: "#94a3b8",
        border: "rgba(148, 163, 184, 0.16)",
        input: "#07101e",
      };

  const handleSubmit = () => {
    if (!response.trim() || submitting) return;

    onSubmit?.(response.trim());
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="reconstruction-gate-title"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        display: "grid",
        placeItems: "center",
        padding: "24px",
        background: theme.overlay,
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
      }}
    >
      <div
        style={{
          width: "min(680px, 100%)",
          maxHeight: "90vh",
          overflowY: "auto",
          borderRadius: "24px",
          background: theme.panel,
          border: `1px solid ${theme.border}`,
          boxShadow: "0 30px 90px rgba(0,0,0,.38)",
          padding: "28px",
          color: theme.text,
        }}
      >
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "7px 12px",
            borderRadius: "999px",
            background: "rgba(245,158,11,.10)",
            border: "1px solid rgba(245,158,11,.20)",
            color: "#fbbf24",
            fontSize: "11px",
            fontWeight: 800,
            letterSpacing: ".08em",
            textTransform: "uppercase",
          }}
        >
          <span>?</span>
          Active Reconstruction Required
        </div>

        <h2
          id="reconstruction-gate-title"
          style={{
            margin: "18px 0 8px",
            fontSize: "25px",
            lineHeight: 1.2,
            fontWeight: 800,
            letterSpacing: "-.02em",
          }}
        >
          Reconstruct it without AI assistance
        </h2>

        <p
          style={{
            margin: 0,
            color: theme.muted,
            fontSize: "13px",
            lineHeight: 1.7,
          }}
        >
          Your learning state requires an independent reconstruction before
          the next step is unlocked.
        </p>

        <div
          style={{
            marginTop: "20px",
            padding: "16px",
            borderRadius: "16px",
            background: "rgba(59,130,246,.07)",
            border: "1px solid rgba(59,130,246,.16)",
          }}
        >
          <div
            style={{
              color: "#60a5fa",
              fontSize: "10px",
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: ".08em",
            }}
          >
            Topic
          </div>

          <div
            style={{
              marginTop: "6px",
              fontSize: "14px",
              fontWeight: 700,
            }}
          >
            {topic}
          </div>
        </div>

        <div style={{ marginTop: "18px" }}>
          <div
            style={{
              fontSize: "12px",
              fontWeight: 800,
              textTransform: "uppercase",
              letterSpacing: ".06em",
            }}
          >
            Reconstruction prompt
          </div>

          <div
            style={{
              marginTop: "8px",
              padding: "17px",
              borderRadius: "15px",
              background: theme.input,
              border: `1px solid ${theme.border}`,
              color: theme.text,
              fontSize: "14px",
              lineHeight: 1.7,
            }}
          >
            {prompt}
          </div>
        </div>

        <div style={{ marginTop: "18px" }}>
          <textarea
            value={response}
            onChange={(event) => setResponse(event.target.value)}
            disabled={submitting}
            placeholder="Explain the reasoning in your own words..."
            style={{
              width: "100%",
              minHeight: "150px",
              boxSizing: "border-box",
              resize: "vertical",
              padding: "15px",
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
        </div>

        {hint && (
          <div
            style={{
              marginTop: "14px",
              padding: "14px 16px",
              borderRadius: "14px",
              background: "rgba(245,158,11,.07)",
              border: "1px solid rgba(245,158,11,.16)",
              color: theme.muted,
              fontSize: "12px",
              lineHeight: 1.6,
            }}
          >
            <strong style={{ color: "#fbbf24" }}>Socratic hint: </strong>
            {hint}
          </div>
        )}

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "12px",
            marginTop: "18px",
          }}
        >
          <div
            style={{
              color: theme.muted,
              fontSize: "11px",
            }}
          >
            Attempts: {attempts}
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!response.trim() || submitting}
            style={{
              border: "none",
              borderRadius: "11px",
              padding: "12px 20px",
              background:
                !response.trim() || submitting
                  ? "#334155"
                  : "linear-gradient(135deg, #2563eb, #4f46e5)",
              color: "#fff",
              cursor:
                !response.trim() || submitting ? "not-allowed" : "pointer",
              fontWeight: 750,
            }}
          >
            {submitting ? "Checking..." : "Check Reconstruction"}
          </button>
        </div>
      </div>
    </div>
  );
}
