import httpx
import pandas as pd
from config.settings import settings

async def get_klines(symbol: str = "BTCUSDT", interval: str = "15m", limit: int = 300) -> pd.DataFrame:
    url = f"{settings.binance_base_url}/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": min(limit, 1000),
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        rows = response.json()

    columns = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore",
    ]
    df = pd.DataFrame(rows, columns=columns)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
