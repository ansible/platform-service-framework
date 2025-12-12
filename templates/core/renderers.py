"""Custom DRF renderers for the core app."""

from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.utils.breadcrumbs import get_breadcrumbs


class ServiceBrowsableAPIRenderer(BrowsableAPIRenderer):
    """
    Custom BrowsableAPIRenderer that handles SCRIPT_NAME prefix correctly.

    When ServicePrefixMiddleware strips the prefix from request.path,
    it stores the original path in request._original_path. This renderer
    uses that original path for breadcrumb generation so DRF can correctly
    strip the SCRIPT_NAME prefix.
    """

    def get_breadcrumbs(self, request):
        # Use original path if available (set by ServicePrefixMiddleware)
        path = getattr(request, "_original_path", request.path)
        return get_breadcrumbs(path, request)
