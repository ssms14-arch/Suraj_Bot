import MetaTrader5 as mt5
import pandas as pd

from config import MT5_LOGIN, MT5_PASSWORD, MT5_PATH, MT5_SERVER


def initialize_mt5():
    initialized = mt5.initialize(
        path=MT5_PATH,
        login=int(MT5_LOGIN),
        password=MT5_PASSWORD,
        server=MT5_SERVER,
    )
    if not initialized:
        raise RuntimeError(f"MetaTrader 5 initialization failed: {mt5.last_error()}")
    return True


def get_available_symbols():
    symbols = mt5.symbols_get()
    if symbols is None:
        raise RuntimeError(f"Could not retrieve MT5 instruments: {mt5.last_error()}")

    available_symbols = sorted(symbol.name for symbol in symbols)
    if not available_symbols:
        raise RuntimeError("MetaTrader 5 returned an empty instrument list")
    return available_symbols


def get_current_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None

    price = tick.bid or tick.last or tick.ask
    return float(price) if price else None


def get_market_frames(symbol, count=100):
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"Could not enable {symbol} in Market Watch: {mt5.last_error()}")

    timeframes = (
        ("4-Hour", mt5.TIMEFRAME_H4),
        ("15-Minute", mt5.TIMEFRAME_M15),
    )
    market_frames = {}

    for label, timeframe in timeframes:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None:
            raise RuntimeError(
                f"Could not retrieve {label} data for {symbol}: {mt5.last_error()}"
            )

        candles = pd.DataFrame(rates)
        if candles.empty:
            raise RuntimeError(f"No {label} market data available for {symbol}")

        candles["time"] = pd.to_datetime(candles["time"], unit="s")
        market_frames[label] = candles

    return market_frames


def get_market_data(symbol):
    sections = []

    for label, candles in get_market_frames(symbol, count=10).items():
        candles = candles[["time", "open", "high", "low", "close"]]
        sections.append(
            f"{label} candles for {symbol}:\n"
            + candles.to_string(
                index=False,
                formatters={
                    "open": "{:.5f}".format,
                    "high": "{:.5f}".format,
                    "low": "{:.5f}".format,
                    "close": "{:.5f}".format,
                },
            )
        )

    return "\n\n".join(sections)
