from dataclasses import dataclass
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from ..db import db
import datetime
from .message import *


@dataclass
class Review(db.Model):
    __tablename__ = "review"
    id: Mapped[int] = mapped_column(primary_key=True)
    review: Mapped[str]  # 評価のスタンプテキスト
    message_id: Mapped[str] = mapped_column(ForeignKey("message.message_id"))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow)
