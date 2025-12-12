from ansible_base.lib.abstract_models.user import AbstractDABUser


class User(AbstractDABUser):
    """
    Custom User model extending DAB's AbstractDABUser.

    This model can be extended with additional fields as needed.
    """

    encrypted_fields = ["password"]

    def related_fields(self, request):
        return {}

    def get_summary_fields(self):
        return {}
