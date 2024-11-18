import redis
import json
from datetime import timedelta
import os

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=True
        )
        self.default_expiry = timedelta(hours=24)

    def get(self, key):
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Cache retrieval error: {str(e)}")
            return None

    def set(self, key, value, expiry=None):
        try:
            expiry = expiry or self.default_expiry
            self.redis_client.setex(
                key,
                expiry,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Cache storage error: {str(e)}")
            return False

    def delete(self, key):
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache deletion error: {str(e)}")
            return False

    def flush(self):
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache flush error: {str(e)}")
            return False