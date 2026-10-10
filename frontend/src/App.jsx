import { useState, useRef, useEffect } from "react";
import { supabase } from "./supabaseClient";
import "./App.css";
import LandingPage from "./LandingPage";
import VerifiedReasoningPage from "./pages/VerifiedReasoningPage";
import SyntheticPeerClassroomPage from "./pages/SyntheticPeerClassroomPage";

const menuItems = [
  { id: "overview", label: "Overview", icon: "ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â‚¬Å¾Ã‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¡" },
  { id: "guide", label: "AI Subject Guide", icon: "ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¦" },
  { id: "virtual-teacher", label: "Virtual Teacher", icon: "VT" },
  { id: "documents", label: "Documents", icon: "ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã¢â‚¬Å“ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â£" },
  { id: "questions", label: "Question Bank", icon: "ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¹ÃƒÆ’Ã¢â‚¬Â¦ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â·" },
  { id: "pyq", label: "PYQ Analysis", icon: "ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚ÂÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¹ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â " },
  { id: "quiz", label: "Quiz", icon: "?" },
  { id: "exam", label: "Exam Mode", icon: "ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚ÂÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â°" },
  { id: "planner", label: "Study Planner", icon: "ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚ÂÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â«" },
  { id: "verified-reasoning", label: "Verified Reasoning", icon: "VR" },
  { id: "synthetic-peer", label: "Synthetic Peer Classroom", icon: "F3" },
];

function Overview({ setActivePage }) {
  return (
    <>
      <section className="hero-panel">
        <div className="hero-copy">
          <div className="eyebrow">AI KNOWLEDGE CORE</div>

          <h1>
            Learn from 
            <hr/>
            your own knowledge.
          </h1>

          <p>
            Turn your notes, textbooks and previous-year questions into an
            intelligent study system.
          </p>

          <div className="hero-actions">
            <button
              className="primary-button"
              onClick={() => setActivePage("guide")}
            >
              Open AI Teacher <span></span>
            </button>

            <button
              className="secondary-button"
              onClick={() => setActivePage("documents")}
            >
              Upload Material
            </button>
          </div>
        </div>

        <div className="knowledge-core">
          <div className="core-ring ring-one" />
          <div className="core-ring ring-two" />
          <div className="core-ring ring-three" />

          <div className="core-center">
            <span>AI</span>
          </div>

          <div className="core-label label-one">RETRIEVE</div>
          <div className="core-label label-two">REASON</div>
          <div className="core-label label-three">GROUND</div>
          <div className="core-label label-four">CITE</div>
        </div>
      </section>

      <section className="metrics-grid">
        <Metric value="06" label="DOCUMENTS" />
        <Metric value="128" label="QUESTIONS" />
        <Metric value="24" label="TOPICS" />
        <Metric value="98%" label="GROUNDING" />
      </section>

      <section className="workspace-grid">
        <div className="workspace-card rag-card">
          <div className="card-top">
            <span className="eyebrow">RAG INTELLIGENCE</span>
            <span className="live-dot">LIVE</span>
          </div>

          <h2>How Subject Guide AI thinks</h2>

<p className="muted">
  Your question moves through a grounded learning pipeline before
  the answer reaches you.
</p>

<div className="pipeline">
  <PipelineStep number="01" title="QUESTION" />
  <span className="pipeline-arrow">Ã¢â€ â€™</span>

  <PipelineStep number="02" title="RETRIEVE" />
  <span className="pipeline-arrow">Ã¢â€ â€™</span>

  <PipelineStep number="03" title="GENERATE" />
  <span className="pipeline-arrow">Ã¢â€ â€™</span>

  <PipelineStep number="04" title="CITE" />
</div>

<div className="grounding-box">
  <div className="grounding-icon">G</div>

  <div>
    <strong>Grounding verification</strong>
    <span>
      Answers are checked against retrieved study material.
    </span>
  </div>
</div>
</div>
        <div className="workspace-card study-card">
          <div className="card-top">
            <span className="eyebrow">CONTINUE LEARNING</span>
            <span className="progress-label">72%</span>
          </div>

          <h2>Database Management</h2>
          <p className="muted">Normalization</p>

          <div className="progress-track">
            <div className="progress-fill" style={{ width: "72%" }} />
          </div>

          <button
            className="secondary-button full-button"
            onClick={() => setActivePage("guide")}
          >
            Continue topic
          </button>
        </div>
           </section>

      <section
        className="workspace-card"
        style={{
          marginTop: "24px",
          padding: "28px",
          overflow: "hidden",
        }}
      >
        <div className="card-top">
          <span className="eyebrow">AI TEACHING VIDEO</span>
          <span className="live-dot">READY</span>
        </div>

        <h2>Binary Search Ã¢â‚¬â€ AI Lesson</h2>

        <p className="muted">
          Watch the generated 2D educational lesson with AI teacher narration.
        </p>

        <div
          style={{
            marginTop: "22px",
            borderRadius: "18px",
            overflow: "hidden",
            background: "#05070b",
            border: "1px solid rgba(255,255,255,0.08)",
          }}
        >
          <video
            controls
            preload="metadata"
            style={{
              width: "100%",
              display: "block",
              maxHeight: "620px",
              background: "#05070b",
            }}
            src="http://127.0.0.1:8000/api/v1/teaching-video/video/binary_search_2d_full.mp4"
          >
            Your browser does not support video playback.
          </video>
        </div>

        <div
          style={{
            marginTop: "16px",
            display: "flex",
            gap: "10px",
            flexWrap: "wrap",
          }}
        >
          <span className="question-type">2D ANIMATION</span>
          <span className="question-type">GEMINI AI VOICE</span>
          <span className="question-type">GROUNDED LEARNING</span>
        </div>
      </section>
    </>
  );
}

