import uuid
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy import DateTime

class Base(DeclarativeBase):
     pass

class Article(Base):
    """Article db model"""
    __tablename__ = 'articles'

    uuid: Mapped[str] = mapped_column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(30))
    url: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(String(2000))
    author: Mapped[str] = mapped_column(String(30))
    source: Mapped[str] = mapped_column(String(30))
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)