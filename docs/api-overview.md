# API Overview

Base URL: `/api/v1`

## Auth
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`

## Incident Lifecycle
- `GET /incidents`
- `POST /incidents`
- `GET /incidents/{incident_id}`
- `PATCH /incidents/{incident_id}`
- `GET /incidents/{incident_id}/events`
- `GET|POST /incidents/{incident_id}/comments`
- `GET|POST /incidents/{incident_id}/evidence`
- `POST /incidents/{incident_id}/evidence/upload`

## Inbound Alert Ingestion
- `POST /webhooks/{connector_id}`

## Integrations and Providers
- `GET|POST /integrations/connectors`
- `GET|POST /integrations/providers`

## AI and Knowledge
- `GET|POST /knowledge/documents`
- `GET /knowledge/jobs`
- `POST /assistant/incidents/{incident_id}/ask`

## Onboarding
- `GET /onboarding/status`
- `POST /onboarding/step`

## COE Reporting
- `POST /reports/incidents/{incident_id}/generate`
- `GET|PATCH /reports/{report_id}`
- `POST /reports/{report_id}/finalize`
- `GET|POST /reports/{report_id}/actions`

## Health
- `GET /health`
- `GET /ready`
