"""
Core App Settings

This file contains settings specific to the core app.
These settings configure Django and DAB to use the core app's models.
"""

AUTH_USER_MODEL = "core.User"
ANSIBLE_BASE_ORGANIZATION_MODEL = "core.Organization"
ANSIBLE_BASE_TEAM_MODEL = "core.Team"

# Resource Registry Configuration
ANSIBLE_BASE_RESOURCE_CONFIG_MODULE = "apps.core.resource_api"

# RBAC Model Registry - register models for permission tracking
ANSIBLE_BASE_RBAC_MODEL_REGISTRY = {
    "core.Organization": {"parent_field_name": None},
    "core.Team": {"parent_field_name": "organization"},
    "core.User": {"parent_field_name": None},
}

# Authentication - insert JWT auth at position 0
REST_FRAMEWORK__DEFAULT_AUTHENTICATION_CLASSES = "@insert 0 apps.core.authentication.ServiceJWTAuthentication"

# Middleware - ServicePrefix at start, APIRootView at end
MIDDLEWARE = [
    "dynaconf_merge_unique",
    "apps.core.middleware.ServicePrefixMiddleware",
    "apps.core.middleware.APIRootViewMiddleware",
]
