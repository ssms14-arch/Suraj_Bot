import pandas as pd
from smartmoneyconcepts import smc


def analyze_smc(candles, swing_length=8):
    chart_candles = candles.reset_index(drop=True).copy()
    ohlc = chart_candles[["open", "high", "low", "close"]].copy()
    if "tick_volume" in chart_candles:
        ohlc["volume"] = chart_candles["tick_volume"].to_numpy()
    elif "volume" in chart_candles:
        ohlc["volume"] = chart_candles["volume"].to_numpy()
    else:
        ohlc["volume"] = 0

    swings = smc.swing_highs_lows(ohlc, swing_length=swing_length)
    structure = smc.bos_choch(ohlc, swings)
    fair_value_gaps = smc.fvg(ohlc, join_consecutive=True)
    order_blocks = smc.ob(ohlc, swings)
    liquidity = smc.liquidity(ohlc, swings)

    events = []
    for index, row in structure.iterrows():
        for event_name in ("BOS", "CHOCH"):
            value = row[event_name]
            if pd.isna(value) or value == 0:
                continue
            events.append(
                {
                    "index": int(index),
                    "broken_index": int(row["BrokenIndex"])
                    if pd.notna(row["BrokenIndex"])
                    else int(index),
                    "event": event_name,
                    "side": "BULLISH" if value > 0 else "BEARISH",
                    "level": float(row["Level"]),
                }
            )

    latest_event = events[-1] if events else None
    if latest_event:
        bias = latest_event["side"]
    else:
        ema = ohlc["close"].ewm(span=20, adjust=False).mean().iloc[-1]
        bias = "BULLISH" if ohlc["close"].iloc[-1] >= ema else "BEARISH"

    active_fvgs = int(
        (fair_value_gaps["FVG"].notna() & fair_value_gaps["MitigatedIndex"].isna()).sum()
    )

    return {
        "candles": chart_candles,
        "ohlc": ohlc,
        "swings": swings,
        "structure": structure,
        "events": events,
        "latest_event": latest_event,
        "bias": bias,
        "fvg": fair_value_gaps,
        "active_fvg_count": active_fvgs,
        "order_blocks": order_blocks,
        "liquidity": liquidity,
    }