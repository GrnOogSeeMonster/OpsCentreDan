# Checkout Service Runbook

## Symptoms
- P95 latency over 1.5s
- Increased DB wait time
- Elevated queue depth

## First Response
1. Check recent deployment in `checkout-api`.
2. Confirm database CPU, locks, and connection pool saturation.
3. Compare request volume with baseline.
4. Apply traffic shedding if customer impact is active.

## Recovery
- Roll back risky release.
- Increase DB capacity if sustained.
- Validate that error rate normalizes before closing.
