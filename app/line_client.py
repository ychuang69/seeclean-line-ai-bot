import requests

from app.config import settings


def reply_message(reply_token: str, text: str) -> dict:
    if not settings.line_channel_access_token:
        return {"ok": False, "skipped": True, "reason": "LINE_CHANNEL_ACCESS_TOKEN not set"}

    headers = {
        "Authorization": f"Bearer {settings.line_channel_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}],
    }
    response = requests.post(
        settings.line_reply_api_url,
        headers=headers,
        json=payload,
        timeout=10,
    )
    response.raise_for_status()
    return {"ok": True, "status_code": response.status_code}
