import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

import data_engine

def make_candles(start, count, frequency):
    positions = np.arange(count)
    close = 2400 + np.sin(positions / 7) * 8 + positions * 0.025
    open_price = close + np.sin(positions / 3) * 0.8
    return pd.DataFrame(
        {
            "time": pd.date_range(start, periods=count, freq=frequency),
            "open": open_price,
            "high": np.maximum(open_price, close) + 0.9,
            "low": np.minimum(open_price, close) - 0.9,
            "close": close,
            "tick_volume": 400 + positions,
        }
    )


class TradingDashboardRenderTests(unittest.TestCase):
    def test_live_order_button_is_visible_but_disabled_when_disconnected(self):
        app = AppTest.from_file("app.py").run()

        place_order = next(button for button in app.button if button.label == "Place live order")

        self.assertFalse(app.exception)
        self.assertTrue(place_order.disabled)
        self.assertIn("Choose", next(widget for widget in app.selectbox if widget.label == "Order side").options)

    def test_populated_market_data_renders_without_errors(self):
        candle_count = 240
        frames = {
            "4-Hour": make_candles("2026-01-01", candle_count, "4h"),
            "15-Minute": make_candles("2026-02-01", candle_count, "15min"),
        }
        app = AppTest.from_file("app.py")
        app.session_state["market_symbol"] = "XAUUSD"
        app.session_state["market_frames"] = frames
        app.session_state["live_price"] = float(frames["15-Minute"].iloc[-1]["close"])

        app.run()

        self.assertEqual(len(app.exception), 0)
        self.assertIn("current_indicators", app.session_state)
        self.assertEqual(app.session_state["market_symbol"], "XAUUSD")
        self.assertEqual(len(app.get("plotly_chart")), 2)

    def test_connection_does_not_switch_to_an_unrequested_instrument(self):
        with (
            patch.object(data_engine.mt5, "initialize", return_value=True),
            patch.object(data_engine, "get_available_symbols", return_value=["EURUSD", "GBPUSD"]),
            patch.object(data_engine, "get_market_frames") as fetch_frames,
        ):
            app = AppTest.from_file("app.py").run(timeout=15)
            next(button for button in app.button if button.label == "Connect to MT5").click()
            app.run(timeout=15)

        selectors = {widget.label: widget.value for widget in app.selectbox}
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(app.session_state["mt5_connected"])
        self.assertEqual(selectors["Instrument"], "Select broker instrument")
        fetch_frames.assert_not_called()


if __name__ == "__main__":
    unittest.main()