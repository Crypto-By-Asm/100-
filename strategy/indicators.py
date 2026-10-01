import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.volatility import AverageTrueRange

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()

    x["ema20"] = EMAIndicator(x["close"], window=20).ema_indicator()
    x["ema50"] = EMAIndicator(x["close"], window=50).ema_indicator()
    x["ema200"] = EMAIndicator(x["close"], window=200).ema_indicator()

    x["rsi"] = RSIIndicator(x["close"], window=14).rsi()

    macd = MACD(x["close"], window_slow=26, window_fast=12, window_sign=9)
    x["macd"] = macd.macd()
    x["macd_signal"] = macd.macd_signal()
    x["macd_hist"] = macd.macd_diff()

    x["adx"] = ADXIndicator(x["high"], x["low"], x["close"], window=14).adx()
    x["atr"] = AverageTrueRange(x["high"], x["low"], x["close"], window=14).average_true_range()

    x["volume_ma20"] = x["volume"].rolling(20).mean()
    return x.dropna().reset_index(drop=True)
