import { FormEvent, useState } from "react";
import { Film, Loader2, Sparkles } from "lucide-react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card } from "../components/ui/card";

export function LandingPage() {
  const { user, login, signup } = useAuth();
  const [mode, setMode] = useState<"login" | "signup">("signup");
  const [email, setEmail] = useState("demo@whatnext.ai");
  const [username, setUsername] = useState("demo");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/dashboard" replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (mode === "signup") await signup(email, username, password);
      else await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="relative flex min-h-screen items-center overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1800&q=80"
          alt=""
          className="absolute inset-0 h-full w-full object-cover opacity-30"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/85 to-background/30" />
        <div className="relative mx-auto grid max-w-7xl gap-8 px-4 py-12 lg:grid-cols-[1.1fr_420px]">
          <div className="flex flex-col justify-center">
            <div className="mb-5 flex items-center gap-2 text-rose-400">
              <Sparkles className="h-5 w-5" />
              <span className="text-sm font-semibold uppercase tracking-wide">AI taste graph for stories</span>
            </div>
            <h1 className="max-w-4xl text-5xl font-black leading-tight md:text-7xl">WhatNext</h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-zinc-300">
              Log what you read and watch, then get cross-media recommendations that understand mood, pacing, themes, and semantic similarity.
            </p>
            <div className="mt-8 grid max-w-xl grid-cols-3 gap-3 text-sm text-zinc-300">
              {["Books", "Movies", "TV shows"].map((item) => (
                <div key={item} className="rounded-md border border-border bg-zinc-950/70 p-3">
                  <Film className="mb-2 h-4 w-4 text-rose-400" />
                  {item}
                </div>
              ))}
            </div>
          </div>
          <Card className="self-center p-5">
            <div className="mb-5 flex rounded-md bg-zinc-950 p-1">
              {(["signup", "login"] as const).map((item) => (
                <button
                  key={item}
                  onClick={() => setMode(item)}
                  className={`h-9 flex-1 rounded text-sm font-semibold ${mode === item ? "bg-zinc-800 text-white" : "text-zinc-500"}`}
                >
                  {item === "signup" ? "Sign up" : "Log in"}
                </button>
              ))}
            </div>
            <form onSubmit={submit} className="space-y-3">
              <Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" required />
              {mode === "signup" ? (
                <Input value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Username" required />
              ) : null}
              <Input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Password" required />
              {error ? <p className="rounded border border-rose-800 bg-rose-950/40 p-2 text-sm text-rose-100">{error}</p> : null}
              <Button type="submit" className="w-full" disabled={busy}>
                {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                {mode === "signup" ? "Create account" : "Log in"}
              </Button>
            </form>
          </Card>
        </div>
      </section>
    </main>
  );
}
