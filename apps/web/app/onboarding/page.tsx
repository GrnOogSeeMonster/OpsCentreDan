"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

type OnboardingStatus = {
  completed_steps: string[];
  checks: Array<{ name: string; ok: boolean }>;
};

const steps = [
  { id: "cloud_provider", title: "Cloud Provider" },
  { id: "observability_provider", title: "Observability" },
  { id: "ai_provider", title: "AI Provider" },
  { id: "embedding_provider", title: "Embedding Provider" },
  { id: "oidc", title: "OIDC (optional)" },
];

export default function OnboardingPage() {
  const [status, setStatus] = useState<OnboardingStatus | null>(null);
  const [message, setMessage] = useState("");

  async function load() {
    const next = await apiFetch<OnboardingStatus>("/api/v1/onboarding/status");
    setStatus(next);
  }

  useEffect(() => {
    load();
  }, []);

  async function completeStep(step: string) {
    await apiFetch("/api/v1/onboarding/step", {
      method: "POST",
      body: JSON.stringify({ step, payload: { configured_at: new Date().toISOString(), mode: "demo" } }),
    });
    setMessage(`Recorded step: ${step}`);
    await load();
  }

  return (
    <section className="card" style={{ maxWidth: 900 }}>
      <h2 style={{ marginTop: 0 }}>Setup Wizard</h2>
      <p style={{ color: "var(--muted)" }}>
        Complete these steps to configure providers, run first connector test, and verify readiness.
      </p>

      {steps.map((step) => (
        <div className="list-row" key={step.id}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong>{step.title}</strong>
            <button className="secondary" onClick={() => completeStep(step.id)}>
              Mark Configured
            </button>
          </div>
        </div>
      ))}

      <h3>Checks</h3>
      {status?.checks.map((check) => (
        <div key={check.name} className="list-row">
          <span className="mono">{check.name}</span> : {check.ok ? "OK" : "Pending"}
        </div>
      ))}

      {message ? <p style={{ color: "var(--ok)" }}>{message}</p> : null}
    </section>
  );
}
