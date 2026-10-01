from datetime import datetime
from sqlalchemy import String, Float, DateTime, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from config.database import Base

class DemoAccount(Base):
    __tablename__ = "demo_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True)
    balance: Mapped[float] = mapped_column(Float, default=10000.0)
    equity: Mapped[float] = mapped_column(Float, default=10000.0)
    total_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    win_count: Mapped[int] = mapped_column(Integer, default=0)
    loss_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="demo_account")

class DemoTrade(Base):
    __tablename__ = "demo_trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(20))
    side: Mapped[str] = mapped_column(String(10))  # LONG / SHORT
    entry_price: Mapped[float] = mapped_column(Float)
    stop_loss: Mapped[float] = mapped_column(Float)
    tp1: Mapped[float] = mapped_column(Float, nullable=True)
    tp2: Mapped[float] = mapped_column(Float, nullable=True)
    tp3: Mapped[float] = mapped_column(Float, nullable=True)
    quantity: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")  # OPEN, CLOSED, SL_HIT, TP1_HIT, TP2_HIT, TP3_HIT
    exit_price: Mapped[float] = mapped_column(Float, nullable=True)
    pnl: Mapped[float] = mapped_column(Float, default=0.0)
    pnl_percent: Mapped[float] = mapped_column(Float, default=0.0)
    signal_score: Mapped[float] = mapped_column(Float, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("User", back_populates="trades")
