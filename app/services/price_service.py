import json
from functools import lru_cache
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "price_rules.json"


@lru_cache
def load_price_rules() -> dict:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_price_reply(text: str) -> str:
    rules = load_price_rules()
    lower_text = text.lower()

    if "洗衣機" in text:
        service = rules["services"]["washing_machine"]
    elif "冷氣" in text or "空調" in text:
        service = rules["services"]["air_conditioner"]
    else:
        return rules["general_reply"]

    lines = [service["title"]]
    lines.extend(service["prices"])
    lines.append(rules["notes"])
    return "\n".join(lines)
