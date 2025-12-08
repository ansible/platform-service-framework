from ansible_base.jwt_consumer.common.auth import JWTAuthentication


class ServiceJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication class for this service.

    Sets use_rbac_permissions=True to enable RBAC permission processing
    from JWT claims.
    """

    use_rbac_permissions = True
