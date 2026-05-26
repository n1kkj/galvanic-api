import os

from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        if settings.SENSOR_DATA_MODE not in {"mock", "factory_api"}:
            return
        if os.environ.get("RUN_MAIN") != "true":
            return
        from apps.core.services.sensor_simulator import SensorSimulator

        simulator = SensorSimulator()
        simulator.start()
