"""
Infrastructure proof: protected route that enqueues a Taskiq job (worker → user WebSocket channel).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.auth_routes import get_current_user
from app.taskiq_worker import infra_user_hello_task

router = APIRouter(prefix="/api/v1/infra", tags=["infrastructure-demo"])


@router.post("/secure-worker-ws")
async def secure_worker_ws(
    current_user: dict = Depends(get_current_user),
):
    """
    Requires Authorization: Bearer. Enqueues a background job that publishes to
    WebSocket channel `user-<id>` with `{"message": "Hello, <username>"}`.
    """
    await infra_user_hello_task.kiq(current_user["id"], current_user["username"])
    return {
        "ok": True,
        "enqueued": True,
        "user_id": current_user["id"],
    }
