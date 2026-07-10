import re
from urllib.parse import parse_qs

from sqlalchemy.orm import Session

from app.config import settings
from app.services.handoff_session_service import resolve_handoff


USER_ID_PATTERN = re.compile(r"^U[0-9a-f]{32}$", re.IGNORECASE)
RESUME_COMMAND_PATTERN = re.compile(r"^恢復\s+(U[0-9a-f]{32})\s*$", re.IGNORECASE)


def build_resolve_postback_data(user_id: str) -> str | None:
    if not USER_ID_PATTERN.fullmatch(user_id):
        return None
    return f"action=resolve_handoff&user_id={user_id}"


def parse_target_user_id(value: str) -> str | None:
    command = RESUME_COMMAND_PATTERN.fullmatch(value.strip())
    if command:
        return command.group(1)

    params = parse_qs(value, keep_blank_values=True)
    if params.get("action") != ["resolve_handoff"]:
        return None
    user_id = params.get("user_id", [""])[0]
    return user_id if USER_ID_PATTERN.fullmatch(user_id) else None


def handle_admin_action(db: Session, actor_user_id: str | None, value: str) -> dict | None:
    target_user_id = parse_target_user_id(value)
    if not target_user_id:
        return None

    if not settings.line_admin_user_id or actor_user_id != settings.line_admin_user_id:
        return {"handled": True, "resolved": False, "reply": "此操作僅限管理員使用。"}

    resolved = resolve_handoff(db, target_user_id)
    if resolved:
        reply = f"已結束人工接手，客戶 Bot 自動回覆已恢復。\nUser ID：{target_user_id}"
    else:
        reply = f"此客戶目前沒有進行中的人工接手。\nUser ID：{target_user_id}"
    return {"handled": True, "resolved": resolved, "reply": reply, "target_user_id": target_user_id}
