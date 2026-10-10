import { useState } from "react";
import { supabase } from "./supabaseClient";

function ResetPasswordPage({ onComplete }) {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");
    setError("");

    if (password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    const { error: updateError } = await supabase.auth.updateUser({ password });
    setLoading(false);

    if (updateError) {
      setError(updateError.message);
      return;
    }

    await supabase.auth.signOut();
    setMessage("Password updated. You can now log in with your new password.");
    setTimeout(() => onComplete?.(), 800);
  }

  return (
    <main className="login-screen">
      <div className="login-grid" />
      <div className="login-layout">
        <section className="login-brand">
          <div className="login-badge"><span className="badge-dot" /> AI LEARNING WORLD</div>
          <h1>Reset.<br /><span>Continue.</span></h1>
          <p>Set a new password and return to your personalized learning workspace.</p>
        </section>
        <section className="login-card">
          <div className="login-card-content">
            <div className="login-console-top">
              <div className="login-logo">
                <div className="logo-core">S</div>
                <div><strong>SUBJECT GUIDE AI</strong><span>SECURE ACCOUNT RECOVERY</span></div>
              </div>
              <div className="login-status"><span /> SECURE</div>
            </div>
            <div className="login-heading">
              <span className="eyebrow">PASSWORD RECOVERY</span>
              <h2>Create a new password.</h2>
              <p>Choose a new password for your learning account.</p>
            </div>
            <form onSubmit={handleSubmit} className="login-form">
              <label><span>New password</span><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={6} required /></label>
              <label><span>Confirm password</span><input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} minLength={6} required /></label>
              <button className="login-submit" type="submit" disabled={loading}><span>{loading ? "UPDATING..." : "UPDATE PASSWORD"}</span><b>&gt;</b></button>
            </form>
            {(error || message) && <div className="login-message">{error || message}</div>}
          </div>
        </section>
      </div>
    </main>
  );
}

export default ResetPasswordPage;
