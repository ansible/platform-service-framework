from ansible_base.lib.utils.views.ansible_base import AnsibleBaseView
from django.contrib.admindocs.views import simplify_regex
from django.urls import URLPattern, URLResolver, get_resolver
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class APIRootView(AnsibleBaseView):
    """
    Dynamically discovers and lists available API endpoints.

    Introspects the URL configuration to find all registered endpoints.
    Shows only direct children under the current path (not all descendants).
    Uses the same traversal order as Django's URL resolver, so the first
    matching pattern wins (like `show_urls --unsorted`).

    Usage:
        path('v1/', APIRootView.as_view(view_name='v1'), name='v1-root'),
        path('', APIRootView.as_view(view_name='my_project'), name='index'),
    """

    permission_classes = [AllowAny]
    view_name = None  # Set via as_view(view_name="...")

    def get_view_name(self):
        """Return the view name for breadcrumbs."""
        if self.view_name:
            return self.view_name
        # Fallback to default
        return "API Root"

    def get(self, request):
        resolver = get_resolver()

        # Derive prefix from request path (e.g., '/v1/' -> '/v1/')
        prefix = request.path if request.path.startswith("/") else "/" + request.path

        # Get the current view's URL name to exclude it from results
        current_url_name = getattr(request.resolver_match, "url_name", None)

        # Collect all patterns in traversal order (like show_urls --unsorted)
        all_patterns = list(self._extract_patterns(resolver.url_patterns, ""))

        # Track seen paths - first occurrence wins (matches Django routing)
        seen_paths = set()
        endpoints = {}

        for clean_path, pattern_name in all_patterns:
            # Must start with our prefix
            if not clean_path.startswith(prefix):
                continue

            # Get the path relative to our prefix
            relative_path = clean_path[len(prefix) :]

            # Skip empty relative path (this is the index itself)
            if not relative_path or relative_path == "/":
                continue

            # Skip debug toolbar and similar internal paths
            if "__debug__" in relative_path or relative_path.startswith("_"):
                continue

            # Extract the first path segment (direct child)
            first_segment = relative_path.strip("/").split("/")[0]

            # Skip if first segment has parameters like <pk>
            if "<" in first_segment:
                continue

            # Skip index views
            if pattern_name and (pattern_name.endswith("-index") or pattern_name == "api-root"):
                continue

            # Skip the current view itself
            if pattern_name == current_url_name:
                continue

            # First occurrence wins - skip if we've seen this path
            if first_segment in seen_paths:
                continue
            seen_paths.add(first_segment)

            # Build the URL for this direct child
            # Check for API service prefix (set by ServicePrefixMiddleware for /api/<service>/...)
            # or fall back to SCRIPT_NAME (set for /<service>/...)
            api_service_prefix = getattr(request, "_api_service_prefix", None)
            if api_service_prefix:
                # For /api/<service>/... URLs, use the stored API prefix
                child_url = request.build_absolute_uri(
                    api_service_prefix + prefix[len("/api") :] + first_segment + "/"
                )
            else:
                # For /<service>/... URLs, SCRIPT_NAME is already set
                script_name = request.META.get("SCRIPT_NAME", "")
                child_url = request.build_absolute_uri(script_name + prefix + first_segment + "/")

            # Use the path segment as the name (cleaner than pattern names)
            endpoints[first_segment] = child_url

        # Sort alphabetically for consistent output
        return Response(dict(sorted(endpoints.items())))

    def _extract_patterns(self, patterns, current_path):
        """
        Recursively extract URL patterns in traversal order.
        Yields (clean_path, pattern_name) tuples.
        """
        for pattern in patterns:
            raw_path = current_path + str(pattern.pattern)
            clean_path = simplify_regex(raw_path)

            if isinstance(pattern, URLResolver):
                # Yield the resolver path itself (for section detection)
                yield (clean_path, None)
                # Recurse into nested patterns
                yield from self._extract_patterns(pattern.url_patterns, raw_path)
            elif isinstance(pattern, URLPattern):
                # Yield leaf pattern with its name
                yield (clean_path, pattern.name)
