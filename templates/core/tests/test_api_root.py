"""Tests for API root view."""

import pytest
from django.conf import settings
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


def get_service_name():
    """Get the service name from settings."""
    return settings.ROOT_URLCONF.split(".")[0].replace("_", "-")


SERVICE_NAME = get_service_name()

# Test parameters for JSON API root URL generation
# (path, expected_key, expected_prefix)
API_ROOT_URL_PATTERNS = [
    pytest.param("/", "api", None, id="root-canonical"),
    pytest.param(f"/{SERVICE_NAME}/", "api", f"/{SERVICE_NAME}/", id="root-service-prefix"),
    pytest.param("/api/", "v1", None, id="api-canonical"),
    pytest.param(f"/api/{SERVICE_NAME}/", "v1", f"/api/{SERVICE_NAME}/", id="api-service-prefix"),
]


class TestAPIRootView(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_root_returns_endpoints(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Should have some endpoints listed
        self.assertIsInstance(data, dict)

    def test_v1_root_returns_endpoints(self):
        response = self.client.get("/api/v1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, dict)
        # v1 should have organizations, teams, users endpoints
        self.assertIn("organizations", data)
        self.assertIn("teams", data)
        self.assertIn("users", data)

    def test_api_root_excludes_debug_paths(self):
        response = self.client.get("/")
        data = response.json()
        # Should not include __debug__ paths
        for key in data:
            self.assertNotIn("__debug__", key)

    def test_api_root_get_view_name(self):
        from apps.core.views import APIRootView

        # Test with custom view_name
        view = APIRootView()
        view.view_name = "Custom API"
        self.assertEqual(view.get_view_name(), "Custom API")

        # Test fallback
        view.view_name = None
        self.assertEqual(view.get_view_name(), "API Root")


@pytest.mark.django_db
class TestAPIRootViewURLGeneration:
    """Test that API root views generate correct URLs for all access patterns.

    Four access patterns:
    1. /                              → canonical URLs (no prefix)
    2. /<service-name>/               → prefixed URLs (/<service-name>/...)
    3. /api/                          → canonical URLs (no prefix)
    4. /api/<service-name>/           → prefixed URLs (/api/<service-name>/...)
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.service_name = SERVICE_NAME

    @pytest.mark.parametrize("path,expected_key,expected_prefix", API_ROOT_URL_PATTERNS)
    def test_json_urls_have_correct_prefix(self, path, expected_key, expected_prefix):
        """JSON response URLs have correct prefix."""
        response = self.client.get(path)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert expected_key in data, f"Expected key '{expected_key}' in response"

        url = data[expected_key]
        if expected_prefix is None:
            # Canonical - should not contain service name
            assert f"/{self.service_name}/" not in url, f"URL {url} should not have service prefix"
        else:
            # Prefixed - should contain the expected prefix
            assert expected_prefix in url, f"URL {url} should contain {expected_prefix}"
