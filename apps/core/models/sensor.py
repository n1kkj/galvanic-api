from django.db import models

from apps.core.models.machine import Machine


class Sensor(models.Model):
    class SensorType(models.TextChoices):
        TEMPERATURE = "temperature", "Температура"
        HUMIDITY = "humidity", "Влажность"
        PRESSURE = "pressure", "Давление"
        DUSTINESS = "dustiness", "Запыленность"
        PH = "ph", "Кислотность pH"
        SERVO_ANGLE = "servo_angle", "Угол поворота сервопривода"
        MOTOR_SPEED = "motor_speed", "Скорость моторчика"

    machine = models.ForeignKey(
        Machine, on_delete=models.CASCADE, related_name="sensors"
    )
    name = models.CharField(max_length=255)
    sensor_type = models.CharField(max_length=50, choices=SensorType.choices)
    unit = models.CharField(max_length=16, default="°C")
    min_threshold = models.FloatField(default=0)
    max_threshold = models.FloatField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        unique_together = ("machine", "name")

    def __str__(self) -> str:
        return f"{self.machine.name}: {self.name}"
