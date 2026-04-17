import time
import logging
from collections import defaultdict, deque
from fastapi import HTTPException
import redis
from app.config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60, redis_url: str = ""):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis_url = redis_url
        self._redis = None
        self._memory_store: dict[str, deque] = defaultdict(deque)

        if self.redis_url:
            try:
                self._redis = redis.from_url(self.redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("RateLimiter: Redis connected ✅")
            except Exception as e:
                logger.warning(f"RateLimiter: Redis connection failed, falling back to in-memory ⚠️: {e}")
                self._redis = None

    def check(self, user_id: str) -> dict:
        now = time.time()
        key = f"rate_limit:{user_id}"

        if self._redis:
            return self._check_redis(key, now)
        return self._check_memory(user_id, now)

    def _check_redis(self, key: str, now: float) -> dict:
        pipe = self._redis.pipeline()
        # Remove timestamps older than the window
        pipe.zremrangebyscore(key, 0, now - self.window_seconds)
        # Count remaining slots
        pipe.zcard(key)
        # Add current timestamp
        pipe.zadd(key, {str(now): now})
        # Set expiry for the key
        pipe.expire(key, self.window_seconds)
        results = pipe.execute()

        count = results[1]
        remaining = self.max_requests - count

        if count >= self.max_requests:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds}s.",
                headers={"Retry-After": str(self.window_seconds)}
            )

        return {
            "limit": self.max_requests,
            "remaining": max(0, remaining - 1),
            "reset_at": int(now + self.window_seconds)
        }

    def _check_memory(self, user_id: str, now: float) -> dict:
        window = self._memory_store[user_id]
        while window and window[0] < now - self.window_seconds:
            window.popleft()

        count = len(window)
        remaining = self.max_requests - count

        if count >= self.max_requests:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded (In-memory). Max {self.max_requests} per {self.window_seconds}s.",
                headers={"Retry-After": str(self.window_seconds)}
            )

        window.append(now)
        return {
            "limit": self.max_requests,
            "remaining": max(0, remaining - 1),
            "reset_at": int(now + self.window_seconds)
        }

# Singleton instances based on config
rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_per_minute,
    window_seconds=60,
    redis_url=settings.redis_url
)
