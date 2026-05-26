import json
import random
import threading
import time
from datetime import datetime
from urllib.error import URLError
from urllib.request import urlopen

from django.conf import settings

from apps.core.models import Sensor
from apps.core.services.redis_storage import SensorHistoryStorage


SIMULATION_RANGES = {
    Sensor.SensorType.TEMPERATURE: (65, 8),
    Sensor.SensorType.HUMIDITY: (55, 18),
    Sensor.SensorType.PRESSURE: (101, 12),
    Sensor.SensorType.DUSTINESS: (30, 20),
    Sensor.SensorType.PH: (7, 2),
    Sensor.SensorType.SERVO_ANGLE: (90, 70),
    Sensor.SensorType.MOTOR_SPEED: (1200, 500),
}

class SensorSimulator:
    def __init__(self) -> None:
        self._stop = threading.Event()
        self._thread = None
        self.storage = SensorHistoryStorage()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            if settings.SENSOR_DATA_MODE == "factory_api":
                self._collect_from_factory_api()
            else:
                self._collect_mock()
            time.sleep(1)

    def _collect_mock(self) -> None:
        sensors = Sensor.objects.filter(is_active=True, machine__is_active=True)
        for sensor in sensors:
            baseline, amplitude = SIMULATION_RANGES.get(sensor.sensor_type, (50, 10))
            value = baseline + random.uniform(-amplitude, amplitude)
            self.storage.add_measurement(sensor.id, value, datetime.utcnow())

    def _collect_from_factory_api(self) -> None:
        try:
            with urlopen(settings.FACTORY_STATUS_URL, timeout=3) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError, OSError):
            return

        stages = payload.get("data") or {}
        for stage_key, stage_payload in stages.items():
            if not isinstance(stage_payload, dict):
                continue
            for sensor_name, value in self._extract_numeric_items(stage_payload):
                sensor = Sensor.objects.filter(
                    machine__name=stage_key,
                    name=sensor_name,
                    is_active=True,
                    machine__is_active=True,
                ).first()
                if sensor:
                    self.storage.add_measurement(sensor.id, value, datetime.utcnow())

    @staticmethod
    def _extract_numeric_items(stage_payload: dict) -> list[tuple[str, float]]:
        values = []
        for key, value in stage_payload.items():
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                values.append((key, float(value)))
        return values
