from django.test import TestCase

from apps.core.models import Organization, Team, User


class TestUserModel(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.assertEqual(str(user), "testuser")
        self.assertTrue(user.check_password("testpass123"))

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class TestOrganizationModel(TestCase):
    def test_create_organization(self):
        org = Organization.objects.create(name="Test Org")
        self.assertEqual(str(org), "Test Org")
        self.assertEqual(org.name, "Test Org")


class TestTeamModel(TestCase):
    def test_create_team(self):
        org = Organization.objects.create(name="Test Org")
        team = Team.objects.create(name="Test Team", organization=org)
        self.assertEqual(str(team), "Test Team")
        self.assertEqual(team.organization, org)

    def test_team_organization_relationship(self):
        org = Organization.objects.create(name="Test Org")
        team1 = Team.objects.create(name="Team 1", organization=org)
        team2 = Team.objects.create(name="Team 2", organization=org)
        self.assertEqual(org.teams.count(), 2)
        self.assertIn(team1, org.teams.all())
        self.assertIn(team2, org.teams.all())
