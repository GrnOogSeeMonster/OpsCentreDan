# Threat Model (Initial)

## Assets
- Incident data and evidence
- Credentials and provider configuration
- Knowledge corpus and embeddings
- Audit history

## Primary Threats and Mitigations
- Unauthorized access:
  - JWT auth, RBAC guards, active-user checks.
- Credential theft:
  - Environment-based secrets, no hardcoded prod keys, explicit docs.
- Injection/XSS:
  - Pydantic validation, constrained rendering surfaces, no raw HTML execution.
- SSRF via connectors:
  - Current design accepts inbound webhooks only; no arbitrary outbound fetch in request path.
- Data tampering:
  - Audit events for sensitive operations and provenance markers.
- Abuse/bruteforce:
  - Rate limiting on login, webhook, and assistant endpoints.
- Unsafe AI actions:
  - AI responses are suggestions only; no silent write-back path.

## Follow-up Hardening
- Add OIDC integration with managed identity provider.
- Add signed webhook verification per provider.
- Add malware scanning for uploaded files.
- Add object storage and encrypted-at-rest evidence option.
