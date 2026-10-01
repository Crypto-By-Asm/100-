def build_trade_plan(side: str, price: float, atr: float) -> dict:
    """
    Conservative starter distances.
    These should be tuned via backtesting before any production claims.
    """
    sl_distance = max(atr * 1.5, price * 0.003)
    tp1_distance = sl_distance * 1.0
    tp2_distance = sl_distance * 1.8
    tp3_distance = sl_distance * 2.6

    if side == "LONG":
        sl = price - sl_distance
        tp1 = price + tp1_distance
        tp2 = price + tp2_distance
        tp3 = price + tp3_distance
    else:
        sl = price + sl_distance
        tp1 = price - tp1_distance
        tp2 = price - tp2_distance
        tp3 = price - tp3_distance

    return {
        "entry": round(price, 8),
        "stop_loss": round(sl, 8),
        "tp1": round(tp1, 8),
        "tp2": round(tp2, 8),
        "tp3": round(tp3, 8),
        "risk_reward_tp1": round(tp1_distance / sl_distance, 2),
        "risk_reward_tp2": round(tp2_distance / sl_distance, 2),
        "risk_reward_tp3": round(tp3_distance / sl_distance, 2),
        "sl_distance_pct": round((sl_distance / price) * 100, 3),
    }
