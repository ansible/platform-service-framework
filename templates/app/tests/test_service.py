from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings


# Create your tests here.


class TestService(TestCase):
    def test_service(self):
        self.assertTrue(settings.FOO, "batata")
        self.assertTrue(True)

    @override_settings(FOO="new value")
    def test_with_overriden_settings(self):
        self.assertEqual(settings.FOO, "new value")
