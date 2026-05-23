import random
import threading
import time
from datetime import datetime

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
            sensors = Sensor.objects.filter(is_active=True, machine__is_active=True)
            for sensor in sensors:
                baseline, amplitude = SIMULATION_RANGES.get(
                    sensor.sensor_type, (50, 10)
                )
                value = baseline + random.uniform(-amplitude, amplitude)
                self.storage.add_measurement(sensor.id, value, datetime.utcnow())
            time.sleep(1)
