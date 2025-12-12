from ansible_base.lib.utils.views.ansible_base import AnsibleBaseView
from ansible_base.rbac import permission_registry
from ansible_base.rbac.api.permissions import AnsibleBaseObjectPermissions
from rest_framework.viewsets import ModelViewSet


class BaseViewSet(ModelViewSet, AnsibleBaseView):
    """Base viewset with RBAC filtering."""

    permission_classes = [AnsibleBaseObjectPermissions]

    def filter_queryset(self, queryset):
        cls = queryset.model
        if permission_registry.is_registered(cls):
            queryset = cls.access_qs(self.request.user, queryset=queryset)
        return super().filter_queryset(queryset)
