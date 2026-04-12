from datetime import datetime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy import DateTime

class Base(DeclarativeBase):
     pass

class Article(Base):
    __tablename__ = 'articles'

    uuid: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    url: Mapped[str] = mapped_column(String(30))
    article: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(String(30))
    author: Mapped[str] = mapped_column(String(30))
    source: Mapped[str] = mapped_column(String(30))
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return (
            f"Article(uuid={self.uuid!r}, title={self.title!r}, "
            f"source={self.source!r}, author={self.author!r}, "
            f"scraped_at={self.scraped_at!r})"
        )