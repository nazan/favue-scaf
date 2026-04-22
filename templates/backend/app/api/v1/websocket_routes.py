"""
WebSocket: subscribe with JWT query param. Topics: `public`, `user-<your user id>`.
"""

import json
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.auth.jwt_utils import decode_access_token
from app.log_setup import get_app_logger
from app.services.websocket_manager import get_websocket_manager
from app.topic_utils import can_subscribe_to_topic, is_public_channel, parse_user_channel_id

router = APIRouter(prefix="/api/v1", tags=["WebSocket"])
logger = get_app_logger()


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    if not token:
        await websocket.close(code=1008)
        return
    try:
        payload = decode_access_token(token)
        sub = int(payload.get("sub"))
    except Exception:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    manager = get_websocket_manager()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            op = msg.get("op")
            topic = msg.get("topic")
            if op not in ("subscribe", "unsubscribe") or not isinstance(topic, str):
                continue
            t = topic.strip()
            if not is_public_channel(t) and parse_user_channel_id(t) is None:
                await websocket.send_text(json.dumps({"error": "invalid topic"}))
                continue
            if not can_subscribe_to_topic(token_sub=sub, topic=t):
                await websocket.send_text(json.dumps({"error": "forbidden topic"}))
                continue
            if op == "subscribe":
                await manager.add_subscription(websocket, t)
            else:
                await manager.remove_subscription(websocket, t)
    except WebSocketDisconnect:
        logger.info("WebSocket notifications disconnected (user id=%s)", sub)
    finally:
        await manager.remove_all_subscriptions(websocket)
