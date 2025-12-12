from ansible_base.lib.abstract_models.organization import AbstractOrganization


class Organization(AbstractOrganization):
    """
    Organization model using DAB's AbstractOrganization.

    Organizations serve as the top-level container for teams and resources.
    """

    class Meta:
        permissions = [('member_organization', 'User is member of this organization')]
