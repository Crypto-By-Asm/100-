from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config.database import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)  # free, pro, elite
    price_monthly: Mapped[float] = mapped_column(Float, default=0.0)
    signals_per_day: Mapped[int] = mapped_column(Integer, default=5)
    demo_balance: Mapped[float] = mapped_column(Float, default=10000.0)
    has_ai_explanations: Mapped[bool] = mapped_column(Boolean, default=False)
    has_blog_access: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str] = mapped_column(Text, default="")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(150), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("subscription_plans.id"), default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("SubscriptionPlan", lazy="joined")
    demo_account = relationship("DemoAccount", back_populates="user", uselist=False)
    trades = relationship("DemoTrade", back_populates="user")
