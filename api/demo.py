from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from config.database import get_db
from auth.deps import get_current_user
from models.user import User
from models.demo import DemoTrade
from services.demo_service import ensure_demo_account, open_demo_trade, close_demo_trade

router = APIRouter()

class OpenTradeRequest(BaseModel):
    symbol: str = "BTCUSDT"
    side: str = Field(..., pattern="^(LONG|SHORT)$")
    entry_price: float
    stop_loss: float
    tp1: float | None = None
    tp2: float | None = None
    tp3: float | None = None
    quantity: float = Field(gt=0)
    signal_score: float | None = None

class CloseTradeRequest(BaseModel):
    exit_price: float
    status: str = "CLOSED"

@router.get("/account")
def get_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = ensure_demo_account(db, current_user)
    open_trades = (
        db.query(DemoTrade)
        .filter(DemoTrade.user_id == current_user.id, DemoTrade.is_open == True)
        .all()
    )
    return {
        "balance": round(account.balance, 2),
        "equity": round(account.equity, 2),
        "total_pnl": round(account.total_pnl, 2),
        "win_count": account.win_count,
        "loss_count": account.loss_count,
        "open_trades_count": len(open_trades),
        "win_rate": round(
            (account.win_count / (account.win_count + account.loss_count) * 100)
            if (account.win_count + account.loss_count) > 0
            else 0,
            1,
        ),
    }

@router.get("/trades")
def list_trades(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    trades = (
        db.query(DemoTrade)
        .filter(DemoTrade.user_id == current_user.id)
        .order_by(DemoTrade.opened_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": t.id,
            "symbol": t.symbol,
            "side": t.side,
            "entry_price": t.entry_price,
            "stop_loss": t.stop_loss,
            "tp1": t.tp1,
            "tp2": t.tp2,
            "tp3": t.tp3,
            "quantity": t.quantity,
            "status": t.status,
            "exit_price": t.exit_price,
            "pnl": t.pnl,
            "pnl_percent": t.pnl_percent,
            "signal_score": t.signal_score,
            "is_open": t.is_open,
            "opened_at": t.opened_at.isoformat() if t.opened_at else None,
            "closed_at": t.closed_at.isoformat() if t.closed_at else None,
        }
        for t in trades
    ]

@router.post("/trades")
def open_trade(
    payload: OpenTradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        trade = open_demo_trade(
            db=db,
            user=current_user,
            symbol=payload.symbol,
            side=payload.side,
            entry_price=payload.entry_price,
            stop_loss=payload.stop_loss,
            tp1=payload.tp1,
            tp2=payload.tp2,
            tp3=payload.tp3,
            quantity=payload.quantity,
            signal_score=payload.signal_score,
        )
        return {
            "id": trade.id,
            "symbol": trade.symbol,
            "side": trade.side,
            "entry_price": trade.entry_price,
            "status": trade.status,
            "message": "Demo trade opened successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trades/{trade_id}/close")
def close_trade(
    trade_id: int,
    payload: CloseTradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        trade = close_demo_trade(
            db=db,
            user=current_user,
            trade_id=trade_id,
            exit_price=payload.exit_price,
            status=payload.status,
        )
        return {
            "id": trade.id,
            "status": trade.status,
            "pnl": trade.pnl,
            "pnl_percent": trade.pnl_percent,
            "message": "Trade closed",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
