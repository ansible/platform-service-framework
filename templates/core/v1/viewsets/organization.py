from apps.core.models import Organization
from apps.core.v1.serializers import OrganizationSerializer

from .base import BaseViewSet


class OrganizationViewSet(BaseViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
