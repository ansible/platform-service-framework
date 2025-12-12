from rest_framework.viewsets import ModelViewSet

from ansible_base.lib.utils.views.ansible_base import AnsibleBaseView
from ansible_base.rbac import permission_registry
from ansible_base.rbac.api.permissions import AnsibleBaseObjectPermissions


class BaseViewSet(ModelViewSet, AnsibleBaseView):
    """Base viewset with RBAC filtering."""

    permission_classes = [AnsibleBaseObjectPermissions]

    def filter_queryset(self, qs):
        cls = qs.model
        if permission_registry.is_registered(cls):
            qs = cls.access_qs(self.request.user, queryset=qs)
        return super().filter_queryset(qs)
