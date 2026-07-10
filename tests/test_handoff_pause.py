import unittest
from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import HandoffSession, utc_now
from app.services.message_router import process_text_message


class HandoffPauseTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        self.db = sessionmaker(bind=engine)()

    def tearDown(self):
        self.db.close()

    def test_follow_up_message_is_logged_without_bot_reply(self):
        first = process_text_message(
            self.db,
            user_id="U123",
            text="洗完漏水怎麼辦",
            source="line",
            dedupe_key="event-1",
        )
        follow_up = process_text_message(
            self.db,
            user_id="U123",
            text="可以盡快聯絡我嗎",
            source="line",
            dedupe_key="event-2",
        )

        self.assertTrue(first["should_reply"])
        self.assertTrue(first["handoff_active"])
        self.assertFalse(follow_up["should_reply"])
        self.assertTrue(follow_up["handoff_active"])
        self.assertIsNone(follow_up["reply"])

    def test_bot_resumes_after_handoff_expires(self):
        process_text_message(
            self.db,
            user_id="U123",
            text="洗完漏水怎麼辦",
            source="line",
            dedupe_key="event-1",
        )
        handoff = self.db.query(HandoffSession).filter_by(user_id="U123").one()
        handoff.expires_at = utc_now() - timedelta(minutes=1)
        self.db.commit()

        after_expiry = process_text_message(
            self.db,
            user_id="U123",
            text="請問冷氣清洗多少錢",
            source="line",
            dedupe_key="event-2",
        )

        self.assertTrue(after_expiry["should_reply"])
        self.assertFalse(after_expiry["handoff_active"])
        self.assertIsNotNone(after_expiry["reply"])


if __name__ == "__main__":
    unittest.main()
