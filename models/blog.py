from datetime import datetime
from sqlalchemy import String, Text, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from config.database import Base

class BlogPost(Base):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(280), unique=True, index=True)
    meta_description: Mapped[str] = mapped_column(String(320), default="")
    content: Mapped[str] = mapped_column(Text)
    excerpt: Mapped[str] = mapped_column(Text, default="")
    keywords: Mapped[str] = mapped_column(String(500), default="")
    category: Mapped[str] = mapped_column(String(100), default="Education")
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    reading_time_minutes: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
