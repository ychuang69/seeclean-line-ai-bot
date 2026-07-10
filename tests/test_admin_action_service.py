import unittest
from datetime import timedelta
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db import Base
from app.models import HandoffSession, utc_now
from app.services.admin_action_service import (
    build_resolve_postback_data,
    handle_admin_action,
)


ADMIN_ID = "Uaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
CUSTOMER_ID = "Ubbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


class AdminActionServiceTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        self.db = sessionmaker(bind=engine)()
        self.db.add(
            HandoffSession(
                user_id=CUSTOMER_ID,
                active=True,
                reason="漏水",
                expires_at=utc_now() + timedelta(hours=24),
            )
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def test_admin_can_resolve_with_postback(self):
        data = build_resolve_postback_data(CUSTOMER_ID)
        with patch.object(settings, "line_admin_user_id", ADMIN_ID):
            result = handle_admin_action(self.db, ADMIN_ID, data)

        self.assertTrue(result["resolved"])
        self.assertFalse(self.db.query(HandoffSession).filter_by(user_id=CUSTOMER_ID).one().active)

    def test_admin_can_resolve_with_text_command(self):
        with patch.object(settings, "line_admin_user_id", ADMIN_ID):
            result = handle_admin_action(self.db, ADMIN_ID, f"恢復 {CUSTOMER_ID}")

        self.assertTrue(result["resolved"])

    def test_non_admin_cannot_resolve(self):
        with patch.object(settings, "line_admin_user_id", ADMIN_ID):
            result = handle_admin_action(self.db, CUSTOMER_ID, f"恢復 {CUSTOMER_ID}")

        self.assertFalse(result["resolved"])
        self.assertTrue(self.db.query(HandoffSession).filter_by(user_id=CUSTOMER_ID).one().active)


if __name__ == "__main__":
    unittest.main()
