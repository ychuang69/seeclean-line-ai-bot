import logging

import requests

from app.config import settings
from app.line_client import get_profile, push_flex_message, push_message
from app.services.admin_action_service import build_resolve_postback_data


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
        "請至 LINE Official Account Manager 查看並回覆。\n"
        f"完成後可輸入：恢復 {customer_id}"
    )


def build_handoff_flex_contents(
    user_id: str,
    text: str,
    display_name: str | None,
    postback_data: str,
) -> dict:
    customer = display_name or "LINE 客戶"
    safe_text = text.strip()[:1000]
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "需要人工接手",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#147D64",
                },
                {"type": "text", "text": f"客戶：{customer}", "wrap": True},
                {"type": "text", "text": f"User ID：{user_id}", "size": "xs", "wrap": True},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": safe_text, "wrap": True, "margin": "md"},
                {
                    "type": "text",
                    "text": f"備用指令：恢復 {user_id}",
                    "size": "xs",
                    "color": "#777777",
                    "wrap": True,
                    "margin": "md",
                },
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#147D64",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "恢復 Bot",
                        "data": postback_data,
                        "displayText": "已選擇恢復 Bot",
                    },
                }
            ],
        },
    }


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
        postback_data = build_resolve_postback_data(user_id) if user_id else None
        if user_id and postback_data:
            contents = build_handoff_flex_contents(user_id, text, display_name, postback_data)
            return push_flex_message(settings.line_admin_user_id, notification, contents)
        return push_message(settings.line_admin_user_id, notification)
    except requests.RequestException as exc:
        logger.error("Unable to send LINE handoff notification", exc_info=True)
        return {"ok": False, "error": type(exc).__name__}
