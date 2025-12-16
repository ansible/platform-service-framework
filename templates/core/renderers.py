"""Custom DRF renderers for the core app."""

from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.utils.breadcrumbs import get_breadcrumbs


class ServiceBrowsableAPIRenderer(BrowsableAPIRenderer):
    """
    Custom BrowsableAPIRenderer that handles service prefix correctly.

    Handles two prefix cases from ServicePrefixMiddleware:
    - SCRIPT_NAME: set for /<service>/... URLs (handled by DRF natively)
    - _api_service_prefix: set for /api/<service>/... URLs (needs custom handling)

    For the /api/<service>/... case, we generate breadcrumbs using the
    rewritten path (/api/...) and then fix up the URLs to include the
    service prefix.
    """

    def get_breadcrumbs(self, request):
        # Check for API service prefix (set by ServicePrefixMiddleware for /api/<service>/...)
        api_service_prefix = getattr(request, "_api_service_prefix", None)

        if api_service_prefix:
            # For /api/<service>/... URLs:
            # 1. Generate breadcrumbs using the rewritten path (/api/...)
            # 2. Fix up URLs to include the service prefix
            breadcrumbs = get_breadcrumbs(request.path, request)

            # Replace /api/ with /api/<service>/ in all breadcrumb URLs
            fixed_breadcrumbs = []
            for name, url in breadcrumbs:
                if url.startswith("/api/"):
                    url = api_service_prefix + url[4:]  # len("/api") = 4
                fixed_breadcrumbs.append((name, url))
            return fixed_breadcrumbs

        # For /<service>/... URLs, use original path (SCRIPT_NAME handles the rest)
        path = getattr(request, "_original_path", request.path)
        return get_breadcrumbs(path, request)
