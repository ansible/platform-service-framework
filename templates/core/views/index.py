from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class IndexView(APIView):
    """
    API Index - shows all available endpoints.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response(
            {
                "ping": reverse("ping", request=request),
                "health": reverse("health", request=request),
                "service_index": reverse("service-index-root", request=request),
                "role_definitions": reverse("roledefinition-list", request=request),
                "docs": reverse("swagger-ui", request=request),
            }
        )
