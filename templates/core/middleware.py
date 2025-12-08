"""
Service prefix middleware.

Allows the service to be accessed at both:
- / (root)
- /api/<service-name>/

When accessed via the service prefix, SCRIPT_NAME is set so that
reverse() and all URLs work correctly.
"""

from django.conf import settings
from django.urls import set_script_prefix


class ServicePrefixMiddleware:
    """
    Middleware that handles /api/<service-name>/ prefix.

    When a request comes in with the service prefix, it:
    1. Strips the prefix from PATH_INFO
    2. Sets SCRIPT_NAME to the prefix

    This makes Django think it's being served at that prefix,
    so reverse() generates correct URLs.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Get service name from ROOT_URLCONF (e.g., "test_service" -> "test-service")
        self.service_name = settings.ROOT_URLCONF.split(".")[0].replace("_", "-")
        self.prefix = f"/api/{self.service_name}"

    def __call__(self, request):
        path = request.path_info

        # If path starts with the service prefix, strip it and set SCRIPT_NAME
        if path.startswith(self.prefix):
            # Remove prefix from path
            new_path = path[len(self.prefix) :] or "/"
            request.path_info = new_path
            request.path = new_path
            # Set SCRIPT_NAME so reverse() works correctly
            request.META["SCRIPT_NAME"] = self.prefix
            # Set script prefix for Django's reverse()
            set_script_prefix(self.prefix)
            # Also update environ for WSGI compatibility
            if hasattr(request, "environ"):
                request.environ["SCRIPT_NAME"] = self.prefix
                request.environ["PATH_INFO"] = new_path

        return self.get_response(request)
