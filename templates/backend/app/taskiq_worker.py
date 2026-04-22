"""
Taskiq worker: Redis queue + result backend. Example task used by the infra demo.
"""

from __future__ import annotations

from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from app.config import settings
from app.log_setup import get_app_logger
from app.services.websocket_manager import get_websocket_manager

logger = get_app_logger("taskiq-worker")

redis_async_result = RedisAsyncResultBackend(redis_url=settings.redis_url)
broker = ListQueueBroker(url=settings.redis_url)
broker.with_result_backend(redis_async_result)


@broker.task
async def demo_background_task(message: str) -> str:
    """Placeholder task (kept for extension)."""
    logger.info("demo_background_task: %s", message)
    return f"echo:{message}"


@broker.task
async def infra_user_hello_task(user_id: int, username: str) -> str:
    """Pushes `{"message": "Hello, <username>"}` to channel `user-<user_id>`."""
    mgr = get_websocket_manager()
    ch = f"user-{user_id}"
    await mgr.publish_json(
        ch,
        {"message": f"Hello, {username}"},
    )
    logger.info("infra_user_hello_task published to %s", ch)
    return "ok"
