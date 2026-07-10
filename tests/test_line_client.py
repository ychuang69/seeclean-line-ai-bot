import unittest
from unittest.mock import Mock, patch

from app.config import settings
from app.line_client import push_flex_message


class LineClientTests(unittest.TestCase):
    @patch("app.line_client.requests.post")
    def test_push_flex_message_includes_persistent_button(self, post):
        response = Mock(status_code=200)
        response.raise_for_status.return_value = None
        post.return_value = response

        with (
            patch.object(settings, "line_channel_access_token", "test-token"),
            patch.object(settings, "line_push_api_url", "https://example.test/push"),
        ):
            result = push_flex_message(
                "UADMIN",
                "通知內容",
                {
                    "type": "bubble",
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "恢復 Bot",
                                    "text": "恢復 U123",
                                },
                            }
                        ],
                    },
                },
            )

        self.assertTrue(result["ok"])
        message = post.call_args.kwargs["json"]["messages"][0]
        self.assertEqual(message["type"], "flex")
        action = message["contents"]["footer"]["contents"][0]["action"]
        self.assertEqual(action["type"], "message")
        self.assertEqual(action["label"], "恢復 Bot")
        self.assertEqual(action["text"], "恢復 U123")


if __name__ == "__main__":
    unittest.main()
