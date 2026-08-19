# Houdini Pro Utility

**Copyright & Ownership (c) 2026 Melvyn Douglas Braun (Prince Mel Braun). All Rights Reserved.**  
**Business Entity:** Dual Sovereign Braun Autonomous Ecosystems

Houdini Pro Utility is a small Flask service that publishes operational status, a fixed pipeline catalog, and deterministic routing-plan validation. It is intentionally **not** a settlement engine, transaction processor, or arbitrary workload executor.

## Implemented capabilities

| Endpoint | Purpose | Side effects |
| --- | --- | --- |
| `GET /health` | Liveness and release metadata | None |
| `GET /api/v1/status` | Operating-mode and integration status | None |
| `GET /api/v1/pipelines` | Published pipeline catalog | None |
| `POST /api/v1/routing/plan` | Validates a workload request and returns a suggested route | None; planning only |

The service rejects malformed JSON and oversized request bodies. Browser-origin access is disabled by default and can be restricted with `CORS_ALLOWED_ORIGINS` when a browser client is introduced.

## Local run

Create a virtual environment, install dependencies, and start the service:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
```

For local development only, `python app.py` is also supported. Do not use Flask development mode for a public deployment.

## Configuration

Copy `.env.example` to your deployment provider’s environment configuration. `APP_VERSION` is optional. Set `CORS_ALLOWED_ORIGINS` only to the exact HTTPS origins that need browser access. No banking, payment, or provider credentials belong in this repository.

## Release checks

Before releasing, run:

```bash
gunicorn --check-config app:app
curl http://127.0.0.1:5000/health
```

A platform is ready to handle real transactions only after a separately approved, authenticated settlement integration, durable audit storage, authorization controls, webhook verification, rate limiting, and operational monitoring have been implemented and tested.

## Ownership

Unauthorized copying, distribution, modification, or commercial utilization of this utility system or its pipelines without explicit written consent from the owner is prohibited.
