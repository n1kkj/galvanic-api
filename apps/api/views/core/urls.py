from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.api.views.core import MachineViewSet, SensorViewSet

app_name = "core"

router = DefaultRouter()
router.register("machines", MachineViewSet, basename="machines")
router.register("sensors", SensorViewSet, basename="sensors")

urlpatterns = [
    path("", include(router.urls)),
]
