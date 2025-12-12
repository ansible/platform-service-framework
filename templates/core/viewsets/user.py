from ansible_base.rbac.api.permissions import AnsibleBaseUserPermissions
from ansible_base.rbac.policies import visible_users
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.models import User
from apps.core.serializers import UserSerializer

from .base import BaseViewSet


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AnsibleBaseUserPermissions]

    def filter_queryset(self, qs):
        qs = visible_users(self.request.user, queryset=qs)
        return super(BaseViewSet, self).filter_queryset(qs)

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
