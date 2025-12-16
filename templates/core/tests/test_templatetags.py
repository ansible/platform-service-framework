"""Tests for core template tags."""

import pytest
from django.test import RequestFactory, TestCase

from apps.core.templatetags.core_tags import login_link, logout_link, script_name


def _patch_get_full_path_with_prefix(request, prefix):
    """Simulate the middleware's patching of get_full_path to prepend a prefix."""
    original_get_full_path = request.get_full_path

    def patched_get_full_path(force_append_slash=False):
        return prefix + original_get_full_path(force_append_slash)

    request.get_full_path = patched_get_full_path


def _patch_get_full_path_api_prefix(request, api_prefix):
    """Simulate the middleware's patching for /api/<service>/... URLs."""
    original_get_full_path = request.get_full_path

    def patched_get_full_path(force_append_slash=False):
        canonical = original_get_full_path(force_append_slash)
        if canonical.startswith(("/api/", "/api?")):
            return api_prefix + canonical[4:]
        return canonical

    request.get_full_path = patched_get_full_path


class TestScriptNameTag(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_script_name_returns_slash_when_empty(self):
        request = self.factory.get("/")
        request.META["SCRIPT_NAME"] = ""
        result = script_name(request)
        self.assertEqual(result, "/")

    def test_script_name_returns_prefix_with_trailing_slash(self):
        request = self.factory.get("/")
        request.META["SCRIPT_NAME"] = "/api/my-service"
        result = script_name(request)
        self.assertEqual(result, "/api/my-service/")

    def test_script_name_preserves_trailing_slash(self):
        request = self.factory.get("/")
        request.META["SCRIPT_NAME"] = "/api/my-service/"
        result = script_name(request)
        self.assertEqual(result, "/api/my-service/")


class TestLoginLogoutLinks(TestCase):
    """Test login/logout link generation."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_login_link_generates_correct_html(self):
        request = self.factory.get("/some/path/")
        request.META["SCRIPT_NAME"] = ""
        result = login_link(request)
        self.assertIn("Log in", result)
        self.assertIn("/api-auth/login/", result)
        self.assertIn("next=/some/path/", result)

    def test_logout_link_generates_correct_html(self):
        request = self.factory.get("/")
        request.META["SCRIPT_NAME"] = ""
        result = logout_link(request, "testuser", "csrf-token-123")
        self.assertIn("testuser", result)
        self.assertIn("Log out", result)
        self.assertIn("/api-auth/logout/", result)
        self.assertIn("csrf-token-123", result)


# Test parameters for full path generation
# (request_path, prefix_to_patch, expected_in_result)
FULL_PATH_PATTERNS = [
    pytest.param(
        "/some/path/",
        None,  # No patching needed
        "/some/path/",
        id="canonical-no-prefix",
    ),
    pytest.param(
        "/api/v1/",
        None,
        "/api/v1/",
        id="api-canonical",
    ),
    pytest.param(
        "/api/v1/",
        "/my-service",  # Service prefix (prepend)
        "/my-service/api/v1/",
        id="service-prefix",
    ),
    pytest.param(
        "/api/v1/",
        "/api/my-service",  # API service prefix (replace /api/)
        "/api/my-service/v1/",
        id="api-service-prefix",
    ),
]


@pytest.mark.django_db
class TestFullPathGeneration:
    """Test that login/logout links include correct paths for all access patterns."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = RequestFactory()

    def _create_request(self, path, prefix):
        """Create a request with appropriate patching based on prefix type."""
        request = self.factory.get(path)
        request.META["SCRIPT_NAME"] = ""

        if prefix is None:
            # No patching - canonical request
            pass
        elif prefix.startswith("/api/"):
            # API service prefix - replace /api/ with /api/<service>/
            request._api_service_prefix = prefix
            _patch_get_full_path_api_prefix(request, prefix)
        else:
            # Service prefix - prepend /<service>/
            request.META["SCRIPT_NAME"] = prefix
            _patch_get_full_path_with_prefix(request, prefix)

        return request

    @pytest.mark.parametrize("request_path,prefix,expected", FULL_PATH_PATTERNS)
    def test_login_link_path(self, request_path, prefix, expected):
        """Login link includes correct path."""
        request = self._create_request(request_path, prefix)
        result = login_link(request)
        assert f"next={expected}" in result, f"Expected 'next={expected}' in {result}"

    @pytest.mark.parametrize("request_path,prefix,expected", FULL_PATH_PATTERNS)
    def test_logout_link_path(self, request_path, prefix, expected):
        """Logout link includes correct path."""
        request = self._create_request(request_path, prefix)
        result = logout_link(request, "user", "token")
        assert f"next={expected}" in result, f"Expected 'next={expected}' in {result}"
