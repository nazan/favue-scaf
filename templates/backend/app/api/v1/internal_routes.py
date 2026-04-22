"""
Internal routes: scheduler (cron) and other protected-by-secret hooks.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, status

from app.config import settings
from app.services.websocket_manager import get_websocket_manager

router = APIRouter(prefix="/api/internal", tags=["internal"])


def _require_cron_secret(x_cron_secret: str | None) -> None:
    secret = (settings.internal_cron_secret or "").strip()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cron secret not configured",
        )
    if not x_cron_secret or (x_cron_secret or "").strip() != secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing X-Cron-Secret",
        )


@router.post("/scheduler-beacon")
async def scheduler_beacon(
    x_cron_secret: str | None = Header(None, alias="X-Cron-Secret"),
):
    """
    Invoked by core-cron every few seconds. Publishes a JSON message on WebSocket channel `public`.
    """
    _require_cron_secret(x_cron_secret)
    mgr = get_websocket_manager()
    await mgr.publish_json(
        "public",
        {
            "message": "beacon",
            "ts": datetime.now(timezone.utc).isoformat(),
        },
    )
    return {"ok": True}
