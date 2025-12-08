from django.urls import path

from .views import HealthView, IndexView, PingView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("ping/", PingView.as_view(), name="ping"),
    path("health/", HealthView.as_view(), name="health"),
]
