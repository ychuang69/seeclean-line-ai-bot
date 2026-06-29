from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@lru_cache
def load_faq() -> str:
    return (DATA_DIR / "faq.md").read_text(encoding="utf-8")


@lru_cache
def load_system_prompt() -> str:
    return (DATA_DIR / "system_prompt.md").read_text(encoding="utf-8")