function Metric({ value, label }) {
  return (
    <div className="metric-card">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function PipelineStep({ number, title }) {
  return (
    <div className="pipeline-step">
      <small>{number}</small>
      <span>{title}</span>
    </div>
  );
}

function GuidePage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askAI = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");
    setCitations([]);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/question", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
          top_k: 3,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      setAnswer(data.answer);
      setCitations(data.citations || []);
    } catch (err) {
      setError("Unable to connect to the AI backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageShell
      eyebrow="AI SUBJECT GUIDE"
      title="Your AI Teacher"
      description="Ask questions from your study material and receive grounded answers with source context."
    >
      <div className="guide-workspace">

        {/* CHAT AREA */}
        <div className="guide-chat-panel">

          <div className="guide-chat-header">
            <div>
              <span className="eyebrow">AI TEACHER</span>
              <h3>Ask from your knowledge</h3>
            </div>

            <div className="guide-live-status">
              <span className="status-dot" />
              GROUNDED
            </div>
          </div>

          <div className="guide-response-area">

            {!loading && !answer && !error && (
              <div className="guide-empty-state">
                <div className="guide-ai-orb">
                  <span>AI</span>
                </div>

                <h3>What would you like to learn?</h3>

                <p>
                  Ask a question from your uploaded study material.
                  The AI will retrieve relevant content before answering.
                </p>

                <div className="guide-suggestions">
                  <button
                    onClick={() => setQuestion("What is C?")}
                  >
                    What is C?
                  </button>

                  <button
                    onClick={() => setQuestion("What are pointers?")}
                  >
                    What are pointers?
                  </button>

                  <button
                    onClick={() => setQuestion("Explain loops")}
                  >
                    Explain loops
                  </button>
                </div>
              </div>
            )}

            {loading && (
              <div className="guide-loading">
                <div className="loading-orb">
                  <span>AI</span>
                </div>

                <div>
                  <strong>Thinking...</strong>
                  <p>
                    Retrieving relevant study material and generating a
                    grounded answer.
                  </p>
                </div>
              </div>
            )}

            {!loading && answer && (
              <div className="guide-answer">

                <div className="answer-label">
                  <span className="status-dot" />
                  AI TEACHER
                </div>

                <p>{answer}</p>

                {citations.length > 0 && (
                  <div className="citation-section">
                    <div className="citation-heading">
                      SOURCE CONTEXT
                    </div>

                    <div className="citation-list">
                      {citations.map((citation, index) => (
                        <div className="citation-item" key={index}>
                          <span>SOURCE</span>
                          <strong>{citation.source}</strong>
                          <span>PAGE {citation.page_number}</span>
                          <span>CHUNK {citation.chunk_index}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {error && (
              <div className="guide-error">
                {error}
              </div>
            )}
          </div>

          {/* INPUT */}
          <div className="guide-input-area">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !loading) {
                  askAI();
                }
              }}
              placeholder="Ask your AI Teacher..."
              disabled={loading}
            />

            <button
              className="primary-button"
              onClick={askAI}
              disabled={loading || !question.trim()}
            >
              {loading ? "Thinking..." : "Ask AI Ã¢â€ â€™"}
            </button>
          </div>

        </div>

        {/* SIDE INFORMATION */}
        <div className="guide-side-panel">

          <div className="feature-card">
            <span className="eyebrow">INTELLIGENCE</span>

            <h3>Grounded answers</h3>

            <p>
              The AI retrieves relevant study material before generating
              the answer.
            </p>
          </div>

          <div className="feature-card">
            <span className="eyebrow">SOURCE CONTROL</span>

            <h3>Traceable learning</h3>

            <p>
              Every retrieved answer can show its source, page and
              document chunk.
            </p>
          </div>

          <div className="feature-card">
            <span className="eyebrow">RAG PIPELINE</span>

            <h3>Retrieve Generate  Cite</h3>

            <p>
              Your question passes through the retrieval pipeline before
              the AI produces the final response.
            </p>
          </div>

        </div>

      </div>
    </PageShell>
  );
}
function DocumentsPage() {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const documents = [
    {
      name: "Database Management Notes.pdf",
      type: "NOTES",
      pages: "48 pages",
      status: "READY",
    },
    {
      name: "DBMS Previous Year Questions.pdf",
      type: "PYQ",
      pages: "32 pages",
      status: "READY",
    },
    {
      name: "Machine Learning Unit 1.pdf",
      type: "NOTES",
      pages: "26 pages",
      status: "READY",
    },
  ];

 const handleFileSelect = async (event) => {
  const file = event.target.files?.[0];

  if (!file) return;

  setSelectedFile(file);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/documents/upload",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Upload failed");
    }

    console.log("PDF uploaded successfully:", data);
  } catch (error) {
    console.error("PDF upload failed:", error);
    alert("PDF upload failed. Make sure the backend is running.");
  }
};

  return (
    <PageShell
      eyebrow="DOCUMENT INTELLIGENCE"
      title="Your Knowledge Base"
      description="Manage the notes, textbooks and previous-year papers used by the AI learning system."
    >
      <div className="documents-workspace">

        {/* UPLOAD AREA */}
        <div className="document-upload-card">
          <div className="upload-glow">
            <span>+</span>
          </div>

          <div className="upload-content">
            <span className="eyebrow">KNOWLEDGE INGESTION</span>

            <h2>Upload study material</h2>

            <p>
              Add notes, textbooks and previous-year questions to build
              your searchable AI knowledge base.
            </p>

            <button
              className="primary-button"
              onClick={() => fileInputRef.current?.click()}
            >
              Choose PDF
            </button>

            {selectedFile && (
  <div className="selected-file">
    <span>SELECTED</span>
    <strong>{selectedFile.name}</strong>
  </div>
)}

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            style={{ display: "none" }}
            onChange={handleFileSelect}
          />

            <span className="upload-hint">
              PDF ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· MAX 20 MB
            </span>
          </div>



          <div className="upload-pipeline">
            <span>UPLOAD</span>
            <i></i>
            <span>PROCESS</span>
            <i></i>
            <span>INDEX</span>
            <i></i>
            <span>AI READY</span>
          </div>
        </div>

        {/* DOCUMENT HEADER */}
        <div className="documents-header">
          <div>
            <span className="eyebrow">KNOWLEDGE BASE</span>
            <h3>Study material</h3>
          </div>

          <div className="document-count">
            {documents.length} DOCUMENTS
          </div>
        </div>

        {/* DOCUMENT LIST */}
        <div className="document-list">
          {documents.map((document, index) => (
            <div className="document-card" key={index}>

              <div className="document-file-icon">
                PDF
              </div>

              <div className="document-info">
                <strong>{document.name}</strong>

                <div className="document-meta">
                  <span>{document.type}</span>
                  <span>{document.pages}</span>
                  <span>Indexed</span>
                </div>
              </div>

              <div className="document-status">
                <span className="status-dot" />
                {document.status}
              </div>

              <button className="document-action">
                <span>OPEN</span>
              </button>

            </div>
          ))}
        </div>

      </div>
    </PageShell>
  );
}

function DocumentRow({ name, pages }) {
  return (
    <div className="document-row">
      <div>
        <strong>{name}</strong>
        <span>{pages} Indexed for retrieval</span>
      </div>
      <span className="document-status">READY</span>
    </div>
  );
}

function QuestionsPage() {
  const [topic, setTopic] = useState("");
  const [questionCount, setQuestionCount] = useState(5);
  const [difficulty, setDifficulty] = useState("mixed");
  const [questionType, setQuestionType] = useState("mixed");
  const [studyText, setStudyText] = useState("");
  const [currentKnowledge, setCurrentKnowledge] = useState("");
  const [teacherQuestion, setTeacherQuestion] = useState("");
  const [voiceTeacherScript, setVoiceTeacherScript] =
  useState("");
  const [voiceTeacherAudio, setVoiceTeacherAudio] =
  useState("");
  const [voiceTeacherLoading, setVoiceTeacherLoading] =
  useState(false);
  const [studentLevel, setStudentLevel] = useState("");
  const [teacherAnswer, setTeacherAnswer] = useState("");
  const [teacherLoading, setTeacherLoading] = useState(false);
  const [visualLearning, setVisualLearning] = useState("");
  const [visualLearningLoading, setVisualLearningLoading] = useState(false);
  const [visualContent, setVisualContent] = useState("");
  const [visualContentLoading, setVisualContentLoading] = useState(false);
  const [whiteboard, setWhiteboard] = useState("");
  const [whiteboardLoading, setWhiteboardLoading] = useState(false);
  const [videoPlan, setVideoPlan] = useState("");
  const [videoFile, setVideoFile] = useState("");
  const [videoPlanLoading, setVideoPlanLoading] = useState(false);
  const [videoElapsedSeconds, setVideoElapsedSeconds] = useState(0);

  useEffect(() => {
    if (!videoPlanLoading) {
      setVideoElapsedSeconds(0);
      return;
    }

    const startedAt = Date.now();
    const timer = setInterval(() => {
      setVideoElapsedSeconds(
        Math.floor((Date.now() - startedAt) / 1000)
      );
    }, 1000);

    return () => clearInterval(timer);
  }, [videoPlanLoading]);
  const [questionBank, setQuestionBank] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [practiceMode, setPracticeMode] = useState(false);
  const [studentAnswers, setStudentAnswers] = useState("");
  const [assessmentReport, setAssessmentReport] = useState("");
  const [assessmentLoading, setAssessmentLoading] = useState(false);
  const [adaptiveReport, setAdaptiveReport] = useState("");
  const [adaptiveLoading, setAdaptiveLoading] = useState(false);
  const [studyGuide, setStudyGuide] = useState("");
  const [studyGuideLoading, setStudyGuideLoading] = useState(false);
  const [prerequisiteReport, setPrerequisiteReport] = useState("");
  const [prerequisiteLoading, setPrerequisiteLoading] = useState(false);




  async function generateQuestions() {
    if (!topic.trim()) {
      setMessage("Enter a topic first.");
      return;
    }

    setLoading(true);
    setMessage("");
    setQuestionBank("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/question-bank",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: topic.trim(),
            question_count: Number(questionCount),
            difficulty,
            question_type: questionType,
            study_text: studyText.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to generate question bank."
        );
      }

      setQuestionBank(data.question_bank || "");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

async function submitAssessment() {
  if (!studentAnswers.trim()) {
    setMessage("Enter your answers first.");
    return;
  }

  setAssessmentLoading(true);
  setMessage("");
  setAssessmentReport("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/assessment",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.trim(),
          question_bank: questionBank,
          student_answers: studentAnswers.trim(),
          study_text: studyText.trim(),
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to assess your answers."
      );
    }

    setAssessmentReport(data.assessment_report || "");
  } catch (error) {
    setMessage(error.message);
  } finally {
    setAssessmentLoading(false);
  }
}

async function generateAdaptiveLearning() {
  if (!assessmentReport.trim()) {
    setMessage("Complete the assessment first.");
    return;
  }

  setAdaptiveLoading(true);
  setMessage("");
  setAdaptiveReport("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/adaptive-learning",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.trim(),
          assessment_report: assessmentReport,
          current_knowledge: "",
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail ||
          "Failed to generate adaptive learning plan."
      );
    }

    setAdaptiveReport(
      data.adaptive_learning_report || ""
    );
  } catch (error) {
    setMessage(error.message);
  } finally {
    setAdaptiveLoading(false);
  }
}

