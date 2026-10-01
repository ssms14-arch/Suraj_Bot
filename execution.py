import MetaTrader5 as mt5


def execute_trade(symbol, decision, lot_size=0.01):
    decision = (decision or "").strip().upper()

    if decision == "HOLD":
        return f"HOLD: no order placed for {symbol}."

    if decision == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
    elif decision == "SELL":
        order_type = mt5.ORDER_TYPE_SELL
    else:
        return f"ERROR: unrecognised decision '{decision}' (expected BUY, SELL or HOLD)."

    if not mt5.symbol_select(symbol, True):
        return f"ERROR: could not enable symbol {symbol} in Market Watch."

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return f"ERROR: no price data for {symbol}: {mt5.last_error()}"

    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot_size),
        "type": order_type,
        "price": price,
        "deviation": 20,
        "magic": 20260927,
        "comment": "ai hedge fund",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result is None:
        return f"ERROR: order_send returned nothing for {symbol}: {mt5.last_error()}"

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return (
            f"ERROR: {decision} {symbol} rejected: "
            f"retcode={result.retcode} comment={result.comment}"
        )

    return (
        f"SUCCESS: {decision} {result.volume} lots of {symbol} "
        f"at {result.price} (deal {result.deal})"
    )
