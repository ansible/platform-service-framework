from django.urls import get_resolver

from apps.core.views import APIRootView


class APIRootViewMiddleware:
    """
    Middleware that serves an endpoint index for any path ending in '/'
    that would otherwise 404 but has child routes registered.

    This allows automatic index pages at any level of the URL hierarchy
    without explicitly registering them.

    Example:
        - /v2/ would show an index if there are routes under /v2/*
        - /some/deep/path/ would show an index if children exist
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only intercept 404s for paths ending with /
        if response.status_code == 404 and request.path.endswith("/"):
            if self._has_child_routes(request.path):
                # Serve the endpoint index view
                view = APIRootView.as_view()
                index_response = view(request)
                # Render the response if needed (DRF responses need rendering)
                if hasattr(index_response, "render"):
                    index_response.render()
                return index_response

        return response

    def _has_child_routes(self, path):
        """Check if there are any routes under the given path."""
        prefix = path.lstrip("/")
        resolver = get_resolver()

        def check_patterns(patterns, current_path=""):
            for pattern in patterns:
                full_path = current_path + str(pattern.pattern)

                # Check if this pattern is under our prefix
                if full_path.startswith(prefix) and full_path != prefix:
                    # Found a child route
                    return True

                # Recurse into includes
                if hasattr(pattern, "url_patterns"):
                    if check_patterns(pattern.url_patterns, full_path):
                        return True

            return False

        return check_patterns(resolver.url_patterns)
