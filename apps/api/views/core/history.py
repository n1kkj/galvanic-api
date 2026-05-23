from statistics import mean

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.models import Machine, Sensor
from apps.core.services.redis_storage import SensorHistoryStorage


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = [
            "id",
            "name",
            "sensor_type",
            "unit",
            "min_threshold",
            "max_threshold",
            "is_active",
            "machine",
        ]


class MachineSerializer(serializers.ModelSerializer):
    sensors = SensorSerializer(many=True, read_only=True)

    class Meta:
        model = Machine
        fields = ["id", "name", "description", "is_active", "sensors"]


class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.prefetch_related("sensors").all()
    serializer_class = MachineSerializer


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.select_related("machine").all()
    serializer_class = SensorSerializer

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        window = request.query_params.get("seconds", "300")
        storage = SensorHistoryStorage()
        if window == "all":
            return Response(storage.get_all(sensor_id=int(pk)))
        return Response(storage.get_recent(sensor_id=int(pk), seconds=int(window)))

    @action(detail=True, methods=["get"], url_path="latest")
    def latest(self, request, pk=None):
        storage = SensorHistoryStorage()
        points = storage.get_recent(sensor_id=int(pk), seconds=5)
        if not points:
            return Response(None)
        return Response(points[-1])

    @action(detail=True, methods=["get"], url_path="stats")
    def stats(self, request, pk=None):
        window = request.query_params.get("seconds", "300")
        storage = SensorHistoryStorage()
        if window == "all":
            points = storage.get_all(sensor_id=int(pk))
        else:
            points = storage.get_recent(sensor_id=int(pk), seconds=int(window))
        sensor = self.get_object()
        if not points:
            return Response({"samples": 0})

        values = [float(p["value"]) for p in points]
        out_of_range = [
            v for v in values if v < sensor.min_threshold or v > sensor.max_threshold
        ]
        return Response(
            {
                "samples": len(values),
                "min": min(values),
                "max": max(values),
                "avg": round(mean(values), 2),
                "last": values[-1],
                "out_of_range_count": len(out_of_range),
                "out_of_range_percent": round(
                    (len(out_of_range) / len(values)) * 100, 2
                ),
            }
        )
