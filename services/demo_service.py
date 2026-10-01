from datetime import datetime
from sqlalchemy.orm import Session
from models.demo import DemoAccount, DemoTrade
from models.user import User

def ensure_demo_account(db: Session, user: User) -> DemoAccount:
    account = db.query(DemoAccount).filter(DemoAccount.user_id == user.id).first()
    if account:
        return account
    starting_balance = 10000.0
    if user.plan and user.plan.demo_balance:
        starting_balance = user.plan.demo_balance
    account = DemoAccount(
        user_id=user.id,
        balance=starting_balance,
        equity=starting_balance,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

def open_demo_trade(
    db: Session,
    user: User,
    symbol: str,
    side: str,
    entry_price: float,
    stop_loss: float,
    tp1: float | None,
    tp2: float | None,
    tp3: float | None,
    quantity: float,
    signal_score: float | None = None,
) -> DemoTrade:
    account = ensure_demo_account(db, user)
    cost = quantity * entry_price
    if cost > account.balance:
        raise ValueError("Insufficient demo balance")

    trade = DemoTrade(
        user_id=user.id,
        symbol=symbol.upper(),
        side=side.upper(),
        entry_price=entry_price,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        tp3=tp3,
        quantity=quantity,
        status="OPEN",
        signal_score=signal_score,
        is_open=True,
    )
    account.balance -= cost
    account.updated_at = datetime.utcnow()
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade

def close_demo_trade(
    db: Session,
    user: User,
    trade_id: int,
    exit_price: float,
    status: str = "CLOSED",
) -> DemoTrade:
    trade = (
        db.query(DemoTrade)
        .filter(DemoTrade.id == trade_id, DemoTrade.user_id == user.id, DemoTrade.is_open == True)
        .first()
    )
    if not trade:
        raise ValueError("Open trade not found")

    account = ensure_demo_account(db, user)

    if trade.side == "LONG":
        pnl = (exit_price - trade.entry_price) * trade.quantity
    else:
        pnl = (trade.entry_price - exit_price) * trade.quantity

    pnl_pct = (pnl / (trade.entry_price * trade.quantity)) * 100 if trade.entry_price else 0

    trade.exit_price = exit_price
    trade.pnl = round(pnl, 4)
    trade.pnl_percent = round(pnl_pct, 3)
    trade.status = status
    trade.is_open = False
    trade.closed_at = datetime.utcnow()

    # Return capital + pnl
    account.balance += (trade.quantity * trade.entry_price) + pnl
    account.total_pnl += pnl
    account.equity = account.balance
    if pnl >= 0:
        account.win_count += 1
    else:
        account.loss_count += 1
    account.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(trade)
    return trade
