import datetime
from dataclasses import dataclass
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from ..db import db


@dataclass
class Message(db.Model):
    __tablename__ = "message"
    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[str] = mapped_column(unique=True)
    sender_id: Mapped[str]
    user_message: Mapped[str]
    ai_response: Mapped[str]
    timestamp: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow)

    children = relationship("Review", backref='message')
