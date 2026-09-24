import { useState } from "react";
import "./App.css";

const menuItems = [
  { id: "overview", label: "Overview", icon: "⌂" },
  { id: "guide", label: "AI Subject Guide", icon: "✦" },
  { id: "documents", label: "Documents", icon: "▣" },
  { id: "questions", label: "Question Bank", icon: "☷" },
  { id: "pyq", label: "PYQ Analysis", icon: "◈" },
  { id: "quiz", label: "Quiz", icon: "?" },
  { id: "exam", label: "Exam Mode", icon: "◉" },
  { id: "planner", label: "Study Planner", icon: "◫" },
];

function Overview({ setActivePage }) {
  return (
    <>
      <section className="hero-panel">
        <div className="hero-copy">
          <div className="eyebrow">AI KNOWLEDGE CORE</div>

          <h1>
            Learn from your
            <br />
            own knowledge.
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
              Open AI Teacher <span>→</span>
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
            <span className="pipeline-arrow">→</span>
            <PipelineStep number="02" title="RETRIEVE" />
            <span className="pipeline-arrow">→</span>
            <PipelineStep number="03" title="GENERATE" />
            <span className="pipeline-arrow">→</span>
            <PipelineStep number="04" title="CITE" />
          </div>

          <div className="grounding-box">
            <div className="grounding-icon">✓</div>
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
            Continue topic →
          </button>
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
      description="Ask questions from your uploaded study material and receive grounded answers with source context."
    >
      <div className="feature-grid">
        <div className="feature-card large-feature">
          <div className="feature-status">GROUNDED AI</div>

          <div className="chat-preview">
            <div className="chat-user">
              <span>YOU</span>

              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    askAI();
                  }
                }}
                placeholder="Ask something from your study material..."
              />

              <button className="primary-button" onClick={askAI} disabled={loading}>
                {loading ? "Thinking..." : "Ask AI →"}
              </button>
            </div>

            <div className="chat-ai">
              <span>AI TEACHER</span>

              {loading && <p>Retrieving relevant study material...</p>}

              {!loading && answer && <p>{answer}</p>}

              {!loading && citations.length > 0 && (
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
)}

              {!loading && !answer && !error && (
                <p>
                  Ask a question to retrieve a grounded answer from your study
                  material.
                </p>
              )}

              {error && <p>{error}</p>}
            </div>
          </div>

          <div className="source-chip">
            RAG PIPELINE · RETRIEVE · GENERATE · CITE
          </div>
        </div>

        <div className="feature-card">
          <span className="eyebrow">INTELLIGENCE</span>
          <h3>Grounded answers</h3>
          <p>
            The AI retrieves relevant study material before generating an
            answer.
          </p>
        </div>

        <div className="feature-card">
          <span className="eyebrow">PERSONALIZATION</span>
          <h3>Student-level explanations</h3>
          <p>
            The Subject Guide is designed to adapt explanations to the
            student's learning intent.
          </p>
        </div>
      </div>
    </PageShell>
  );
}
function DocumentsPage() {
  return (
    <PageShell
      eyebrow="DOCUMENT INTELLIGENCE"
      title="Your Knowledge Base"
      description="Manage the notes, textbooks and previous-year papers used by the AI learning system."
    >
      <div className="upload-panel">
        <div className="upload-icon">↑</div>
        <h2>Upload study material</h2>
        <p>PDF documents can become searchable knowledge for your AI Teacher.</p>
        <button className="primary-button">Choose PDF</button>
      </div>

      <div className="document-list">
        <DocumentRow name="Database Management Notes.pdf" pages="48 pages" />
        <DocumentRow name="DBMS Previous Year Questions.pdf" pages="32 pages" />
        <DocumentRow name="Machine Learning Unit 1.pdf" pages="26 pages" />
      </div>
    </PageShell>
  );
}

function DocumentRow({ name, pages }) {
  return (
    <div className="document-row">
      <div>
        <strong>{name}</strong>
        <span>{pages} · Indexed for retrieval</span>
      </div>
      <span className="document-status">READY</span>
    </div>
  );
}

function QuestionsPage() {
  return (
    <PageShell
      eyebrow="QUESTION BANK"
      title="Practice with purpose."
      description="Generate and organize questions from your learning material."
    >
      <div className="question-grid">
        <QuestionCard type="2 MARK" title="Define normalization." />
        <QuestionCard type="5 MARK" title="Explain the normal forms in DBMS." />
        <QuestionCard type="10 MARK" title="Discuss normalization with examples." />
      </div>
    </PageShell>
  );
}

function QuestionCard({ type, title }) {
  return (
    <div className="question-card">
      <span className="question-type">{type}</span>
      <h3>{title}</h3>
      <button className="text-button">Open question →</button>
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
      <button className="secondary-button">Start practice →</button>
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

function App() {
  const [activePage, setActivePage] = useState("overview");

  const activeMenu = menuItems.find((item) => item.id === activePage);

  const renderPage = () => {
    switch (activePage) {
      case "guide":
        return <GuidePage />;
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
      default:
        return <Overview setActivePage={setActivePage} />;
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
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

          <div className="topbar-user">
            <span className="grounded-badge">GROUNDED</span>
            <div className="avatar">SK</div>
          </div>
        </header>

        {renderPage()}
      </main>
    </div>
  );
}

export default App;