"""
Testing environment overrides
Inherits from ./defaults.py and adds test-specific settings

NOTE: Tests use PostgreSQL to match the production environment setup.
"""

# Basic required settings
DEBUG = False
TESTING = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
SECRET_KEY = "test-only-secret-key-for-testing-purposes-only"

ANSIBLE_BASE_BYPASS_SUPERUSER_FLAGS = ["is_superuser"]
ANSIBLE_BASE_BYPASS_ACTION_FLAGS = {
    "create": "is_superuser",
    "read": "is_superuser",
    "update": "is_superuser",
    "delete": "is_superuser",
}

# Additional DAB RBAC settings required for tests
ANSIBLE_BASE_CHECK_RELATED_PERMISSIONS = ["use", "change", "view"]
ANSIBLE_BASE_CACHE_PARENT_PERMISSIONS = False
ANSIBLE_BASE_EVALUATIONS_IGNORE_CONFLICTS = False
ANSIBLE_BASE_DELETE_REQUIRE_CHANGE = False
ANSIBLE_BASE_CREATOR_DEFAULTS = ["add", "change", "delete", "view"]

# Service identification
SERVICE_ID = "test-service-id"

# Let Django create unique test database names automatically
DATABASES__default__TEST__NAME = None

# Disable caching during tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Use faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Email settings for testing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable logging during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
    },
}

# REST Framework settings for tests
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Test database settings
TEST_DATABASE_PREFIX = "test_"
