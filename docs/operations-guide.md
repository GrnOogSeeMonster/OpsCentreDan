# Operations Guide

## Local Start
1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open web app at `http://localhost:3000`.
4. API docs at `http://localhost:8000/docs`.

## Default Seed User
- Email: `admin@opscentredan.dev`
- Password: `ChangeMeNow123!`

## Health Endpoints
- Liveness: `GET /health`
- Readiness: `GET /ready`

## Alert Ingestion Test
Use the seeded connector secret (`demo-secret`) with payload examples under `examples/webhook-payloads/`.

## Notes
- AI endpoints require `OPENAI_API_KEY` for generation/embeddings.
- Without API key, assistant/embedding APIs return explicit service-unavailable errors.
