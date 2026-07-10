import requests

from app.config import settings


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.line_channel_access_token}",
        "Content-Type": "application/json",
    }


def reply_message(reply_token: str, text: str) -> dict:
    if not settings.line_channel_access_token:
        return {"ok": False, "skipped": True, "reason": "LINE_CHANNEL_ACCESS_TOKEN not set"}

    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}],
    }
    response = requests.post(
        settings.line_reply_api_url,
        headers=_headers(),
        json=payload,
        timeout=10,
    )
    response.raise_for_status()
    return {"ok": True, "status_code": response.status_code}


def push_message(user_id: str, text: str, postback_data: str | None = None) -> dict:
    if not settings.line_channel_access_token:
        return {"ok": False, "skipped": True, "reason": "LINE_CHANNEL_ACCESS_TOKEN not set"}

    message = {"type": "text", "text": text}
    if postback_data:
        message["quickReply"] = {
            "items": [
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "恢復 Bot",
                        "data": postback_data,
                        "displayText": "已選擇恢復 Bot",
                    },
                }
            ]
        }

    response = requests.post(
        settings.line_push_api_url,
        headers=_headers(),
        json={"to": user_id, "messages": [message]},
        timeout=10,
    )
    response.raise_for_status()
    return {"ok": True, "status_code": response.status_code}


def get_profile(user_id: str) -> dict:
    if not settings.line_channel_access_token:
        return {}

    response = requests.get(
        f"{settings.line_profile_api_url}/{user_id}",
        headers=_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
