"""Tests for core middleware."""

import pytest
from django.conf import settings
from django.test import TestCase
from django.urls import set_script_prefix
from rest_framework import status
from rest_framework.test import APIClient


def get_service_name():
    """Get the service name from settings."""
    return settings.ROOT_URLCONF.split(".")[0].replace("_", "-")


# Test parameters for the three URL access patterns
SERVICE_NAME = get_service_name()
URL_PATTERNS = [
    pytest.param(
        f"/api/v1/",
        None,  # No prefix expected
        id="canonical",
    ),
    pytest.param(
        f"/{SERVICE_NAME}/api/v1/",
        f"/{SERVICE_NAME}/",
        id="service-prefix",
    ),
    pytest.param(
        f"/api/{SERVICE_NAME}/v1/",
        f"/api/{SERVICE_NAME}/",
        id="api-service-prefix",
    ),
]


class TestServicePrefixMiddleware(TestCase):
    """Tests for ServicePrefixMiddleware.

    Two routing modes:
    1. /api/<service-name>/... → /api/... (no SCRIPT_NAME, canonical URLs)
    2. /<service-name>/... → /... (SCRIPT_NAME set for prefixed URLs)
    """

    def setUp(self):
        self.client = APIClient()
        self.service_name = get_service_name()

    def tearDown(self):
        # Reset script prefix to avoid affecting other tests
        set_script_prefix("/")

    def test_request_without_prefix_works(self):
        """Direct requests without service prefix work normally."""
        response = self.client.get("/ping/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_with_api_service_prefix_routes_to_api(self):
        """/api/<service-name>/v1/ routes to /api/v1/."""
        response = self.client.get(f"/api/{self.service_name}/v1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_service_prefix_preserves_prefix_in_urls(self):
        """/api/<service-name>/... generates URLs with the service prefix."""
        response = self.client.get(f"/api/{self.service_name}/v1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # URLs should include the service prefix
        for url in data.values():
            self.assertIn(f"/api/{self.service_name}/v1/", url)

    def test_api_service_prefix_root_returns_prefixed_urls(self):
        """/api/<service-name>/ returns URLs with the service prefix."""
        response = self.client.get(f"/api/{self.service_name}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Should have v1 endpoint
        self.assertIn("v1", data)
        # v1 URL should include service prefix
        self.assertIn(f"/api/{self.service_name}/v1/", data["v1"])

    def test_request_with_service_prefix_routes_to_root(self):
        """/<service-name>/ping/ routes to /ping/."""
        response = self.client.get(f"/{self.service_name}/ping/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"ping": "pong"})

    def test_service_prefix_sets_script_name(self):
        """/<service-name>/... sets SCRIPT_NAME so URLs include the prefix."""
        response = self.client.get(f"/{self.service_name}/api/v1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # URLs should include the service prefix
        for url in data.values():
            self.assertIn(f"/{self.service_name}/", url)


class TestAPIRootViewMiddleware(TestCase):
    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        # Reset script prefix to avoid affecting other tests
        set_script_prefix("/")

    def test_middleware_serves_index_for_404_with_children(self):
        # /api/v1/ has child routes, so even if it were a 404, middleware would serve index
        response = self.client.get("/api/v1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_trailing_slash_404_not_intercepted(self):
        # Paths not ending in / should not be intercepted
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_404_without_children_not_intercepted(self):
        # A path with no child routes should remain 404
        response = self.client.get("/completely/fake/path/with/no/children/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
class TestBrowsableAPIURLs:
    """Test that all URLs in the browsable API are correct for all access patterns.

    Tests three access patterns:
    1. /api/v1/                       → canonical URLs (no prefix)
    2. /<service>/api/v1/             → prefixed URLs (/<service>/...)
    3. /api/<service>/v1/             → prefixed URLs (/api/<service>/...)

    For each pattern, verifies:
    - Breadcrumb URLs
    - Form action URLs
    - GET button href
    - Request info path display
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.service_name = SERVICE_NAME
        set_script_prefix("/")
        yield
        set_script_prefix("/")

    def _get_html_content(self, path):
        """Get HTML response content."""
        response = self.client.get(path, HTTP_ACCEPT="text/html")
        assert response.status_code == status.HTTP_200_OK
        return response.content.decode("utf-8")

    def _extract_breadcrumbs(self, content):
        """Extract breadcrumb URLs from HTML content."""
        import re

        breadcrumb_match = re.search(
            r'<ul class="breadcrumb"[^>]*>(.*?)</ul>', content, re.DOTALL
        )
        if breadcrumb_match:
            breadcrumb_html = breadcrumb_match.group(1)
            return re.findall(r'href="([^"]+)"', breadcrumb_html)
        return []

    def _extract_form_actions(self, content):
        """Extract form action URLs from HTML content."""
        import re

        return re.findall(r'action="([^"]+)"', content)

    def _extract_request_info_path(self, content):
        """Extract the path shown in request info (e.g., 'GET /api/v1/')."""
        import re

        match = re.search(r"<b>GET</b>\s+([^\s<]+)", content)
        return match.group(1) if match else None

    def _extract_get_button_href(self, content):
        """Extract the GET button href."""
        import re

        match = re.search(r'href="([^"]+)"[^>]*>\s*GET\s*</a>', content)
        return match.group(1) if match else None

    def _assert_urls_have_correct_prefix(self, urls, expected_prefix):
        """Assert that URLs have the correct prefix (or no prefix if None)."""
        api_urls = [url for url in urls if "/api" in url]
        assert len(api_urls) > 0, f"Expected API URLs, got: {urls}"

        for url in api_urls:
            if expected_prefix is None:
                # Canonical - should not contain service name
                assert f"/{self.service_name}/" not in url, f"URL {url} should not have service prefix"
            else:
                # Prefixed - should contain the expected prefix
                assert expected_prefix in url, f"URL {url} should contain {expected_prefix}"

    @pytest.mark.parametrize("path,expected_prefix", URL_PATTERNS)
    def test_breadcrumbs(self, path, expected_prefix):
        """Breadcrumb URLs have correct prefix."""
        content = self._get_html_content(path)
        breadcrumbs = self._extract_breadcrumbs(content)
        assert len(breadcrumbs) > 0, "Expected breadcrumbs"
        self._assert_urls_have_correct_prefix(breadcrumbs, expected_prefix)

    @pytest.mark.parametrize("path,expected_prefix", URL_PATTERNS)
    def test_form_actions(self, path, expected_prefix):
        """Form action URLs have correct prefix."""
        content = self._get_html_content(path)
        form_actions = self._extract_form_actions(content)
        self._assert_urls_have_correct_prefix(form_actions, expected_prefix)

    @pytest.mark.parametrize("path,expected_prefix", URL_PATTERNS)
    def test_get_button(self, path, expected_prefix):
        """GET button href has correct prefix."""
        content = self._get_html_content(path)
        get_href = self._extract_get_button_href(content)
        assert get_href is not None, "GET button href not found"
        self._assert_urls_have_correct_prefix([get_href], expected_prefix)

    @pytest.mark.parametrize("path,expected_prefix", URL_PATTERNS)
    def test_request_info_path(self, path, expected_prefix):
        """Request info path display has correct prefix."""
        content = self._get_html_content(path)
        request_path = self._extract_request_info_path(content)
        assert request_path is not None, "Request info path not found"
        self._assert_urls_have_correct_prefix([request_path], expected_prefix)
