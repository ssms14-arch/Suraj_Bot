import unittest

import numpy as np
import pandas as pd

from smc_analysis import analyze_smc


class SmcAnalysisTests(unittest.TestCase):
    def test_analyzes_mt5_ohlcv_candles(self):
        candle_count = 240
        positions = np.arange(candle_count)
        close = 100 + np.sin(positions / 5) * 3 + positions * 0.03
        open_price = close + np.sin(positions / 3) * 0.4
        candles = pd.DataFrame(
            {
                "time": pd.date_range("2026-01-01", periods=candle_count, freq="15min"),
                "open": open_price,
                "high": np.maximum(open_price, close) + 0.5,
                "low": np.minimum(open_price, close) - 0.5,
                "close": close,
                "tick_volume": 500 + positions,
            }
        )

        result = analyze_smc(candles)

        self.assertEqual(len(result["swings"]), candle_count)
        self.assertEqual(len(result["structure"]), candle_count)
        self.assertEqual(len(result["fvg"]), candle_count)
        self.assertEqual(len(result["order_blocks"]), candle_count)
        self.assertEqual(len(result["liquidity"]), candle_count)
        self.assertIn(result["bias"], {"BULLISH", "BEARISH"})


if __name__ == "__main__":
    unittest.main()