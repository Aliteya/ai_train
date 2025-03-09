from .base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP, func, UniqueConstraint
from datetime import datetime

class Treasure(Base):
    __tablename__ = "treasures"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    user_id: Mapped[str] = mapped_column(nullable=False)
    treasure_value: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'treasure_value', name='uix_user_treasure'),
    )