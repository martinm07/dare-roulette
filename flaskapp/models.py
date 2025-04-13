from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from .extensions import db

# class User(db.Model):
#     __tablename__ = "users"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str]


class Dare(db.Model):
    __tablename__ = "dares"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_created: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp()
    )
    content: Mapped[str]
    by: Mapped[str]
    used: Mapped[bool] = mapped_column(default=False)
    played: Mapped[bool] = mapped_column(default=False)
