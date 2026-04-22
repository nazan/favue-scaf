"""
Redis pub/sub bridge for per-topic WebSocket messages.

Topics (full_topic strings) are e.g. `public`, `user-42` — see app.topic_utils.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Set

import redis.asyncio as redis
from fastapi import WebSocket

from app.config import settings

logger = logging.getLogger(__name__)


class RedisWebSocketManager:
    def __init__(self, redis_url: Optional[str] = None, key_prefix: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url
        self.key_prefix = key_prefix or settings.redis_key_prefix
        self.redis_client: Optional[redis.Redis] = None
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis_subscriptions: Dict[str, asyncio.Task] = {}
        self._ws_topics: Dict[WebSocket, Set[str]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        await self.redis_client.ping()
        self._initialized = True
        logger.info("WebSocket manager initialized (Redis %s)", self.redis_url)

    def _redis_channel_name(self, full_topic: str) -> str:
        return f"{self.key_prefix}ws:channel:{full_topic}"

    async def add_subscription(self, websocket: WebSocket, full_topic: str) -> None:
        if not self._initialized:
            await self.initialize()
        if full_topic not in self.active_connections:
            self.active_connections[full_topic] = set()
        self.active_connections[full_topic].add(websocket)
        if websocket not in self._ws_topics:
            self._ws_topics[websocket] = set()
        self._ws_topics[websocket].add(full_topic)
        await self._ensure_redis_listener(full_topic)

    async def remove_subscription(self, websocket: WebSocket, full_topic: str) -> None:
        if full_topic in self.active_connections:
            self.active_connections[full_topic].discard(websocket)
            if not self.active_connections[full_topic]:
                del self.active_connections[full_topic]
                if full_topic in self.redis_subscriptions:
                    t = self.redis_subscriptions.pop(full_topic)
                    t.cancel()
                    try:
                        await t
                    except asyncio.CancelledError:
                        pass
        if websocket in self._ws_topics:
            self._ws_topics[websocket].discard(full_topic)
            if not self._ws_topics[websocket]:
                del self._ws_topics[websocket]

    async def remove_all_subscriptions(self, websocket: WebSocket) -> None:
        topics = list(self._ws_topics.get(websocket, set()))
        for t in topics:
            await self.remove_subscription(websocket, t)

    async def _ensure_redis_listener(self, full_topic: str) -> None:
        if full_topic in self.redis_subscriptions:
            return
        assert self.redis_client is not None
        redis_channel = self._redis_channel_name(full_topic)
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(redis_channel)
        task = asyncio.create_task(self._listen_redis(pubsub, full_topic))
        self.redis_subscriptions[full_topic] = task

    async def _listen_redis(self, pubsub: Any, full_topic: str) -> None:
        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                await self._broadcast_raw(full_topic, data)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("Redis listener error for %s: %s", full_topic, e, exc_info=True)
        finally:
            try:
                await pubsub.unsubscribe()
                await pubsub.close()
            except Exception:
                pass

    async def _broadcast_raw(self, full_topic: str, text: str) -> None:
        if full_topic not in self.active_connections:
            return
        disconnected: Set[WebSocket] = set()
        for ws in list(self.active_connections[full_topic]):
            try:
                await ws.send_text(text)
            except Exception:
                disconnected.add(ws)
        for ws in disconnected:
            await self.remove_all_subscriptions(ws)

    async def publish_json(self, full_topic: str, payload: dict) -> None:
        if not self._initialized:
            await self.initialize()
        assert self.redis_client is not None
        data = json.dumps(payload)
        await self.redis_client.publish(self._redis_channel_name(full_topic), data)


_websocket_manager: Optional[RedisWebSocketManager] = None


def get_websocket_manager() -> RedisWebSocketManager:
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = RedisWebSocketManager()
    return _websocket_manager
