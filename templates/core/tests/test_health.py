from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class TestPingEndpoint(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_ping_returns_pong(self):
        response = self.client.get("/ping/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"ping": "pong"})


class TestHealthEndpoint(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_returns_healthy(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data["checks"])
        self.assertEqual(data["checks"]["database"], "ok")
