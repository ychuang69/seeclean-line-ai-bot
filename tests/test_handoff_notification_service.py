import unittest
from unittest.mock import patch

from app.config import settings
from app.services.handoff_notification_service import (
    build_handoff_flex_contents,
    build_handoff_notification,
    notify_handoff,
)


CUSTOMER_ID = "Ubbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


class HandoffNotificationServiceTests(unittest.TestCase):
    def test_build_notification_contains_customer_context(self):
        message = build_handoff_notification("U123", "洗完漏水怎麼辦", "王小明")

        self.assertIn("王小明", message)
        self.assertIn("U123", message)
        self.assertIn("洗完漏水怎麼辦", message)

    def test_notification_is_skipped_without_admin_user_id(self):
        with patch.object(settings, "line_admin_user_id", ""):
            result = notify_handoff("U123", "洗完漏水怎麼辦")

        self.assertTrue(result["skipped"])

    @patch("app.services.handoff_notification_service.push_flex_message")
    @patch("app.services.handoff_notification_service.get_profile")
    def test_notification_uses_profile_and_pushes_to_admin(self, get_profile, push_flex_message):
        get_profile.return_value = {"displayName": "王小明"}
        push_flex_message.return_value = {"ok": True, "status_code": 200}

        with patch.object(settings, "line_admin_user_id", "UADMIN"):
            result = notify_handoff(CUSTOMER_ID, "洗完漏水怎麼辦")

        self.assertTrue(result["ok"])
        push_flex_message.assert_called_once()
        self.assertEqual(push_flex_message.call_args.args[0], "UADMIN")
        self.assertIn("王小明", push_flex_message.call_args.args[1])
        contents = push_flex_message.call_args.args[2]
        self.assertEqual(contents["footer"]["contents"][0]["action"]["label"], "恢復 Bot")

    def test_flex_contents_include_persistent_postback_button(self):
        contents = build_handoff_flex_contents(
            CUSTOMER_ID,
            "洗完漏水怎麼辦",
            "王小明",
            f"action=resolve_handoff&user_id={CUSTOMER_ID}",
        )

        action = contents["footer"]["contents"][0]["action"]
        self.assertEqual(action["type"], "postback")
        self.assertIn(CUSTOMER_ID, action["data"])


if __name__ == "__main__":
    unittest.main()
