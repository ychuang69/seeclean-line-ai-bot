import json
from functools import lru_cache
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "handoff_keywords.json"
HANDOFF_REPLY = "我先幫您轉由專人確認，稍後會由洗可淨人員協助您處理。"


@lru_cache
def load_handoff_keywords() -> list[str]:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get("keywords", [])


def needs_handoff(text: str) -> bool:
    return any(keyword in text for keyword in load_handoff_keywords())


def handoff_reply() -> str:
    return HANDOFF_REPLY
