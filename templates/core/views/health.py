import logging

from ansible_base.lib.utils.views.ansible_base import AnsibleBaseView
from django.db import connection
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class HealthView(AnsibleBaseView):
    """
    Health check endpoint to verify service health.

    Checks database connectivity and returns overall health status.

    Extensions that add service-specific checks must return sanitized status
    values. Health responses are public and must not expose exception details,
    connection strings, or other internal implementation data.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        health_status: dict = {"status": "healthy", "checks": {}}

        # Database check
        try:
            connection.ensure_connection()
            health_status["checks"]["database"] = "ok"
        except Exception:
            logger.exception("Health check database connection failed")
            health_status["status"] = "unhealthy"
            health_status["checks"]["database"] = "error"

        http_status = (
            status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(health_status, status=http_status)
