from strategy.indicators import add_indicators
from strategy.risk_manager import build_trade_plan
from strategy.duration import estimate_duration

def generate_signal(df) -> dict:
    x = add_indicators(df)
    if len(x) == 0:
        return {
            "signal": "WAIT",
            "score": 0.0,
            "score_is_not_a_guaranteed_probability": True,
            "duration_minutes": 0,
            "price": 0.0,
            "indicators": {},
            "plan": {},
            "reasons": ["Insufficient data for analysis."],
        }

    row = x.iloc[-1]

    long_score = 0.0
    short_score = 0.0
    reasons = []

    # Trend structure (EMA stack)
    if row["close"] > row["ema20"] > row["ema50"]:
        long_score += 0.22
        reasons.append("Price is above EMA20 and EMA50 (bullish structure).")
    if row["close"] < row["ema20"] < row["ema50"]:
        short_score += 0.22
        reasons.append("Price is below EMA20 and EMA50 (bearish structure).")

    # RSI momentum (avoid extremes)
    if 52 < row["rsi"] < 70:
        long_score += 0.16
        reasons.append("RSI supports bullish momentum without being deeply overbought.")
    if 30 < row["rsi"] < 48:
        short_score += 0.16
        reasons.append("RSI supports bearish momentum without being deeply oversold.")

    # MACD histogram
    if row["macd_hist"] > 0:
        long_score += 0.16
        reasons.append("MACD histogram is positive.")
    elif row["macd_hist"] < 0:
        short_score += 0.16
        reasons.append("MACD histogram is negative.")

    # ADX trend strength
    if row["adx"] >= 20:
        if long_score > short_score:
            long_score += 0.16
        elif short_score > long_score:
            short_score += 0.16
        reasons.append(f"ADX ({row['adx']:.1f}) indicates a measurable trend.")

    # Volume confirmation
    if row["volume"] > row["volume_ma20"]:
        if long_score > short_score:
            long_score += 0.10
        elif short_score > long_score:
            short_score += 0.10
        reasons.append("Current volume is above its 20-period average.")

    # Higher timeframe context via EMA200
    if row["close"] > row["ema200"]:
        long_score += 0.08
        reasons.append("Price is above EMA200 (higher-timeframe bullish bias).")
    else:
        short_score += 0.08
        reasons.append("Price is below EMA200 (higher-timeframe bearish bias).")

    long_score = min(long_score, 1.0)
    short_score = min(short_score, 1.0)

    if max(long_score, short_score) < 0.55 or abs(long_score - short_score) < 0.12:
        side = "WAIT"
        strength = max(long_score, short_score)
        plan = {}
    else:
        side = "LONG" if long_score > short_score else "SHORT"
        strength = max(long_score, short_score)
        plan = build_trade_plan(side, float(row["close"]), float(row["atr"]))

    atr_pct = float(row["atr"] / row["close"]) if row["close"] else 0
    duration = estimate_duration(float(row["adx"]), atr_pct, strength)

    return {
        "signal": side,
        "score": round(strength, 3),
        "score_is_not_a_guaranteed_probability": True,
        "duration_minutes": duration,
        "price": float(row["close"]),
        "indicators": {
            "rsi": round(float(row["rsi"]), 2),
            "adx": round(float(row["adx"]), 2),
            "ema20": round(float(row["ema20"]), 6),
            "ema50": round(float(row["ema50"]), 6),
            "ema200": round(float(row["ema200"]), 6),
            "macd": round(float(row["macd"]), 6),
            "macd_signal": round(float(row["macd_signal"]), 6),
            "macd_hist": round(float(row["macd_hist"]), 6),
            "atr": round(float(row["atr"]), 6),
            "volume": float(row["volume"]),
            "volume_ma20": round(float(row["volume_ma20"]), 2),
        },
        "plan": plan,
        "reasons": reasons[-6:],
    }
