from ansible_base.lib.utils.views.ansible_base import AnsibleBaseView
from django.db import connection
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class HealthView(AnsibleBaseView):
    """
    Health check endpoint to verify service health.

    Checks database connectivity and returns overall health status.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        health_status: dict = {"status": "healthy", "checks": {}}

        # Database check
        try:
            connection.ensure_connection()
            health_status["checks"]["database"] = "ok"
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["checks"]["database"] = f"error: {str(e)}"

        http_status = (
            status.HTTP_200_OK
            if health_status["status"] == "healthy"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(health_status, status=http_status)
