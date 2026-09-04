"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { apiFetch, setSession } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@opscentredan.dev");
  const [password, setPassword] = useState("ChangeMeNow123!");
  const [error, setError] = useState("");

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");

    try {
      const response = await apiFetch<{ access_token: string; refresh_token: string }>(
        "/api/v1/auth/login",
        {
        method: "POST",
        body: JSON.stringify({ email, password }),
        }
      );
      setSession(response.access_token, response.refresh_token);
      router.push("/incidents");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <section style={{ maxWidth: 480, margin: "40px auto" }}>
      <div className="card">
        <h2 style={{ marginTop: 0 }}>Sign In</h2>
        <p style={{ color: "var(--muted)" }}>
          Use seeded admin credentials or your configured account.
        </p>
        <form onSubmit={onSubmit}>
          <label>Email</label>
          <input value={email} onChange={(e) => setEmail(e.target.value)} />
          <label style={{ marginTop: 12, display: "block" }}>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ marginBottom: 12 }}
          />
          <button type="submit">Sign in</button>
        </form>
        {error ? (
          <p style={{ color: "var(--danger)", marginTop: 10 }} className="mono">
            {error}
          </p>
        ) : null}
      </div>
    </section>
  );
}
