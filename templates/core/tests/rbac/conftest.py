import uuid

import pytest
from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ansible_base.rbac import permission_registry
from ansible_base.rbac.models import RoleDefinition
from apps.core.models import Organization, Team

User = get_user_model()


@pytest.fixture(autouse=True)
def create_managed_roles(db):
    """Create managed roles for all tests."""
    permission_registry.create_managed_roles(apps)


@pytest.fixture
def rando(db):
    return User.objects.create(username=f'rando-{uuid.uuid4().hex[:8]}')


@pytest.fixture
def organization(db):
    return Organization.objects.create(name='Test Org')


@pytest.fixture
def team(db, organization):
    return Team.objects.create(name='Test Team', organization=organization)


@pytest.fixture
def org_admin_rd(db):
    return RoleDefinition.objects.get(name='Organization Admin')


@pytest.fixture
def org_member_rd(db):
    return RoleDefinition.objects.get(name='Organization Member')


@pytest.fixture
def team_admin_rd(db):
    return RoleDefinition.objects.get(name='Team Admin')


@pytest.fixture
def team_member_rd(db):
    return RoleDefinition.objects.get(name='Team Member')


@pytest.fixture
def admin_user(db):
    unique_id = uuid.uuid4().hex[:8]
    return User.objects.create_superuser(
        username=f'admin-{unique_id}',
        password=f'password-{unique_id}',
        email=f'admin-{unique_id}@test.com',
    )


@pytest.fixture
def user_api_client(rando):
    client = APIClient()
    client.force_authenticate(user=rando)
    return client


@pytest.fixture
def admin_api_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client
