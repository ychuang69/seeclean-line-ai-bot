from enum import StrEnum


class Intent(StrEnum):
    PRICE = "詢價"
    BOOKING = "預約"
    FAQ = "FAQ"
    HANDOFF = "人工接手"
    UNKNOWN = "未知"


PRICE_KEYWORDS = ["多少錢", "價格", "價錢", "報價", "收費", "費用", "怎麼算", "清洗多少"]
BOOKING_KEYWORDS = ["預約", "安排", "有空", "時間", "日期", "幾號", "可以洗", "我要洗", "想洗"]
FAQ_KEYWORDS = ["冷氣", "洗衣機", "拆洗", "清洗", "多久", "流程", "保養", "服務", "水盤", "風扇", "馬達"]


def detect_intent(text: str, is_handoff: bool = False) -> Intent:
    normalized = text.strip()
    if is_handoff:
        return Intent.HANDOFF
    if any(keyword in normalized for keyword in PRICE_KEYWORDS):
        return Intent.PRICE
    if any(keyword in normalized for keyword in BOOKING_KEYWORDS):
        return Intent.BOOKING
    if any(keyword in normalized for keyword in FAQ_KEYWORDS):
        return Intent.FAQ
    return Intent.UNKNOWN
