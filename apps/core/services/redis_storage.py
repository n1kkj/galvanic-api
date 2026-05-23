import json
from datetime import datetime

import redis
from django.conf import settings


class SensorHistoryStorage:
    def __init__(self) -> None:
        self.client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    @staticmethod
    def history_key(sensor_id: int) -> str:
        return f"sensor:{sensor_id}:history"

    def add_measurement(self, sensor_id: int, value: float, ts: datetime) -> dict:
        payload = {
            "sensor_id": sensor_id,
            "value": round(value, 2),
            "timestamp": ts.isoformat(),
        }
        score = ts.timestamp()
        self.client.zadd(self.history_key(sensor_id), {json.dumps(payload): score})
        return payload

    def get_recent(self, sensor_id: int, seconds: int = 300) -> list[dict]:
        now = datetime.now().timestamp()
        raw = self.client.zrangebyscore(
            self.history_key(sensor_id), min=now - seconds, max=now
        )
        return [json.loads(item) for item in raw]

    def get_all(self, sensor_id: int) -> list[dict]:
        raw = self.client.zrange(self.history_key(sensor_id), 0, -1)
        return [json.loads(item) for item in raw]
