"""Custom authentication classes for the service."""

from ansible_base.jwt_consumer.common.auth import JWTAuthentication


class ServiceJWTAuthentication(JWTAuthentication):
    """JWT Authentication with RBAC permissions enabled."""

    use_rbac_permissions = True