async function generateStudyGuide() {
  if (!adaptiveReport.trim()) {
    setMessage("Generate the adaptive learning plan first.");
    return;
  }

  setStudyGuideLoading(true);
  setMessage("");
  setStudyGuide("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/study-guide",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.trim(),
          context: studyText.trim(),
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to generate study guide."
      );
    }

    setStudyGuide(
  data.study_guide ||
  "Study Guide response was received, but no study guide content was returned."
);
  } catch (error) {
    setMessage(error.message);
  } finally {
    setStudyGuideLoading(false);
  }
}

async function generatePrerequisites() {
  if (!topic.trim()) {
    setMessage("Enter a topic first.");
    return;
  }

  setPrerequisiteLoading(true);
  setMessage("");
  setPrerequisiteReport("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/prerequisite",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          goal: topic.trim(),
          current_knowledge: currentKnowledge.trim(),
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to analyze prerequisites."
      );
    }

    setPrerequisiteReport(
      data.prerequisites ||
      "Prerequisite analysis was received, but no content was returned."
    );
  } catch (error) {
    setMessage(error.message);
  } finally {
    setPrerequisiteLoading(false);
  }
}

async function generateVoiceTeacher() {
  const voiceTopic = topic.trim();

  if (!voiceTopic) {
    setMessage("Enter a topic first.");
    return;
  }

  setVoiceTeacherLoading(true);
  setMessage("");
  setVoiceTeacherScript("");
  setVoiceTeacherAudio("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/voice-teacher",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: voiceTopic,
          student_level: studentLevel.trim(),
          learning_goal: teacherQuestion.trim(),
          lesson_context:
            whiteboard.trim() ||
            visualLearning.trim(),
          study_text: studyText.trim(),
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to generate Voice Teacher content."
      );
    }

    setVoiceTeacherScript(
      data.voice_script ||
      "Voice Teacher response was received, but no script was returned."
    );

    if (data.audio_file) {
      setVoiceTeacherAudio(
        `http://127.0.0.1:8000${data.audio_file}`
      );
    }
  } catch (error) {
    setMessage(error.message);
  } finally {
    setVoiceTeacherLoading(false);
  }
}

async function askAITeacher() {
  if (!teacherQuestion.trim()) {
    setMessage("Enter a question for the AI Teacher.");
    return;
  }

  setTeacherLoading(true);
  setMessage("");
  setTeacherAnswer("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/teacher",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: teacherQuestion.trim(),
          lesson_context: studyText.trim(),
          student_level: studentLevel.trim(),
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to get AI Teacher response."
      );
    }

    setTeacherAnswer(
      data.answer ||
      "AI Teacher response was received, but no answer was returned."
    );
  } catch (error) {
    setMessage(error.message);
  } finally {
    setTeacherLoading(false);
  }
}

async function generateVisualLearning() {
  if (!topic.trim()) {
    setMessage("Enter a topic first.");
    return;
  }

  setVisualLearningLoading(true);
  setMessage("");
  setVisualLearning("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/visual-learning",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.trim(),
          student_level: studentLevel.trim(),
          learning_goal: teacherQuestion.trim(),
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to generate visual learning content."
      );
    }

    setVisualLearning(
      data.visual_learning ||
      "Visual Learning response was received, but no content was returned."
    );
  } catch (error) {
    setMessage(error.message);
  } finally {
    setVisualLearningLoading(false);
  }
}

async function generateVisualContent() {
  if (!topic.trim()) {
    setMessage("Enter a topic first.");
    return;
  }

  if (!visualLearning.trim()) {
    setMessage("Generate Visual Learning first.");
    return;
  }

  setVisualContentLoading(true);
  setMessage("");
  setVisualContent("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/visual-content",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.trim(),
          visual_learning_spec: visualLearning.trim(),
          student_level: studentLevel.trim(),
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to generate visual content."
      );
    }

    setVisualContent(
      data.visual_content ||
      "Visual Content response was received, but no content was returned."
    );
  } catch (error) {
    setMessage(error.message);
  } finally {
    setVisualContentLoading(false);
  }
}

