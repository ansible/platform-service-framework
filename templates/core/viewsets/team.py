from apps.core.models import Team
from apps.core.serializers import TeamSerializer

from .base import BaseViewSet


class TeamViewSet(BaseViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
