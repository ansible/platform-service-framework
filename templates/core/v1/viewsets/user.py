from ansible_base.rbac.api.permissions import AnsibleBaseUserPermissions
from ansible_base.rbac.policies import visible_users
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.models import User
from apps.core.v1.serializers import UserSerializer

from .base import BaseViewSet


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AnsibleBaseUserPermissions]

    def filter_queryset(self, queryset):
        queryset = visible_users(self.request.user, queryset=queryset)
        return super(BaseViewSet, self).filter_queryset(queryset)

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