async function generateWhiteboard() {
  if (!topic.trim()) {
    setMessage("Enter a topic first.");
    return;
  }

  setWhiteboardLoading(true);
  setMessage("");
  setWhiteboard("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/whiteboard",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.trim(),
          student_level: studentLevel.trim(),
          lesson_context: visualLearning.trim(),
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to generate AI Whiteboard content."
      );
    }

    setWhiteboard(
      data.whiteboard ||
      "AI Whiteboard response was received, but no content was returned."
    );
  } catch (error) {
    setMessage(error.message);
  } finally {
    setWhiteboardLoading(false);
  }
}

async function generateTeachingVideo() {
  const videoTopic = topic.trim();

  if (!videoTopic) {
    setMessage("Enter a topic first.");
    return;
  }

  setVideoPlanLoading(true);
  setMessage("");
  setVideoPlan("");
  setVideoFile("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/teaching-video",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: videoTopic,
          student_level: studentLevel.trim(),
          lesson_context:
            whiteboard.trim() || visualLearning.trim(),
          learning_goal: teacherQuestion.trim(),
          study_text: studyText.trim(),
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to generate teaching video."
      );
    }

    setVideoPlan(
      data.video_plan ||
      "Teaching Video plan was generated, but no plan was returned."
    );

    if (data.video_file) {
      setVideoFile(
        `http://127.0.0.1:8000${data.video_file}?t=${Date.now()}`
      );
    } else {
      setMessage(
        "Teaching plan was generated, but the backend did not return a video file."
      );
    }

  } catch (error) {
    setMessage(error.message);
  } finally {
    setVideoPlanLoading(false);
  }
}
  function renderQuestionBank(text) {
    if (!text.trim()) {
      return null;
    }

    const blocks = text
      .split(/\n\s*(?=\d+\.\s*(?:Question|Q))/i)
      .map((block) => block.trim())
      .filter(Boolean);

    return blocks.map((block, index) => (
      <div className="generated-question" key={index}>
        <div className="generated-question-number">
          Q{index + 1}
        </div>

        <div className="generated-question-content">
          <pre>{block}</pre>
        </div>
      </div>
    ));
  }

  return (
    <PageShell
      eyebrow="QUESTION BANK AGENT"
      title="Practice with purpose."
      description="Generate grounded questions from your study material."
    >
      <div className="question-grid">
        <div className="question-card">
          <h3>Question Bank Generator</h3>

          <label>
            <span>Topic</span>
            <input
              type="text"
              placeholder="Example: Binary Search Tree"
              value={topic}
              onChange={(event) => setTopic(event.target.value)}
            />
          </label>

          <label>
            <span>Number of Questions</span>
            <select
              value={questionCount}
              onChange={(event) =>
                setQuestionCount(event.target.value)
              }
            >
              <option value="1">1</option>
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="15">15</option>
              <option value="20">20</option>
            </select>
          </label>

          <label>
            <span>Difficulty</span>
            <select
              value={difficulty}
              onChange={(event) =>
                setDifficulty(event.target.value)
              }
            >
              <option value="mixed">Mixed</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="difficult">Difficult</option>
            </select>
          </label>

          <label>
            <span>Question Type</span>
            <select
              value={questionType}
              onChange={(event) =>
                setQuestionType(event.target.value)
              }
            >
              <option value="mixed">Mixed</option>
              <option value="MCQ">MCQ</option>
              <option value="Short Answer">Short Answer</option>
              <option value="True/False">True/False</option>
              <option value="Fill in the Blank">
                Fill in the Blank
              </option>
            </select>
          </label>

          <label>
  <span>Current Knowledge (Optional)</span>
  <textarea
    placeholder="Example: I know basic Python, arrays, and sorting..."
    value={currentKnowledge}
    onChange={(event) =>
      setCurrentKnowledge(event.target.value)
    }
    rows={4}
  />
</label>
          <label>
            <span>Study Material (Optional)</span>
            <textarea
              placeholder="Paste your study material here..."
              value={studyText}
              onChange={(event) =>
                setStudyText(event.target.value)
              }
              rows={6}
            />
          </label>

          <button
            type="button"
            className="login-submit"
            onClick={generateQuestions}
            disabled={loading}
          >
            <span>
              {loading
                ? "GENERATING..."
                : "GENERATE QUESTION BANK"}
            </span>
            <b>&gt;</b>
          </button>
          
          <button
  type="button"
  className="login-submit"
  onClick={generatePrerequisites}
  disabled={prerequisiteLoading}
>
  <span>
    {prerequisiteLoading
      ? "ANALYZING PREREQUISITES..."
      : "ANALYZE PREREQUISITES"}
  </span>
  <b>&gt;</b>
</button>

{prerequisiteReport && (
  <div className="adaptive-result">
    <h3>Prerequisite Analysis</h3>
    <pre>{prerequisiteReport}</pre>
  </div>
)}

<div className="adaptive-result">
  <h3>AI Teacher</h3>

  <textarea
    value={teacherQuestion}
    onChange={(event) => setTeacherQuestion(event.target.value)}
    placeholder="Ask the AI Teacher a question..."
    rows={4}
  />

  <input
    type="text"
    value={studentLevel}
    onChange={(event) => setStudentLevel(event.target.value)}
    placeholder="Student level (e.g. Beginner, Intermediate)"
  />

  <button
    type="button"
    onClick={askAITeacher}
    disabled={teacherLoading}
  >
    {teacherLoading ? "TEACHER IS THINKING..." : "ASK AI TEACHER"}
  </button>

  {teacherAnswer && (
    <pre>{teacherAnswer}</pre>
  )}
</div>

<div className="agent-card">
  <h3>Voice Teacher</h3>

  <p>
    Generate a grounded teaching script and hear it as AI voice narration.
  </p>

  <button
    onClick={generateVoiceTeacher}
    disabled={voiceTeacherLoading}
  >
    {voiceTeacherLoading
      ? "GENERATING VOICE TEACHER..."
      : "START VOICE TEACHER"}
  </button>

  {voiceTeacherScript && (
    <div className="adaptive-result">
      <h3>Voice Teacher Script</h3>

      <pre>{voiceTeacherScript}</pre>
    </div>
  )}

  {voiceTeacherAudio && (
    <div className="adaptive-result">
      <h3>Teacher Voice</h3>

      <audio
        controls
        src={voiceTeacherAudio}
        style={{ width: "100%" }}
      >
        Your browser does not support audio playback.
      </audio>
    </div>
  )}
</div>

<div className="adaptive-result">
  <h3>Visual Learning</h3>

  <button
    type="button"
    onClick={generateVisualLearning}
    disabled={visualLearningLoading}
  >
    {visualLearningLoading
      ? "GENERATING VISUAL LEARNING..."
      : "GENERATE VISUAL LEARNING"}
  </button>

  {visualLearning && (
    <pre>{visualLearning}</pre>
  )}
</div>

<div className="adaptive-result">
  <h3>Visual Content</h3>

  <button
    type="button"
    onClick={generateVisualContent}
    disabled={visualContentLoading || !visualLearning}
  >
    {visualContentLoading
      ? "GENERATING VISUAL CONTENT..."
      : "GENERATE VISUAL CONTENT"}
  </button>

  {visualContent && (
    <pre>{visualContent}</pre>
  )}
</div>


<div className="adaptive-result">
  <h3>AI Whiteboard</h3>

  <button
    type="button"
    onClick={generateWhiteboard}
    disabled={whiteboardLoading}
  >
    {whiteboardLoading
      ? "GENERATING WHITEBOARD..."
      : "GENERATE AI WHITEBOARD"}
  </button>

  {whiteboard && (
    <pre>{whiteboard}</pre>
  )}
</div>

<div className="adaptive-result">
  <h3>Teaching Video</h3>

  <p>
    Generate a grounded teaching lesson with AI narration and a
    playable 2D educational video.
  </p>

  <button
    type="button"
    onClick={generateTeachingVideo}
    disabled={videoPlanLoading}
  >
    {videoPlanLoading
      ? "GENERATING TEACHING VIDEO..."
      : "GENERATE TEACHING VIDEO"}
  </button>

  {videoFile && (
    <div
      style={{
        marginTop: "20px",
        borderRadius: "18px",
        overflow: "hidden",
        background: "#05070b",
        border: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      <video
        controls
        preload="metadata"
        src={videoFile}
        style={{
          width: "100%",
          display: "block",
          maxHeight: "620px",
          background: "#05070b",
        }}
      >
        Your browser does not support video playback.
      </video>
    </div>
  )}

  {videoFile && (
    <div
      style={{
        marginTop: "14px",
        display: "flex",
        gap: "10px",
        flexWrap: "wrap",
      }}
    >
      <span className="question-type">AI TEACHER</span>
      <span className="question-type">2D ANIMATION</span>
      <span className="question-type">GROUNDED VIDEO</span>
    </div>
  )}

  {videoPlan && (
    <details style={{ marginTop: "20px" }}>
      <summary>View Teaching Video Plan</summary>
      <pre style={{ marginTop: "12px" }}>{videoPlan}</pre>
    </details>
  )}
</div>
          </div>

      {message && (
            <div className="login-message">
              {message}
            </div>
          )}
        </div>

        {questionBank && (
          <div className="question-card">
            <h3>Generated Question Bank</h3>

              <button
                type="button"
                className="login-submit"
                onClick={() => {
                setPracticeMode(true);
                setStudentAnswers("");
                setAssessmentReport("");
                setMessage("");
              }}
             >
              <span>START PRACTICE</span>
              <b>&gt;</b>
              </button>

            <div className="question-result">
              <pre style={{marginTop:"20px",padding:"18px",borderRadius:"14px",background:"rgba(5,8,20,0.72)",border:"1px solid rgba(130,145,255,0.16)",color:"#e8ecff",whiteSpace:"pre-wrap",lineHeight:1.6,overflowX:"auto"}}>{questionBank}</pre>
                {practiceMode && (
  <div className="practice-panel">
    <h3>Practice Mode</h3>

    <p className="muted">
      Write your answers below, then submit them for assessment.
    </p>

    <textarea
      className="practice-answer-input"
      placeholder="Write your answers here...

Example:
1. ...
2. ...
3. ..."
      value={studentAnswers}
      onChange={(event) =>
        setStudentAnswers(event.target.value)
      }
      rows={12}
    />

    <button
      type="button"
      className="login-submit"
      onClick={submitAssessment}
      disabled={assessmentLoading}
    >
      <span>
        {assessmentLoading
          ? "ASSESSING..."
          : "SUBMIT FOR ASSESSMENT"}
      </span>
      <b>&gt;</b>
    </button>

    {assessmentReport && (
  <div className="assessment-result">
    <h3>Assessment Report</h3>

    <pre>{assessmentReport}</pre>

    <button
      type="button"
      className="login-submit"
      onClick={generateAdaptiveLearning}
      disabled={adaptiveLoading}
    >
      <span>
        {adaptiveLoading
          ? "ANALYZING..."
          : "GENERATE ADAPTIVE LEARNING PLAN"}
      </span>
      <b>&gt;</b>
    </button>



    {adaptiveReport && (
      <div className="adaptive-result">
        <h3>Adaptive Learning Plan</h3>
        <pre>{adaptiveReport}</pre>
      </div>
    )}

{adaptiveReport && (
  <>  

    <button
      type="button"
      className="login-submit"
      onClick={generateStudyGuide}
      disabled={studyGuideLoading}
    >
      <span>
        {studyGuideLoading
          ? "GENERATING STUDY GUIDE..."
          : "GENERATE STUDY GUIDE"}
      </span>
      <b>&gt;</b>
    </button>

    {studyGuide && (
      <div className="adaptive-result">
        <h3>Study Guide</h3>
        <pre>{studyGuide}</pre>
      </div>

    )}
  </>
)}

  </div>
)}
  </div>
)}
            </div>
          </div>
        )}
    </PageShell>
  );
}
function QuestionCard({ type, title }) {
  return (
    <div className="question-card">
      <span className="question-type">{type}</span>
      <h3>{title}</h3>
      <button className="text-button">Open question</button>
    </div>
  );
}

function PYQPage() {
  return (
    <PageShell
      eyebrow="PYQ ANALYSIS"
      title="Understand what gets asked."
      description="Analyze previous-year questions to identify repeated and important topics."
    >
      <div className="analysis-grid">
        <AnalysisCard value="18" label="REPEATED QUESTIONS" />
        <AnalysisCard value="12" label="IMPORTANT TOPICS" />
        <AnalysisCard value="07" label="HIGH-FREQUENCY AREAS" />
      </div>

      <div className="feature-card">
        <span className="eyebrow">TOPIC SIGNAL</span>
        <h3>Normalization</h3>
        <p>
          PYQ analysis can help identify topics that repeatedly appear across
          previous examination papers.
        </p>
      </div>
    </PageShell>
  );
}

function AnalysisCard({ value, label }) {
  return (
    <div className="analysis-card">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function QuizPage() {
  return (
    <PageShell
      eyebrow="QUIZ ENGINE"
      title="Test what you know."
      description="Use generated quizzes to check understanding before the exam."
    >
      <div className="quiz-panel">
        <span className="question-type">QUESTION 01 / 10</span>
        <h2>Which normal form removes partial dependency?</h2>

        <div className="options">
          <button>A. First Normal Form</button>
          <button>B. Second Normal Form</button>
          <button>C. Third Normal Form</button>
          <button>D. BCNF</button>
        </div>
      </div>
    </PageShell>
  );
}

function ExamPage() {
  return (
    <PageShell
      eyebrow="EXAM MODE"
      title="Practice the answer format."
      description="Prepare answers according to the marks and depth expected in an examination."
    >
      <div className="exam-grid">
        <ExamCard marks="2 MARKS" text="Short definition" />
        <ExamCard marks="5 MARKS" text="Structured explanation" />
        <ExamCard marks="10 MARKS" text="Detailed examination answer" />
      </div>
    </PageShell>
  );
}

function ExamCard({ marks, text }) {
  return (
    <div className="exam-card">
      <span>{marks}</span>
      <h3>{text}</h3>
      <button className="secondary-button">Start practice</button>
    </div>
  );
}

function PlannerPage() {
  return (
    <PageShell
      eyebrow="STUDY PLANNER"
      title="Turn goals into progress."
      description="Organize topics, revision and practice into a focused learning workflow."
    >
      <div className="planner-card">
        <div className="planner-row">
          <span>Database Management</span>
          <strong>72%</strong>
        </div>

        <div className="progress-track">
          <div className="progress-fill" style={{ width: "72%" }} />
        </div>

        <div className="planner-row">
          <span>Machine Learning</span>
          <strong>48%</strong>
        </div>

        <div className="progress-track">
          <div className="progress-fill" style={{ width: "48%" }} />
        </div>

        <div className="planner-row">
          <span>Python</span>
          <strong>64%</strong>
        </div>

        <div className="progress-track">
          <div className="progress-fill" style={{ width: "64%" }} />
        </div>
      </div>
    </PageShell>
  );
}

function PageShell({ eyebrow, title, description, children }) {
  return (
    <section className="page-view">
      <div className="page-header">
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>

      <div className="page-content">{children}</div>
    </section>
  );
}


function VirtualTeacherPage() {
  const [topic, setTopic] = useState("");
  const [studentLevel, setStudentLevel] = useState("beginner");
  const [learningGoal, setLearningGoal] = useState("");
  const [teacherScript, setTeacherScript] = useState("");
  const [checkQuestion, setCheckQuestion] = useState("");
  const [studentAnswer, setStudentAnswer] = useState("");
  const [assessmentReport, setAssessmentReport] = useState("");
  const [adaptiveReport, setAdaptiveReport] = useState("");
  const [nextAction, setNextAction] = useState("");
  const [loading, setLoading] = useState(false);
  const [answerLoading, setAnswerLoading] = useState(false);
  const [voiceLoading, setVoiceLoading] = useState(false);
  const [voiceFile, setVoiceFile] = useState("");
  const [videoLoading, setVideoLoading] = useState(false);
  const [videoFile, setVideoFile] = useState("");
  const [videoPlan, setVideoPlan] = useState("");
  const [liveMessages, setLiveMessages] = useState([]);
  const [liveListening, setLiveListening] = useState(false);
  const [liveThinking, setLiveThinking] = useState(false);
  const [liveText, setLiveText] = useState("");
  const [liveMode, setLiveMode] = useState(false);
  const [liveError, setLiveError] = useState("");
  const recognitionRef = useRef(null);
  const [message, setMessage] = useState("");

  async function startLesson() {
    if (!topic.trim()) {
      setMessage("Enter a topic first.");
      return;
    }

    setLoading(true);
    setMessage("");
    setTeacherScript("");
    setCheckQuestion("");
    setStudentAnswer("");
    setAssessmentReport("");
    setAdaptiveReport("");
    setNextAction("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/virtual-teacher",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: topic.trim(),
            student_level: studentLevel,
            learning_goal: learningGoal.trim(),
            lesson_context: "",
            study_text: "",
            student_answer: "",
            check_question: "",
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to start Virtual Teacher."
        );
      }

      setTeacherScript(data.teacher_script || "");
      setCheckQuestion(data.check_question || "");
      setNextAction(data.next_action || "");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function speakLesson() {
  if (!topic.trim()) {
    setMessage("Start a lesson first.");
    return;
  }

  setVoiceLoading(true);
  setMessage("");
  setVoiceFile("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/voice-teacher",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.trim(),
          student_level: studentLevel,
          learning_goal: learningGoal.trim(),
          lesson_context: "",
          study_text: "",
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to generate teacher voice."
      );
    }

    if (!data.audio_file) {
      throw new Error(
        "Voice Teacher did not return an audio file."
      );
    }

    setVoiceFile(
      `http://127.0.0.1:8000${data.audio_file}`
    );
  } catch (error) {
    setMessage(error.message);
  } finally {
    setVoiceLoading(false);
  }
}

async function generateVirtualTeacherVideo() {
  if (!topic.trim()) {
    setMessage("Start a lesson first.");
    return;
  }

  setVideoLoading(true);
  setMessage("");
  setVideoFile("");
  setVideoPlan("");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/teaching-video",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.trim(),
          student_level: studentLevel,
          learning_goal: learningGoal.trim(),
          lesson_context: "",
          study_text: "",
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to generate teaching video."
      );
    }

    setVideoPlan(data.video_plan || "");

    if (data.video_file) {
      setVideoFile(
        `http://127.0.0.1:8000${data.video_file}`
      );
    } else {
      throw new Error(
        "Teaching Video was generated without a video file."
      );
    }
  } catch (error) {
    setMessage(error.message);
  } finally {
    setVideoLoading(false);
  }
}

