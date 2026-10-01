from fastapi import APIRouter, Query, Depends
from data.market_data import get_klines
from strategy.signal_engine import generate_signal
from services.gemini_service import explain_signal
from auth.deps import get_current_user_optional
from models.user import User

router = APIRouter()

@router.get("/current")
async def current_signal(
    symbol: str = Query("BTCUSDT"),
    interval: str = Query("15m"),
    explain: bool = Query(False),
    current_user: User | None = Depends(get_current_user_optional),
):
    df = await get_klines(symbol, interval, 300)
    result = generate_signal(df)
    result["symbol"] = symbol.upper()
    result["timeframe"] = interval

    if explain:
        # Only give AI explanation if user has pro/elite or for demo
        can_explain = True
        if current_user and current_user.plan:
            can_explain = current_user.plan.has_ai_explanations or current_user.plan.name == "free"
        if can_explain:
            result["ai_explanation"] = explain_signal(result)
        else:
            result["ai_explanation"] = "Upgrade to Pro for AI signal explanations."
    return result
