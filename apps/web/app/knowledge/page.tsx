"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

type Doc = {
  id: string;
  title: string;
  source_type: string;
  ingestion_status: string;
  created_at: string;
};

type Job = {
  id: string;
  document_id: string;
  status: string;
  attempts: number;
  error_message: string;
};

export default function KnowledgePage() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [title, setTitle] = useState("Checkout Service Runbook");
  const [text, setText] = useState("If checkout latency rises: verify DB waits, queue depth, and deployment history.");

  async function load() {
    const [nextDocs, nextJobs] = await Promise.all([
      apiFetch<Doc[]>("/api/v1/knowledge/documents"),
      apiFetch<Job[]>("/api/v1/knowledge/jobs"),
    ]);
    setDocs(nextDocs);
    setJobs(nextJobs);
  }

  useEffect(() => {
    load();
  }, []);

  async function ingest(event: React.FormEvent) {
    event.preventDefault();
    await apiFetch("/api/v1/knowledge/documents", {
      method: "POST",
      body: JSON.stringify({
        title,
        source_type: "text",
        source_ref: "inline://runbook",
        text_content: text,
        metadata_json: { service: "checkout-api", environment: "production", kind: "runbook" },
      }),
    });
    await load();
  }

  return (
    <section className="grid-2">
      <div className="card">
        <h2 style={{ marginTop: 0 }}>Knowledge Base</h2>
        {docs.map((doc) => (
          <div className="list-row" key={doc.id}>
            <strong>{doc.title}</strong>
            <div className="mono">{doc.source_type}</div>
            <small style={{ color: "var(--muted)" }}>{doc.ingestion_status}</small>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Ingest Document</h3>
        <form onSubmit={ingest}>
          <label>Title</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
          <label style={{ marginTop: 8, display: "block" }}>Text</label>
          <textarea value={text} onChange={(e) => setText(e.target.value)} rows={6} />
          <div style={{ marginTop: 8 }}>
            <button type="submit">Ingest</button>
          </div>
        </form>

        <h4 style={{ marginTop: 16 }}>Embedding Jobs</h4>
        {jobs.map((job) => (
          <div className="list-row" key={job.id}>
            <div className="mono">{job.status}</div>
            <div>attempts: {job.attempts}</div>
            {job.error_message ? <small style={{ color: "var(--danger)" }}>{job.error_message}</small> : null}
          </div>
        ))}
      </div>
    </section>
  );
}