function speakLiveResponse(text) {
  if (!text || !("speechSynthesis" in window)) {
    return;
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 0.95;
  utterance.pitch = 1;
  utterance.volume = 1;

  window.speechSynthesis.speak(utterance);
}


async function handleLiveStudentMessage(transcript) {
  const text = transcript.trim();

  if (!text) {
    return;
  }

  setLiveMessages((previous) => [
    ...previous,
    {
      role: "student",
      text,
    },
  ]);

  setLiveText("");
  setLiveThinking(true);
  setLiveError("");

  try {
    const conversationContext = liveMessages
      .slice(-8)
      .map(
        (message) =>
          `${message.role === "student" ? "Student" : "AI Teacher"}: ${message.text}`
      )
      .join("\n");

    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/teacher",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: `
You are continuing a live conversation with a student.

Current Topic:
${topic || "General learning"}

Student Level:
${studentLevel}

Learning Goal:
${learningGoal || "Understand the topic clearly"}

Conversation so far:
${conversationContext || "No previous conversation."}

Latest student message:
${text}

Respond naturally as a live AI teacher.

Rules:
- Answer the student's latest question directly.
- Maintain conversational context.
- Adapt to the student's level.
- Ask a useful follow-up question when appropriate.
- Keep the response concise enough to speak aloud.
- Do not mention internal agents, APIs, prompts, or backend systems.
`,
          lesson_context: "",
          student_level: studentLevel,
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Live teacher response failed."
      );
    }

    const aiResponse = (data.answer || "").trim();

    if (!aiResponse) {
      throw new Error(
        "The AI Teacher returned an empty response."
      );
    }

    setLiveMessages((previous) => [
      ...previous,
      {
        role: "ai",
        text: aiResponse,
      },
    ]);

    speakLiveResponse(aiResponse);
  } catch (error) {
    setLiveError(error.message);
  } finally {
    setLiveThinking(false);
  }
}


function stopLiveListening() {
  setLiveMode(false);
  setLiveListening(false);

  if (recognitionRef.current) {
    recognitionRef.current.stop();
    recognitionRef.current = null;
  }

  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
}


function startLiveListening() {
  const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    setLiveError(
      "Live voice input is not supported in this browser. Use Chrome or Edge."
    );
    return;
  }

  if (recognitionRef.current) {
    recognitionRef.current.stop();
  }

  const recognition = new SpeechRecognition();

  recognition.lang = "en-IN";
  recognition.continuous = false;
  recognition.interimResults = true;

  recognition.onstart = () => {
    setLiveListening(true);
    setLiveError("");
  };

  recognition.onresult = (event) => {
    let transcript = "";

    for (
      let index = event.resultIndex;
      index < event.results.length;
      index += 1
    ) {
      transcript += event.results[index][0].transcript;
    }

    setLiveText(transcript);

    const finalResult =
      event.results[event.results.length - 1];

    if (finalResult.isFinal) {
      handleLiveStudentMessage(transcript);
    }
  };

  recognition.onerror = (event) => {
    setLiveListening(false);

    if (event.error !== "no-speech") {
      setLiveError(
        `Voice input error: ${event.error}`
      );
    }
  };

  recognition.onend = () => {
    setLiveListening(false);
    recognitionRef.current = null;

    if (liveMode) {
      setTimeout(() => {
        startLiveListening();
      }, 500);
    }
  };

  recognitionRef.current = recognition;
  recognition.start();
}


function toggleLiveConversation() {
  if (liveMode) {
    stopLiveListening();
    return;
  }

  setLiveMode(true);
  setLiveError("");
  startLiveListening();
}

  async function submitStudentAnswer() {
    if (!studentAnswer.trim()) {
      setMessage("Enter your answer first.");
      return;
    }

    if (!checkQuestion.trim()) {
      setMessage("Start a lesson before submitting an answer.");
      return;
    }

    setAnswerLoading(true);
    setMessage("");
    setAssessmentReport("");
    setAdaptiveReport("");
    setNextAction("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/virtual-teacher",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: topic.trim(),
            student_level: studentLevel,
            learning_goal: learningGoal.trim(),
            lesson_context: "",
            study_text: "",
            student_answer: studentAnswer.trim(),
            check_question: checkQuestion,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to evaluate your answer."
        );
      }

      setTeacherScript(data.teacher_script || "");
      setAssessmentReport(data.assessment_report || "");
      setAdaptiveReport(data.adaptive_learning_report || "");
      setNextAction(data.next_action || "");
    } catch (error) {
      setMessage(error.message);
    } finally {
      setAnswerLoading(false);
    }
  }

  return (
    <PageShell
      eyebrow="VIRTUAL TEACHER"
      title="Learn with an adaptive AI teacher"
      description="Your teacher explains, checks your understanding, evaluates your answer, and decides the next learning action."
    >
      <div
        className="virtual-teacher-page"
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 1.5fr) minmax(280px, 0.8fr)",
          gap: "20px",
        }}
      >
        <div className="workspace-card">
          <div className="card-top">
            <span className="eyebrow">LIVE LESSON</span>
            <span className="live-dot">AI</span>
          </div>

          <div style={{ display: "grid", gap: "14px", marginTop: "18px" }}>
            <input
              className="text-input"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="What do you want to learn?"
            />

            <select
              className="text-input"
              value={studentLevel}
              onChange={(e) => setStudentLevel(e.target.value)}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>

            <input
              className="text-input"
              value={learningGoal}
              onChange={(e) => setLearningGoal(e.target.value)}
              placeholder="Learning goal (optional)"
            />

           <button
  className="secondary-button"
  onClick={speakLesson}
  disabled={voiceLoading || !topic.trim()}
  style={{ marginTop: "10px" }}
>
  {voiceLoading ? "GENERATING VOICE..." : "SPEAK LESSON"}
</button>

            <button
              className="primary-button live-start-button"
              onClick={startLesson}
              disabled={loading}
            >
              {loading ? "STARTING LESSON..." : "START VIRTUAL LESSON"}
            </button>
          </div>
         
          <button
  className="secondary-button"
  onClick={generateVirtualTeacherVideo}
  disabled={videoLoading || !topic.trim()}
  style={{ marginTop: "10px" }}
>
  {videoLoading
    ? "GENERATING TEACHING VIDEO..."
    : "WATCH TEACHING VIDEO"}
</button>

{videoFile && (
  <div
    className="workspace-card"
    style={{ marginTop: "16px" }}
  >
    <span className="eyebrow">AI TEACHING VIDEO</span>

    <video
      controls
      preload="metadata"
      src={videoFile}
      style={{
        width: "100%",
        display: "block",
        marginTop: "12px",
        maxHeight: "520px",
        background: "#05070b",
      }}
    >
      Your browser does not support video playback.
    </video>
  </div>
)}

{videoPlan && (
  <details style={{ marginTop: "14px" }}>
    <summary>View Teaching Video Plan</summary>
    <pre
      style={{
        marginTop: "10px",
        whiteSpace: "pre-wrap",
        lineHeight: 1.6,
        fontFamily: "inherit",
      }}
    >
      {videoPlan}
    </pre>
  </details>
)}  

{voiceFile && (
  <div
    className="workspace-card"
    style={{ marginTop: "14px" }}
  >
    <span className="eyebrow">VOICE TEACHER</span>

    <audio
      controls
      preload="metadata"
      src={voiceFile}
      style={{
        width: "100%",
        marginTop: "12px",
      }}
    >
      Your browser does not support audio playback.
    </audio>
  </div>
)} 
 
          {teacherScript && (
            <div
              className="adaptive-result"
              style={{ marginTop: "24px" }}
            >
              <h3>AI Teacher</h3>
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  lineHeight: 1.7,
                  fontFamily: "inherit",

                }}
              >
                {teacherScript}
              </pre>
            </div>
          )}

          {checkQuestion && !assessmentReport && (
            <div
              className="workspace-card"
              style={{ marginTop: "18px" }}
            >
              <span className="eyebrow">CHECK YOUR UNDERSTANDING</span>

              <h3 style={{ marginTop: "10px" }}>
                {checkQuestion}
              </h3>

              <textarea
                className="text-input"
                rows="5"
                value={studentAnswer}
                onChange={(e) => setStudentAnswer(e.target.value)}
                placeholder="Write your answer here..."
                style={{
                  marginTop: "14px",
                  width: "100%",
                  resize: "vertical",
                }}
              />

              <button
                className="primary-button"
                onClick={submitStudentAnswer}
                disabled={answerLoading}
                style={{ marginTop: "12px" }}
              >
                {answerLoading
                  ? "EVALUATING..."
                  : "SUBMIT ANSWER"}
              </button>
            </div>
          )}

          {assessmentReport && (
            <div
              className="adaptive-result"
              style={{ marginTop: "18px" }}
            >
              <h3>Assessment</h3>
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  lineHeight: 1.6,
                  fontFamily: "inherit",
                }}
              >
                {assessmentReport}
              </pre>
            </div>
          )}

          {adaptiveReport && (
            <div
              className="adaptive-result"
              style={{ marginTop: "18px" }}
            >
              <h3>Adaptive Learning</h3>
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  lineHeight: 1.6,
                  fontFamily: "inherit",
                }}
              >
                {adaptiveReport}
              </pre>
            </div>
          )}
        </div>

        <div style={{ display: "grid", gap: "18px" }}>
          <div className="workspace-card">
            <span className="eyebrow">NEXT ACTION</span>

            <h3 style={{ marginTop: "10px" }}>
              {nextAction || "Start a lesson to begin."}
            </h3>

            <p className="muted" style={{ marginTop: "10px" }}>
              The next step is determined from the student's
              demonstrated performance.
            </p>
          </div>

          <div className="workspace-card">
            <span className="eyebrow">LEARNING LOOP</span>

            <p style={{ lineHeight: 1.8, marginTop: "12px" }}>
              Teach
              <br />
              ?
              <br />
              Check
              <br />
              ?
              <br />
              Assess
              <br />
              ?
              <br />
              Adapt
              <br />
              ?
              <br />
              Continue / Reteach / Practice / Retest
            </p>
          </div>
        </div>
      </div>

      <div
  className="workspace-card"
  style={{ marginTop: "20px" }}
>
  <div
    className="card-top"
    style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: "12px",
    }}
  >
    <span className="eyebrow">LIVE CONVERSATION</span>

    <span
      className="live-dot"
      style={{
        opacity: liveMode ? 1 : 0.65,
      }}
    >
      {liveMode ? "LIVE" : "READY"}
    </span>
  </div>

  <h3 style={{ marginTop: "12px" }}>
    Talk directly with your AI Teacher
  </h3>

  <p className="muted">
    Speak naturally. The teacher listens, responds, and continues
    the conversation.
  </p>

  <div
    style={{
      minHeight: "180px",
      maxHeight: "320px",
      overflowY: "auto",
      marginTop: "16px",
      padding: "14px",
      borderRadius: "14px",
      background: "rgba(255,255,255,0.03)",
      border: "1px solid rgba(255,255,255,0.08)",
    }}
  >
    {liveMessages.length === 0 && (
      <div className="muted">
        Start the conversation and ask your teacher anything.
      </div>
    )}

    {liveMessages.map((messageItem, index) => (
      <div
        key={`${messageItem.role}-${index}`}
        style={{
          marginBottom: "14px",
          textAlign:
            messageItem.role === "student"
              ? "right"
              : "left",
        }}
      >
        <div
          className="eyebrow"
          style={{
            marginBottom: "5px",
          }}
        >
          {messageItem.role === "student"
            ? "YOU"
            : "AI TEACHER"}
        </div>

        <div
          style={{
            display: "inline-block",
            maxWidth: "88%",
            padding: "10px 13px",
            borderRadius: "12px",
            lineHeight: 1.55,
            background:
              messageItem.role === "student"
                ? "rgba(255,255,255,0.08)"
                : "rgba(80,120,255,0.12)",
          }}
        >
          {messageItem.text}
        </div>
      </div>
    ))}
  </div>

  {liveText && (
    <div
      className="muted"
      style={{
        marginTop: "12px",
        fontStyle: "italic",
      }}
    >
      Listening: {liveText}
    </div>
  )}

  {liveThinking && (
    <div
      className="muted"
      style={{ marginTop: "10px" }}
    >
      AI Teacher is thinking...
    </div>
  )}

  <div
    style={{
      display: "flex",
      gap: "10px",
      marginTop: "16px",
      flexWrap: "wrap",
    }}
  >
  <div className="live-conversation-actions">
  <button
    className="live-start-button"
    style={{minWidth:"180px",minHeight:"50px",padding:"0 22px",border:"1px solid rgba(140,165,255,0.65)",borderRadius:"15px",background:"linear-gradient(135deg,#6b3cff 0%,#4d74ff 55%,#2fcfff 100%)",color:"#fff",fontWeight:800,letterSpacing:"0.04em",boxShadow:"0 12px 30px rgba(82,75,255,0.28)",cursor:"pointer"}}
    onClick={toggleLiveConversation}
    disabled={liveThinking}
  >
    <span className="live-mic-dot" />
    {liveListening
      ? "STOP LISTENING"
      : liveMode
      ? "END LIVE CHAT"
      : "START LIVE CHAT"}
  </button>

  <button
    className="live-clear-button"
    style={{minWidth:"120px",minHeight:"50px",padding:"0 18px",border:"1px solid rgba(150,160,210,0.22)",borderRadius:"15px",background:"rgba(24,29,58,0.88)",color:"#dfe5ff",fontWeight:700,letterSpacing:"0.03em",boxShadow:"0 10px 24px rgba(0,0,0,0.22)",cursor:"pointer"}}
    onClick={() => {
      setLiveMessages([]);
      setLiveText("");
      setLiveError("");
    }}
    disabled={liveThinking || liveListening}
  >
    CLEAR CHAT
  </button>
  </div>

  {liveError && (
    <div
      className="guide-error"
      style={{ marginTop: "12px" }}
    >
      {liveError}
    </div>
  )}
</div>

      </div>

      {message && (
        <div
          className="guide-error"
          style={{ marginTop: "18px" }}
        >
          {message}
        </div>
      )}
    </PageShell>
  );
}

function App({ user }) {
  const [showWorkspace, setShowWorkspace] = useState(false);
  const [activePage, setActivePage] = useState("overview");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [isLightMode, setIsLightMode] = useState(false);

  const toggleTheme = () => {
    setIsLightMode((prev) => !prev);
  };

  if (!showWorkspace) {
    return <LandingPage onEnterWorkspace={() => setShowWorkspace(true)} isLightMode={isLightMode} toggleTheme={toggleTheme} />;
  }

  const activeMenu = menuItems.find((item) => item.id === activePage);

  const renderPage = () => {
    switch (activePage) {
      case "guide":
        return <GuidePage />;
      case "virtual-teacher":
        return <VirtualTeacherPage />;
      case "documents":
        return <DocumentsPage />;
      case "questions":
        return <QuestionsPage />;
      case "pyq":
        return <PYQPage />;
      case "quiz":
        return <QuizPage />;
      case "exam":
        return <ExamPage />;
      case "planner":
        return <PlannerPage />;
      case "verified-reasoning":
        return <VerifiedReasoningPage isLightMode={isLightMode} />;
      case "synthetic-peer":
        return <SyntheticPeerClassroomPage />;
      default:
        return <Overview setActivePage={setActivePage} />;
    }
  };

  return (
    <div className={`app-shell ${isLightMode ? "light-mode" : ""}`}>

      <button
  className="workspace-menu-toggle"
  onClick={() => setSidebarOpen(!sidebarOpen)}
  aria-label="Toggle workspace menu"
>
  <span />
  <span />
  <span />
</button>

      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">S</div>

          <div>
            <strong>SUBJECT GUIDE</strong>
            <span>AI LEARNING SYSTEM</span>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          AI SYSTEM ONLINE
        </div>

        <nav className="nav-menu">
          {menuItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${
                activePage === item.id ? "active" : ""
              }`}
              onClick={() => setActivePage(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span>LOCAL AI</span>
          <span>RAG CORE</span>
          <span>v0.1</span>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div>
            <span className="topbar-label">STUDENT INTELLIGENCE WORKSPACE</span>
            <strong>{activeMenu?.label}</strong>
          </div>

          <div className="topbar-user"><button type="button" className="secondary-button" onClick={toggleTheme} aria-label="Toggle theme">{isLightMode ? "☀️" : "🌙"}</button>
            <span className="grounded-badge">GROUNDED</span>
            <div className="avatar">{(user?.email || "SK").slice(0, 2).toUpperCase()}</div>
            <button
              type="button"
              className="secondary-button"
              onClick={() => supabase.auth.signOut()}
            >
              Logout
            </button>
          </div>
        </header>

        {renderPage()}
      </main>
    </div>
  );
}

export default App;





















