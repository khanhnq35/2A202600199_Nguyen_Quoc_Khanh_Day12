import json
import logging
import redis
from app.config import settings

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, redis_url: str = ""):
        self.redis_url = redis_url
        self._redis = None
        self._memory_store = {} # Fallback

        if self.redis_url:
            try:
                self._redis = redis.from_url(self.redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("SessionManager: Redis connected ✅")
            except Exception as e:
                logger.warning(f"SessionManager: Redis failed, using memory ⚠️: {e}")

    def get_history(self, session_id: str) -> list:
        if self._redis:
            data = self._redis.get(f"chat_history:{session_id}")
            return json.loads(data) if data else []
        return self._memory_store.get(session_id, [])

    def save_history(self, session_id: str, history: list, ttl: int = 3600):
        if self._redis:
            self._redis.setex(f"chat_history:{session_id}", ttl, json.dumps(history))
        else:
            self._memory_store[session_id] = history

    def add_message(self, session_id: str, role: str, content: str):
        history = self.get_history(session_id)
        history.append({"role": role, "content": content})
        # Keep last 10 messages
        if len(history) > 10:
            history = history[-10:]
        self.save_history(session_id, history)
        return history

session_manager = SessionManager(redis_url=settings.redis_url)
