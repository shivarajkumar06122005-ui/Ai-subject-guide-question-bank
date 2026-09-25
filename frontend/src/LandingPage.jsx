import { useEffect, useRef } from "react";

function LandingPage({ onEnterWorkspace }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    let animationFrame;
    let particles = [];

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;

      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;

      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      particles = Array.from({ length: 90 }, () => ({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        size: Math.random() * 1.8 + 0.3,
        speed: Math.random() * 0.35 + 0.08,
        opacity: Math.random() * 0.6 + 0.15,
      }));
    };

    const animate = () => {
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

      particles.forEach((particle) => {
        particle.y -= particle.speed;

        if (particle.y < -10) {
          particle.y = window.innerHeight + 10;
          particle.x = Math.random() * window.innerWidth;
        }

        ctx.beginPath();
        ctx.arc(
          particle.x,
          particle.y,
          particle.size,
          0,
          Math.PI * 2
        );

        ctx.fillStyle = `rgba(140, 130, 255, ${particle.opacity})`;
        ctx.fill();
      });

      animationFrame = requestAnimationFrame(animate);
    };

    resize();
    animate();

    window.addEventListener("resize", resize);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrame);
    };
  }, []);

  return (
    <div className="landing-page">
      <div className="landing-background">
        <div className="landing-orb orb-one" />
        <div className="landing-orb orb-two" />
        <div className="landing-orb orb-three" />

        <div className="landing-grid" />
        <canvas ref={canvasRef} className="landing-stars" />
      </div>

      <nav className="landing-nav">
        <div className="landing-brand">
          <div className="brand-mark">S</div>

          <div>
            <strong>SUBJECT GUIDE <span>AI LEARNING SYSTEM</span></strong>
          </div>
        </div>

        <div className="landing-links">
          <a href="#workspace">Workspace</a>
          <a href="#features">Features</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#question-bank">Question Bank</a>
        </div>

        <div className="landing-nav-actions">
          <span className="demo-pill">
            <span />
            DEMO MODE
          </span>
          <br/>

          <button
            className="landing-enter-button"
            onClick={onEnterWorkspace}
          >
            Enter Workspace 
          </button>
        </div>
      </nav>

      <main className="landing-hero" id="workspace">
        <div className="activation-pill">
          <span className="status-dot" />
          AI KNOWLEDGE CORE · ONLINE
        </div>

        <div className="landing-core">
          <div className="core-aura" />

          <div className="core-sphere">
            <div className="core-highlight" />
            <div className="core-glow" />

            <div className="core-center">
              <span>AI</span>
              <small>GROUNDED</small>
            </div>
          </div>

          <div className="core-ring ring-one" />
          <div className="core-ring ring-two" />
          <div className="core-ring ring-three" />

          <div className="core-label retrieve">RETRIEVE</div>
          <div className="core-label reason">REASON</div>
          <div className="core-label ground">GROUND</div>
          <div className="core-label cite">CITE</div>
        </div>

        <div className="landing-title">
          <span>Learn from</span>
          <strong>your own knowledge.</strong>
        </div>

        <p className="landing-subtitle">
          Turn notes, textbooks and previous-year questions into
          an intelligent AI-powered learning system.
        </p>

        <div className="landing-actions">
          <button
            className="landing-primary-button"
            onClick={onEnterWorkspace}
          >
            Enter AI Workspace
            <span>→</span>
          </button>

          <a
            className="landing-secondary-button"
            href="#how-it-works"
          >
            Explore how it works
          </a>
        </div>

        <div className="landing-feature-row">
          <div>
            <strong>RAG</strong>
            <span>Grounded answers</span>
          </div>

          <div>
            <strong>AI TEACHER</strong>
            <span>Student-level explanations</span>
          </div>

          <div>
            <strong>PYQ</strong>
            <span>Exam-focused intelligence</span>
          </div>

          <div>
            <strong>LOCAL AI</strong>
            <span>Privacy-aware learning</span>
          </div>
        </div>
      </main>

      <section className="landing-section" id="features">
        <div className="section-eyebrow">THE INTELLIGENCE LAYER</div>

        <h2>
          One learning system.
          <br />
          <span>Everything connected.</span>
        </h2>

        <div className="landing-feature-grid">
          <article>
            <span>01</span>
            <h3>AI Subject Guide</h3>
            <p>
              Ask questions and receive answers grounded in
              your study material.
            </p>
          </article>

          <article>
            <span>02</span>
            <h3>Question Bank</h3>
            <p>
              Turn academic material into focused examination
              practice.
            </p>
          </article>

          <article>
            <span>03</span>
            <h3>PYQ Intelligence</h3>
            <p>
              Discover repeated questions and important
              examination topics.
            </p>
          </article>
        </div>
      </section>

      <section
        className="landing-section landing-process"
        id="how-it-works"
      >
        <div className="section-eyebrow">HOW IT WORKS</div>

        <h2>
          From question
          <br />
          <span>to grounded answer.</span>
        </h2>

        <div className="question-demo">
          <div>
            <span>QUESTION</span>
            <strong>What is C?</strong>
          </div>

          <span>→</span>

          <div>
            <span>RETRIEVE</span>
            <strong>Study material</strong>
          </div>

          <span>→</span>

          <div>
            <span>GENERATE</span>
            <strong>Grounded response</strong>
          </div>

          <span>→</span>

          <div>
            <span>CITE</span>
            <strong>Source context</strong>
          </div>
        </div>
      </section>

      <section
        className="landing-section landing-final"
        id="question-bank"
      >
        <div className="section-eyebrow">SUBJECT GUIDE AI</div>

        <h2>
          Your knowledge.
          <br />
          <span>Your AI teacher.</span>
        </h2>

        <button
          className="landing-primary-button"
          onClick={onEnterWorkspace}
        >
          Enter Workspace
          <span>→</span>
        </button>
      </section>
    </div>
  );
}

export default LandingPage;