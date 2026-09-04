"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

type Incident = {
  id: string;
  title: string;
  status: string;
  severity: string;
  environment: string;
  updated_at: string;
};

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [error, setError] = useState("");

  const [title, setTitle] = useState("Database CPU saturation");
  const [description, setDescription] = useState("Primary DB CPU above 95% for 8m.");

  async function load() {
    try {
      const data = await apiFetch<Incident[]>("/api/v1/incidents");
      setIncidents(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load incidents");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function createIncident(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await apiFetch("/api/v1/incidents", {
        method: "POST",
        body: JSON.stringify({
          title,
          description,
          severity: "sev2",
          priority: 2,
          environment: "production",
          affected_systems: ["postgres"],
          tags: ["db", "performance"],
        }),
      });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create incident");
    }
  }

  return (
    <section>
      <div className="grid-2">
        <div className="card">
          <h2 style={{ marginTop: 0 }}>Incidents</h2>
          <p style={{ color: "var(--muted)", marginTop: -6 }}>
            Incident lifecycle workspace for triage and response.
          </p>
          {incidents.map((incident) => (
            <Link href={`/incidents/${incident.id}`} key={incident.id} className="list-row">
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                <strong>{incident.title}</strong>
                <span className={`badge ${incident.severity}`}>{incident.severity}</span>
              </div>
              <div style={{ color: "var(--muted)", marginTop: 6 }}>
                <span className="mono">{incident.status}</span> | {incident.environment}
              </div>
            </Link>
          ))}
        </div>

        <div className="card">
          <h3 style={{ marginTop: 0 }}>Create Incident</h3>
          <form onSubmit={createIncident}>
            <label>Title</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} />
            <label style={{ marginTop: 12, display: "block" }}>Description</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={5} />
            <div style={{ marginTop: 12 }}>
              <button type="submit">Create</button>
            </div>
          </form>
          {error ? <p style={{ color: "var(--danger)" }}>{error}</p> : null}
        </div>
      </div>
    </section>
  );
}
