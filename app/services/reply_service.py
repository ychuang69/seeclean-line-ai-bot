from app.services.ai_service import answer_faq
from app.services.booking_service import get_booking_reply
from app.services.handoff_service import handoff_reply
from app.services.intent_service import Intent
from app.services.price_service import get_price_reply


UNKNOWN_REPLY = "我先幫您轉由專人確認，稍後會由洗可淨人員回覆您。"


def build_reply(intent: Intent, text: str) -> str:
    if intent == Intent.HANDOFF:
        return handoff_reply()
    if intent == Intent.PRICE:
        return get_price_reply(text)
    if intent == Intent.BOOKING:
        return get_booking_reply()
    if intent == Intent.FAQ:
        return answer_faq(text)
    return UNKNOWN_REPLY
