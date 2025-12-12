from django.urls import include, path

from .v1 import urls as v1_urls
from .views import HealthView, PingView

urlpatterns = [
    path("ping/", PingView.as_view(), name="ping"),
    path("health/", HealthView.as_view(), name="health"),
    path("v1/", include(v1_urls)),
]
