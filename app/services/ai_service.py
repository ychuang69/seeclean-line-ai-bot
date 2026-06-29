import requests

from app.config import settings
from app.services.faq_service import load_faq, load_system_prompt


FAQ_FALLBACK_REPLY = "這題我先幫您轉由專人確認，避免提供不精確的資訊。"


def answer_faq(question: str) -> str:
    if not settings.ai_enabled or not settings.ai_api_key:
        return FAQ_FALLBACK_REPLY

    prompt = (
        f"{load_system_prompt()}\n\n"
        "以下是唯一可使用的 FAQ 知識內容：\n"
        f"{load_faq()}\n\n"
        f"使用者問題：{question}"
    )
    headers = {
        "Authorization": f"Bearer {settings.ai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.ai_model,
        "messages": [
            {"role": "system", "content": "你是洗可淨 LINE AI 小編，只能根據提供內容回答。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    try:
        response = requests.post(settings.ai_api_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return FAQ_FALLBACK_REPLY
