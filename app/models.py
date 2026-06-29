from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, UniqueConstraint

from app.db import Base


class MessageLog(Base):
    __tablename__ = "message_logs"
    __table_args__ = (
        UniqueConstraint("dedupe_key", name="uq_message_logs_dedupe_key"),
    )

    id = Column(Integer, primary_key=True, index=True)
    dedupe_key = Column(String(255), nullable=False, index=True)
    source = Column(String(50), nullable=False, default="line")
    user_id = Column(String(255), nullable=True, index=True)
    message_id = Column(String(255), nullable=True, index=True)
    event_id = Column(String(255), nullable=True, index=True)
    event_type = Column(String(50), nullable=True)
    intent = Column(String(50), nullable=True)
    user_text = Column(Text, nullable=True)
    reply_text = Column(Text, nullable=True)
    raw_event = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
