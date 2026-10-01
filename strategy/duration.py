def estimate_duration(adx: float, atr_pct: float, signal_strength: float) -> int:
    """
    Dynamic validity window in minutes based on trend strength and volatility.
    """
    if adx >= 30 and signal_strength >= 0.75:
        return 20
    if adx >= 25 and signal_strength >= 0.65:
        return 15
    if atr_pct >= 0.01:
        return 12
    if signal_strength >= 0.60:
        return 10
    return 6
