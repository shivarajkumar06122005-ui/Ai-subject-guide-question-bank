import { useEffect, useState } from "react";
import { supabase } from "./supabaseClient";

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [resetMode, setResetMode] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState("");
  const [mode, setMode] = useState("login");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [isLightMode, setIsLightMode] = useState(false);

  useEffect(() => {
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY") {
        setResetMode(true);
        setMode("login");
        setMessage("");
        setPassword("");
        setConfirmPassword("");
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");

    if (resetMode) {
      if (password.length < 6) {
        setMessage("Password must be at least 6 characters.");
        return;
      }

      if (password !== confirmPassword) {
        setMessage("Passwords do not match.");
        return;
      }

      setLoading(true);

      const { error } = await supabase.auth.updateUser({
        password,
      });

      setLoading(false);

      if (error) {
        setMessage(error.message);
        return;
      }

      setPassword("");
      setConfirmPassword("");
      setResetMode(false);
      setMode("login");
      setMessage("Password updated successfully. You can now log in.");
      return;
    }

    setLoading(true);

    const result =
      mode === "login"
        ? await supabase.auth.signInWithPassword({
            email,
            password,
          })
        : await supabase.auth.signUp({
            email,
            password,
          });

    setLoading(false);

    if (result.error) {
      setMessage(result.error.message);
      return;
    }

    if (mode === "signup") {
      setMessage(
        "Account created. Check your email if confirmation is enabled."
      );
      return;
    }

    onLogin(result.data.user);
  }

  async function handleForgotPassword() {
    if (!email.trim()) {
      setMessage("Enter your email first.");
      return;
    }

    setMessage("");
    setLoading(true);

    const { error } = await supabase.auth.resetPasswordForEmail(
      email.trim(),
      {
        redirectTo: `${window.location.origin}/`,
      }
    );

    setLoading(false);

    if (error) {
      setMessage(error.message);
      return;
    }

    setMessage("Password reset email sent. Check your inbox.");
  }

  return (
    <main className={`login-screen ${isLightMode ? "light-mode" : ""}`}>
      <div className="login-grid" />

      <div className="login-layout">
        <section className="login-brand">
          <div className="login-badge">
            <span className="badge-dot" />
            AI LEARNING WORLD
          </div>

          <h1>
            Learn.
            <br />
            <span>Level Up.</span>
          </h1>

          <p>
            Your AI-powered study world for concepts, practice,
            exams, projects and personalized learning.
          </p>

          <div className="login-stats">
            <div>
              <strong>AI</strong>
              <span>Teacher</span>
            </div>

            <div>
              <strong>XP</strong>
              <span>Learning paths</span>
            </div>

            <div>
              <strong>XP</strong>
              <span>Progress</span>
            </div>
          </div>
        </section>

        <section className="login-card">
          <div className="login-card-content">
            <div className="login-console-top">
              <div className="login-logo">
                <div className="logo-core">S</div>

                <div>
                  <strong>SUBJECT GUIDE AI</strong>
                  <span>INTELLIGENT LEARNING SYSTEM</span>
                </div>
              </div>
              <button
                type="button"
                className="login-theme-button"
                onClick={() => setIsLightMode((prev) => !prev)}
                aria-label="Toggle theme"
              >
                {isLightMode ? "☀️" : "🌙"}
              </button>


              <div className="login-status">
                <span></span>
                SYSTEM READY
              </div>
            </div>

            <div className="login-learning-core">
              <div className="core-ring">
                <div className="core-dot"></div>
              </div>

              <div>
                <strong>LEARNING CORE</strong>
                <span>Personalized AI workspace</span>
              </div>
            </div>

            <div className="login-heading">
              <span className="eyebrow">
                {resetMode
                  ? "RESET PASSWORD"
                  : mode === "login"
                    ? "WELCOME BACK"
                    : "START YOUR JOURNEY"}
              </span>

              <h2>
                {resetMode
                  ? "Create a new password."
                  : mode === "login"
                    ? "Continue learning."
                    : "Create your learning profile."}
              </h2>

              <p>
                {resetMode
                  ? "Set a new password for your Subject Guide AI account."
                  : mode === "login"
                    ? "Enter your account to continue your progress."
                    : "Build a personalized AI learning journey."}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="login-form">
              {!resetMode && (
                <label>
                  <span>Email</span>

                  <input
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(event) =>
                      setEmail(event.target.value)
                    }
                    required
                  />
                </label>
              )}

              <label>
                <span>{resetMode ? "New Password" : "Password"}</span>

                <input
                  type="password"
                  placeholder={
                    resetMode ? "New password" : "Password"
                  }
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  required
                  minLength={6}
                />
              </label>

              {resetMode && (
                <label>
                  <span>Confirm Password</span>

                  <input
                    type="password"
                    placeholder="Confirm new password"
                    value={confirmPassword}
                    onChange={(event) =>
                      setConfirmPassword(event.target.value)
                    }
                    required
                    minLength={6}
                  />
                </label>
              )}

              {!resetMode && mode === "login" && (
                <button
                  type="button"
                  className="forgot-password"
                  onClick={handleForgotPassword}
                  disabled={loading}
                >
                  Forgot password?
                </button>
              )}

              <button
                className="login-submit"
                type="submit"
                disabled={loading}
              >
                <span>
                  {loading
                    ? "PROCESSING..."
                    : resetMode
                      ? "UPDATE PASSWORD"
                      : mode === "login"
                        ? "ENTER LEARNING WORLD"
                        : "CREATE LEARNING PROFILE"}
                </span>

                <b>&gt;</b>
              </button>
            </form>

            {message && (
              <div className="login-message">
                {message}
              </div>
            )}

            {!resetMode && (
              <div className="login-switch">
                <span>
                  {mode === "login"
                    ? "New to Subject Guide AI?"
                    : "Already have an account?"}
                </span>

                <button
                  type="button"
                  onClick={() => {
                    setMode(
                      mode === "login"
                        ? "signup"
                        : "login"
                    );
                    setMessage("");
                  }}
                >
                  {mode === "login"
                    ? "Create account"
                    : "Login"}
                </button>
              </div>
            )}

            {resetMode && (
              <div className="login-switch">
                <span>Remember your password?</span>

                <button
                  type="button"
                  onClick={() => {
                    setResetMode(false);
                    setMode("login");
                    setPassword("");
                    setConfirmPassword("");
                    setMessage("");
                  }}
                >
                  Back to Login
                </button>
              </div>
            )}

            <div className="login-footer">
              <span>SECURE AUTHENTICATION</span>
              <span>/</span>
              <span>PERSONALIZED PROGRESS</span>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

export default LoginPage;
