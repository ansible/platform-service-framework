"""
URL configuration for the apps package.

This file serves as the primary location for adding custom URL patterns to your
service. Since the top-level urls.py is managed by the platform-service-framework
and should not be modified directly, use this file for any custom URLs your
service needs.

## LOADED_APPS Mechanism

The framework dynamically discovers and loads URL patterns from apps:

1. **App registration**: Apps are registered in `apps/settings.py` under the
   `project_applications` list (e.g., ["apps.core", "apps.api"]).

2. **Discovery**: At runtime, the framework filters `INSTALLED_APPS` for entries
   that start with "apps." and have a corresponding directory in the apps folder.

3. **LOADED_APPS population**: The filtered list becomes `settings.LOADED_APPS`,
   preserving the order defined in `project_applications`.

4. **URL loading**: The framework iterates through LOADED_APPS and imports each
   app's urls.py, appending patterns to the main urlpatterns.

## Controlling URL Loading Order

Django uses first-match routing, so loading order determines which pattern
handles a request when multiple patterns could match.

**Example conflict**: If both `apps.core` and `apps.api` define a pattern for
`api/v1/users/`, only the first-loaded app's pattern will handle requests.
The other pattern becomes unreachable.

You have two options to control this:

### Option 1: Reorder apps in `project_applications`

The URL loading order follows the order in `project_applications` in
`apps/settings.py`. Reordering apps there changes their URL loading order.

- If `project_applications = ["apps.core", "apps.api"]`, core's URLs load first
- If two apps define the same URL pattern, the first one in the list wins

**Trade-offs**:
- Changing app order affects settings loading order (each app's settings.py
  is loaded in this order)
- This changes URL loading order for ALL URLs in the app - you cannot load
  a single URL from app B before app A while keeping the rest of app B after

Use this when you want to change the overall priority of an entire app.

### Option 2: Use this file (apps/urls.py)

This file loads BEFORE all individual app URL patterns, giving you a way to
define URLs that are independent of app order. This provides finer control:

- Add a single high-priority URL without reordering apps
- Define URLs that don't belong to any specific app
- Override patterns from any app regardless of app order

Use this for service-level customizations, cross-app endpoints, or when you
need a specific URL to take priority without changing app order.

## Full URL Loading Order

1. Django Ansible Base URLs (DAB)
2. Dynamic API root view overrides
3. >>> This file (apps/urls.py) <<<  -- BEFORE individual apps
4. Individual app URL patterns (order from project_applications in apps/settings.py)
5. Debug/development URLs

## Example Usage

    from django.urls import path
    from apps.core.views import SomeView
    from apps.api.views import AnotherView

    urlpatterns = [
        # Service-specific endpoint
        path("api/v1/service-info/", ServiceInfoView.as_view(), name="service-info"),

        # Priority pattern - matches before any app patterns
        path("api/v1/critical/", CriticalView.as_view(), name="critical"),

        # Cross-app endpoint combining data from multiple apps
        path("api/v1/combined/", CombinedView.as_view(), name="combined"),
    ]

"""


urlpatterns = [
    # Define your service-specific, priority, or cross-app URL patterns here
]
