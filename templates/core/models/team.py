from ansible_base.lib.abstract_models.team import AbstractTeam
from django.db import models


class Team(AbstractTeam):
    """
    Team model using DAB's AbstractTeam.

    Teams belong to organizations and group users for access control.
    The organization FK is inherited from AbstractTeam and uses
    settings.ANSIBLE_BASE_ORGANIZATION_MODEL.
    """

    objects = models.Manager()

    class Meta:
        permissions = [("member_team", "Has all roles assigned to this team")]
