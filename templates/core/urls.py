from django.urls import include, path

from .router import router
from .views import HealthView, PingView

urlpatterns = [
    path("ping/", PingView.as_view(), name="ping"),
    path("health/", HealthView.as_view(), name="health"),
    path("v1/", include(router.urls)),
]
