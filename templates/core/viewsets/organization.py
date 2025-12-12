from apps.core.models import Organization
from apps.core.serializers import OrganizationSerializer

from .base import BaseViewSet


class OrganizationViewSet(BaseViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
