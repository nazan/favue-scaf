"""
WebSocket channel names: `public` (broadcast) and `user-<id>` (per user).

Must stay in sync with `web/src/utils/infraTopic.js`.
"""

from __future__ import annotations

import re

RE_USER_CHANNEL = re.compile(r"^user-(\d+)$")


def is_public_channel(name: str) -> bool:
    return name == "public"


def parse_user_channel_id(name: str) -> int | None:
    m = RE_USER_CHANNEL.match((name or "").strip())
    return int(m.group(1)) if m else None


def can_subscribe_to_topic(*, token_sub: int, topic: str) -> bool:
    if is_public_channel(topic):
        return True
    uid = parse_user_channel_id(topic)
    if uid is None:
        return False
    return uid == token_sub
