# Past Incident: DB Wait Event Spike

Incident summary:
- Start: 2026-02-11T09:14:00Z
- End: 2026-02-11T10:06:00Z

Root cause hypothesis:
- Unoptimized query path activated by feature flag rollout.

Remediation:
- Feature flag disabled.
- Hotfix deployed for query index path.
- Added canary check for DB wait growth.
