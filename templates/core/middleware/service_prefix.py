"""
Service prefix middleware.

Allows the service to be accessed with a /<service-name> prefix:
- /api/<service-name>/v1/users → /api/v1/users
- /<service-name>/ping → /ping

For the /api/<service-name> case, no SCRIPT_NAME is set so reverse()
generates canonical /api/... URLs.

For the /<service-name> case, SCRIPT_NAME is set so reverse()
generates /<service-name>/... URLs.
"""

from django.conf import settings
from django.urls import set_script_prefix


def _has_prefix(path, prefix):
    """Check if path starts with prefix at a segment boundary.

    Returns True if path equals prefix or starts with prefix followed by '/'.
    This prevents '/metrics-servicefoo' from matching prefix '/metrics-service'.
    """
    return path == prefix or path.startswith(prefix + "/")


class ServicePrefixMiddleware:
    """
    Middleware that handles /<service-name> prefix in URLs.

    Two routing modes:
    1. /api/<service-name>/... → /api/... (no SCRIPT_NAME, canonical URLs)
    2. /<service-name>/... → /... (SCRIPT_NAME set for prefixed URLs)
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Get service name from ROOT_URLCONF (e.g., "test_service" -> "test-service")
        self.service_name = settings.ROOT_URLCONF.split(".")[0].replace("_", "-")
        self.service_prefix = f"/{self.service_name}"

    def __call__(self, request):
        path = request.path_info

        # Handle /api/<service-name>/... → /api/...
        # No SCRIPT_NAME set - reverse() generates canonical /api/... URLs
        # Store the API prefix so views can build correct absolute URLs
        # Store original path for DRF breadcrumbs
        # Patch get_full_path to return the original path for templates
        api_prefix = f"/api{self.service_prefix}"
        if _has_prefix(path, api_prefix):
            request._original_path = path
            request._api_service_prefix = api_prefix
            new_path = "/api" + path[len(api_prefix) :] or "/api/"
            request.path_info = new_path
            request.path = new_path
            if hasattr(request, "environ"):
                request.environ["PATH_INFO"] = new_path

            # Patch get_full_path to return the original prefixed path
            # This ensures DRF templates show correct URLs for forms/links
            original_get_full_path = request.get_full_path

            def patched_get_full_path(force_append_slash=False):
                # Get the canonical path and replace /api/ with /api/<service>/
                canonical = original_get_full_path(force_append_slash)
                if canonical.startswith(("/api/", "/api?")):
                    return api_prefix + canonical[4:]  # len("/api") = 4
                return canonical

            request.get_full_path = patched_get_full_path
        # Handle /<service-name>/... → /...
        # Set SCRIPT_NAME so reverse() generates /<service-name>/... URLs
        elif _has_prefix(path, self.service_prefix):
            # Store original path for DRF breadcrumbs
            request._original_path = path
            new_path = path[len(self.service_prefix) :] or "/"
            request.path_info = new_path
            request.path = new_path
            request.META["SCRIPT_NAME"] = self.service_prefix
            set_script_prefix(self.service_prefix)
            if hasattr(request, "environ"):
                request.environ["SCRIPT_NAME"] = self.service_prefix
                request.environ["PATH_INFO"] = new_path

            # Patch get_full_path to return the original prefixed path
            # Django's get_full_path() doesn't include SCRIPT_NAME
            service_prefix = self.service_prefix
            original_get_full_path = request.get_full_path

            def patched_get_full_path(force_append_slash=False):
                return service_prefix + original_get_full_path(force_append_slash)

            request.get_full_path = patched_get_full_path

        return self.get_response(request)
