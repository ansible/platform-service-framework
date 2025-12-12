from ansible_base.lib.serializers.common import NamedCommonModelSerializer
from ansible_base.rbac.api.related import RelatedAccessMixin

from apps.core.models import Team


class TeamSerializer(RelatedAccessMixin, NamedCommonModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"
