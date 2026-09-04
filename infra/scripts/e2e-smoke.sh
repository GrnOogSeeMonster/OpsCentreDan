#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@opscentredan.dev}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-ChangeMeNow123!}"

TOKEN=$(curl -sS -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$ADMIN_PASSWORD\"}" | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "Failed to obtain token"
  exit 1
fi

INCIDENT_ID=$(curl -sS -X POST "$API_URL/api/v1/incidents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Smoke test incident","description":"E2E smoke path","severity":"sev3","priority":3,"environment":"production","affected_systems":["api"],"tags":["smoke"]}' | jq -r '.id')

curl -sS -X POST "$API_URL/api/v1/incidents/$INCIDENT_ID/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body":"Smoke comment","provenance":"human","citations":[]}' > /dev/null

REPORT_ID=$(curl -sS -X POST "$API_URL/api/v1/reports/incidents/$INCIDENT_ID/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"label":"COE"}' | jq -r '.id')

echo "Smoke test passed: incident=$INCIDENT_ID report=$REPORT_ID"
