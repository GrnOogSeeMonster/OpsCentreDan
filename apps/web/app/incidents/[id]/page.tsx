"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { apiFetch } from "@/lib/api";

type Incident = {
  id: string;
  title: string;
  description: string;
  status: string;
  severity: string;
  priority: number;
  environment: string;
  tags: string[];
  affected_systems: string[];
  resolution_summary: string;
};

type IncidentEvent = {
  id: string;
  event_type: string;
  message: string;
  created_at: string;
};

type Comment = {
  id: string;
  body: string;
  provenance: string;
  created_at: string;
};

type Evidence = {
  id: string;
  title: string;
  evidence_type: string;
  content: string;
  source_url: string;
  provenance: string;
  created_at: string;
};

type AssistantResponse = {
  answer: string;
  evidence_summary: string[];
  inferences: string[];
  uncertainty: string;
  suggested_next_actions: string[];
  citations: Array<{ source_ref: string; excerpt: string; score: number; source_type: string; chunk_id: string }>;
};

export default function IncidentDetailPage({ params }: { params: { id: string } }) {
  const incidentId = params.id;

  const [incident, setIncident] = useState<Incident | null>(null);
  const [events, setEvents] = useState<IncidentEvent[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [error, setError] = useState("");

  const [commentText, setCommentText] = useState("Captured initial triage notes.");
  const [evidenceTitle, setEvidenceTitle] = useState("Grafana dashboard link");
  const [evidenceUrl, setEvidenceUrl] = useState("https://grafana.local/d/checkouts");

  const [question, setQuestion] = useState("What changed recently and what is the likely failing service?");
  const [assistant, setAssistant] = useState<AssistantResponse | null>(null);

  async function loadAll() {
    try {
      const [i, ev, c, e] = await Promise.all([
        apiFetch<Incident>(`/api/v1/incidents/${incidentId}`),
        apiFetch<IncidentEvent[]>(`/api/v1/incidents/${incidentId}/events`),
        apiFetch<Comment[]>(`/api/v1/incidents/${incidentId}/comments`),
        apiFetch<Evidence[]>(`/api/v1/incidents/${incidentId}/evidence`),
      ]);
      setIncident(i);
      setEvents(ev);
      setComments(c);
      setEvidence(e);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load incident");
    }
  }

  useEffect(() => {
    loadAll();
  }, [incidentId]);

  async function addComment(event: React.FormEvent) {
    event.preventDefault();
    await apiFetch(`/api/v1/incidents/${incidentId}/comments`, {
      method: "POST",
      body: JSON.stringify({ body: commentText, provenance: "human", citations: [] }),
    });
    setCommentText("");
    await loadAll();
  }

  async function addEvidence(event: React.FormEvent) {
    event.preventDefault();
    await apiFetch(`/api/v1/incidents/${incidentId}/evidence`, {
      method: "POST",
      body: JSON.stringify({
        title: evidenceTitle,
        evidence_type: "link",
        content: "Dashboard indicates elevated DB wait metrics.",
        source_url: evidenceUrl,
        provenance: "human",
      }),
    });
    await loadAll();
  }

  async function askAssistant(event: React.FormEvent) {
    event.preventDefault();
    try {
      const response = await apiFetch<AssistantResponse>(`/api/v1/assistant/incidents/${incidentId}/ask`, {
        method: "POST",
        body: JSON.stringify({ question, include_similar_incidents: true }),
      });
      setAssistant(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Assistant request failed");
    }
  }

  async function generateReport() {
    const report = await apiFetch<{ id: string }>(`/api/v1/reports/incidents/${incidentId}/generate`, {
      method: "POST",
      body: JSON.stringify({ label: "COE" }),
    });
    window.location.href = `/reports/${report.id}`;
  }

  const summary = useMemo(() => {
    if (!incident) return null;
    return `${incident.status.toUpperCase()} | ${incident.environment} | P${incident.priority}`;
  }, [incident]);

  if (error) {
    return <p style={{ color: "var(--danger)" }}>{error}</p>;
  }

  if (!incident) {
    return <p>Loading incident...</p>;
  }

  return (
    <section className="workspace">
      <div className="card">
        <h2 style={{ marginTop: 0 }}>{incident.title}</h2>
        <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <span className={`badge ${incident.severity}`}>{incident.severity}</span>
          <span className="badge">{incident.status}</span>
        </div>
        <p style={{ color: "var(--muted)" }}>{summary}</p>
        <p>{incident.description}</p>
        <hr style={{ borderColor: "var(--border)" }} />
        <p>
          <strong>Affected:</strong> {incident.affected_systems.join(", ") || "n/a"}
        </p>
        <p>
          <strong>Tags:</strong> {incident.tags.join(", ") || "n/a"}
        </p>
        <button onClick={generateReport}>Generate Draft COE</button>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Timeline and Evidence</h3>

        <form onSubmit={addComment} style={{ marginBottom: 14 }}>
          <label>Add Comment</label>
          <textarea value={commentText} onChange={(e) => setCommentText(e.target.value)} rows={3} />
          <div style={{ marginTop: 8 }}>
            <button type="submit" className="secondary">
              Add Comment
            </button>
          </div>
        </form>

        <form onSubmit={addEvidence} style={{ marginBottom: 16 }}>
          <label>Evidence Title</label>
          <input value={evidenceTitle} onChange={(e) => setEvidenceTitle(e.target.value)} />
          <label style={{ marginTop: 8, display: "block" }}>Evidence URL</label>
          <input value={evidenceUrl} onChange={(e) => setEvidenceUrl(e.target.value)} />
          <div style={{ marginTop: 8 }}>
            <button type="submit" className="secondary">
              Add Evidence Link
            </button>
          </div>
        </form>

        <h4>Events</h4>
        {events.map((event) => (
          <div className="list-row" key={event.id}>
            <div className="mono">{event.event_type}</div>
            <div>{event.message}</div>
            <small style={{ color: "var(--muted)" }}>{new Date(event.created_at).toLocaleString()}</small>
          </div>
        ))}

        <h4>Comments</h4>
        {comments.map((comment) => (
          <div className="list-row" key={comment.id}>
            <div>{comment.body}</div>
            <small style={{ color: "var(--muted)" }}>
              {comment.provenance} | {new Date(comment.created_at).toLocaleString()}
            </small>
          </div>
        ))}

        <h4>Evidence</h4>
        {evidence.map((item) => (
          <div className="list-row" key={item.id}>
            <strong>{item.title}</strong>
            <div>{item.content}</div>
            {item.source_url ? (
              <Link href={item.source_url} target="_blank" style={{ color: "var(--accent)" }}>
                {item.source_url}
              </Link>
            ) : null}
            <small style={{ color: "var(--muted)" }}>{item.provenance}</small>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>AI Investigation Assistant</h3>
        <form onSubmit={askAssistant}>
          <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={4} />
          <div style={{ marginTop: 8 }}>
            <button type="submit">Ask</button>
          </div>
        </form>

        {assistant ? (
          <div style={{ marginTop: 14 }}>
            <h4>Answer</h4>
            <p>{assistant.answer}</p>

            <h4>Evidence Summary</h4>
            <ul>
              {assistant.evidence_summary.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>

            <h4>Inferences (Not Confirmed Facts)</h4>
            <ul>
              {assistant.inferences.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>

            <h4>Suggested Next Actions</h4>
            <ul>
              {assistant.suggested_next_actions.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>

            <h4>Citations</h4>
            {assistant.citations.map((citation, idx) => (
              <div className="list-row" key={`${citation.chunk_id}-${idx}`}>
                <div className="mono">{citation.source_type}</div>
                <div>{citation.source_ref || "internal"}</div>
                <small style={{ color: "var(--muted)" }}>{citation.excerpt}</small>
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: "var(--muted)" }}>Ask a question to start AI-assisted investigation.</p>
        )}
      </div>
    </section>
  );
}
