from fastapi import APIRouter, Query, HTTPException
from data.market_data import get_klines

router = APIRouter()

@router.get("/klines")
async def klines(
    symbol: str = Query("BTCUSDT"),
    interval: str = Query("15m"),
    limit: int = Query(300, ge=50, le=1000),
):
    try:
        df = await get_klines(symbol, interval, limit)
        records = df.to_dict(orient="records")
        # Convert timestamps for frontend
        for r in records:
            r["time"] = int(r["open_time"]) // 1000  # seconds for lightweight charts
        return records
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Market data unavailable: {type(e).__name__}")
