"""Houdini Pro Utility service.

This service exposes operational status and deterministic routing-plan validation.
It deliberately does not execute financial transfers, transactions, or arbitrary jobs.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

APP_NAME = "Houdini Pro Utility"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
VALID_PRIORITIES = {"standard", "expedited", "critical"}
PIPELINES = (
    {
        "id": "isolation",
        "name": "Isolation Pipeline",
        "purpose": "Separates validated workload classes before downstream handling.",
        "state": "ready",
    },
    {
        "id": "throughput",
        "name": "Throughput Pipeline",
        "purpose": "Plans high-volume execution workloads after validation.",
        "state": "ready",
    },
    {
        "id": "performance",
        "name": "Performance Pipeline",
        "purpose": "Reports capacity and operating mode without accessing customer data.",
        "state": "ready",
    },
)


def _allowed_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _error(message: str, status: int) -> tuple[Any, int]:
    return jsonify({"status": "error", "message": message}), status


def create_app() -> Flask:
    """Create the HTTP application without enabling development-only settings."""
    app = Flask(__name__)
    app.config.update(JSON_SORT_KEYS=False, MAX_CONTENT_LENGTH=16 * 1024)

    origins = _allowed_origins()
    if origins:
        CORS(app, resources={r"/api/*": {"origins": origins}}, methods=["GET", "POST"])

    @app.get("/health")
    def health_check() -> tuple[Any, int]:
        return jsonify(
            {
                "service": APP_NAME,
                "version": APP_VERSION,
                "status": "operational",
                "timestamp": _timestamp(),
            }
        ), 200

    @app.get("/api/v1/status")
    def service_status() -> tuple[Any, int]:
        return jsonify(
            {
                "service": APP_NAME,
                "version": APP_VERSION,
                "operating_mode": os.getenv("HOUDINI_OPERATING_MODE", "balanced"),
                "transaction_processing": "not_configured",
                "timestamp": _timestamp(),
            }
        ), 200

    @app.get("/api/v1/pipelines")
    def list_pipelines() -> tuple[Any, int]:
        return jsonify({"count": len(PIPELINES), "pipelines": PIPELINES}), 200

    @app.post("/api/v1/routing/plan")
    def plan_route() -> tuple[Any, int]:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return _error("A JSON object is required.", 400)

        workload_type = data.get("workload_type")
        priority = data.get("priority", "standard")
        if not isinstance(workload_type, str) or not workload_type.strip() or len(workload_type) > 80:
            return _error("workload_type must be a non-empty string of at most 80 characters.", 400)
        if priority not in VALID_PRIORITIES:
            return _error("priority must be one of: standard, expedited, critical.", 400)

        route = "throughput" if priority in {"expedited", "critical"} else "isolation"
        return jsonify(
            {
                "status": "planned",
                "request_id": str(uuid.uuid4()),
                "workload_type": workload_type.strip(),
                "priority": priority,
                "recommended_pipeline": route,
                "execution": "not_started",
                "notice": "This endpoint validates and plans only; it does not execute a workload or move funds.",
                "timestamp": _timestamp(),
            }
        ), 200

    @app.errorhandler(404)
    def not_found(_: Any) -> tuple[Any, int]:
        return _error("The requested resource was not found.", 404)

    @app.errorhandler(413)
    def request_too_large(_: Any) -> tuple[Any, int]:
        return _error("Request body exceeds the 16 KB limit.", 413)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
