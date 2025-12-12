"""Router configuration for core models."""

from ansible_base.lib.routers import AssociationResourceRouter

from apps.core.viewsets import OrganizationViewSet, TeamViewSet, UserViewSet

router = AssociationResourceRouter()

router.register(
    r"organizations",
    OrganizationViewSet,
    related_views={
        "teams": (TeamViewSet, "teams"),
    },
)

router.register(
    r"teams",
    TeamViewSet,
    related_views={
        "organization": (OrganizationViewSet, "organization"),
    },
)

router.register(
    r"users",
    UserViewSet,
    basename="user",
)
