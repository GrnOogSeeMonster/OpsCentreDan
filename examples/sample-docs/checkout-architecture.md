# Architecture: Checkout Flow

`web` -> `checkout-api` -> `orders-db` and `payment-gateway`

Critical dependencies:
- Redis cache for session and rate checks
- Postgres primary for transactional writes
- External payment provider API

Known hotspots:
- Connection pool exhaustion under burst traffic
- Retry storms when payment gateway latency rises
