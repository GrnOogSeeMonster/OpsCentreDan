"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

type Connector = {
  id: string;
  name: string;
  connector_type: string;
  is_active: boolean;
};

export default function ConnectorsPage() {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [name, setName] = useState("Datadog Production");
  const [type, setType] = useState("datadog");
  const [secret, setSecret] = useState("replace-me");
  const [error, setError] = useState("");

  async function load() {
    const data = await apiFetch<Connector[]>("/api/v1/integrations/connectors");
    setConnectors(data);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, []);

  async function createConnector(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await apiFetch("/api/v1/integrations/connectors", {
        method: "POST",
        body: JSON.stringify({ name, connector_type: type, shared_secret: secret, config_json: {} }),
      });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create connector");
    }
  }

  return (
    <section className="grid-2">
      <div className="card">
        <h2 style={{ marginTop: 0 }}>Integration Connectors</h2>
        {connectors.map((connector) => (
          <div className="list-row" key={connector.id}>
            <strong>{connector.name}</strong>
            <div className="mono">{connector.connector_type}</div>
            <small style={{ color: "var(--muted)" }}>{connector.is_active ? "active" : "disabled"}</small>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Add Connector</h3>
        <form onSubmit={createConnector}>
          <label>Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} />
          <label style={{ marginTop: 8, display: "block" }}>Type</label>
          <select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="datadog">Datadog</option>
            <option value="prometheus">Prometheus</option>
            <option value="grafana">Grafana</option>
            <option value="cloudwatch">CloudWatch</option>
            <option value="azure_monitor">Azure Monitor</option>
            <option value="gcp_monitoring">GCP Monitoring</option>
            <option value="generic">Generic</option>
          </select>
          <label style={{ marginTop: 8, display: "block" }}>Shared secret</label>
          <input value={secret} onChange={(e) => setSecret(e.target.value)} />
          <div style={{ marginTop: 10 }}>
            <button type="submit">Create</button>
          </div>
        </form>
        {error ? <p style={{ color: "var(--danger)" }}>{error}</p> : null}
      </div>
    </section>
  );
}
