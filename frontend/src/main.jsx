import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import LoginPage from "./LoginPage.jsx";
import ResetPasswordPage from "./ResetPasswordPage.jsx";
import { supabase } from "./supabaseClient";

function AuthGate() {
  const [session, setSession] = useState(null);
  const [checking, setChecking] = useState(true);
  const [recovering, setRecovering] = useState(false);

  useEffect(() => {
    let mounted = true;

    supabase.auth.getSession().then(({ data }) => {
      if (mounted) {
        setSession(data.session);
        setChecking(false);
      }
    });

    const { data: listener } = supabase.auth.onAuthStateChange((event, nextSession) => {
      if (!mounted) return;
      if (event === "PASSWORD_RECOVERY") {
        setRecovering(true);
        setSession(nextSession);
        return;
      }
      setSession(nextSession);
    });

    return () => {
      mounted = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  if (checking) return <div className="login-screen"><div className="login-message">Loading secure workspace...</div></div>;
  if (recovering) return <ResetPasswordPage onComplete={() => { setRecovering(false); setSession(null); }} />;
  if (!session) return <LoginPage onLogin={setSession} />;
  return <App user={session.user} />;
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AuthGate />
  </StrictMode>,
);
