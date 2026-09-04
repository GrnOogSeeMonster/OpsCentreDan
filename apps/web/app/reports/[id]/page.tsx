"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

type Report = {
  id: string;
  incident_id: string;
  label: string;
  status: string;
  summary: string;
  root_cause: string;
  impact_analysis: string;
  remediation: string;
  preventative_recommendations: string;
};

export default function ReportPage({ params }: { params: { id: string } }) {
  const reportId = params.id;
  const [report, setReport] = useState<Report | null>(null);
  const [message, setMessage] = useState("");

  async function load() {
    const data = await apiFetch<Report>(`/api/v1/reports/${reportId}`);
    setReport(data);
  }

  useEffect(() => {
    load();
  }, [reportId]);

  async function save() {
    if (!report) return;
    await apiFetch(`/api/v1/reports/${reportId}`, {
      method: "PATCH",
      body: JSON.stringify({
        summary: report.summary,
        root_cause: report.root_cause,
        impact_analysis: report.impact_analysis,
        remediation: report.remediation,
        preventative_recommendations: report.preventative_recommendations,
      }),
    });
    setMessage("Saved draft report.");
    await load();
  }

  async function finalize() {
    await apiFetch(`/api/v1/reports/${reportId}/finalize`, { method: "POST" });
    setMessage("Report finalized.");
    await load();
  }

  if (!report) {
    return <p>Loading report...</p>;
  }

  return (
    <section className="card" style={{ maxWidth: 1000 }}>
      <h2 style={{ marginTop: 0 }}>
        {report.label} Report <span className="badge">{report.status}</span>
      </h2>
      <p style={{ color: "var(--muted)" }} className="mono">
        Incident: {report.incident_id}
      </p>

      <label>Summary</label>
      <textarea
        rows={4}
        value={report.summary}
        onChange={(e) => setReport({ ...report, summary: e.target.value })}
      />

      <label style={{ marginTop: 8, display: "block" }}>Root Cause</label>
      <textarea
        rows={3}
        value={report.root_cause}
        onChange={(e) => setReport({ ...report, root_cause: e.target.value })}
      />

      <label style={{ marginTop: 8, display: "block" }}>Impact Analysis</label>
      <textarea
        rows={3}
        value={report.impact_analysis}
        onChange={(e) => setReport({ ...report, impact_analysis: e.target.value })}
      />

      <label style={{ marginTop: 8, display: "block" }}>Remediation</label>
      <textarea
        rows={3}
        value={report.remediation}
        onChange={(e) => setReport({ ...report, remediation: e.target.value })}
      />

      <label style={{ marginTop: 8, display: "block" }}>Preventative Recommendations</label>
      <textarea
        rows={3}
        value={report.preventative_recommendations}
        onChange={(e) => setReport({ ...report, preventative_recommendations: e.target.value })}
      />

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button onClick={save}>Save Draft</button>
        <button onClick={finalize} className="secondary">
          Finalize
        </button>
      </div>

      {message ? <p style={{ color: "var(--ok)" }}>{message}</p> : null}
    </section>
  );
}
