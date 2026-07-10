import logging

import requests

from app.config import settings
from app.line_client import get_profile, push_message


logger = logging.getLogger(__name__)


def build_handoff_notification(user_id: str | None, text: str, display_name: str | None = None) -> str:
    customer = display_name or "LINE 客戶"
    customer_id = user_id or "unknown"
    safe_text = text.strip()[:1000]
    return (
        "【洗可淨｜需要人工接手】\n"
        f"客戶：{customer}\n"
        f"User ID：{customer_id}\n"
        f"訊息：{safe_text}\n\n"
        "請至 LINE Official Account Manager 查看並回覆。"
    )


def notify_handoff(user_id: str | None, text: str) -> dict:
    if not settings.line_admin_user_id:
        return {"ok": False, "skipped": True, "reason": "LINE_ADMIN_USER_ID not set"}

    display_name = None
    if user_id:
        try:
            display_name = get_profile(user_id).get("displayName")
        except (requests.RequestException, ValueError):
            logger.warning("Unable to load LINE profile for handoff notification", exc_info=True)

    try:
        notification = build_handoff_notification(user_id, text, display_name)
        return push_message(settings.line_admin_user_id, notification)
    except requests.RequestException as exc:
        logger.error("Unable to send LINE handoff notification", exc_info=True)
        return {"ok": False, "error": type(exc).__name__}
