import unittest

from app import create_app


class HoudiniProTests(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_health_is_operational(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["service"], "Houdini Pro Utility")
        self.assertEqual(response.json["status"], "operational")

    def test_pipeline_catalog_is_available(self):
        response = self.client.get("/api/v1/pipelines")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["count"], 3)

    def test_plan_route_is_non_executing(self):
        response = self.client.post(
            "/api/v1/routing/plan",
            json={"workload_type": "reporting", "priority": "critical"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["recommended_pipeline"], "throughput")
        self.assertEqual(response.json["execution"], "not_started")

    def test_invalid_plan_is_rejected(self):
        response = self.client.post(
            "/api/v1/routing/plan",
            json={"workload_type": "", "priority": "unknown"},
        )
        self.assertEqual(response.status_code, 400)

    def test_unknown_endpoint_is_json_404(self):
        response = self.client.get("/unknown")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["status"], "error")


if __name__ == "__main__":
    unittest.main()
