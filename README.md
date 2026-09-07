# Fractal Model — Reclaim Strength (RS) Engine

A Pine v6 indicator for TradingView. Tracks the latest confirmed C2 sweep/reclaim setup with two reference levels and groups historical C2-extreme survival rates by Reclaim Strength. Works on chart timeframes of 15 minutes and above.

## Install

Paste [scripts/fractal_reclaim_strength.pine](scripts/fractal_reclaim_strength.pine) into the Pine Editor, save, and add it to a standard candlestick chart. The engine, table, and drawings are hidden below 15 minutes. The active setup uses the chart timeframe; there is no multi-timeframe projection.

## Setup and metrics

C1, C2, C3, and C4 are four consecutive chart bars. A bullish C2 trades below C1's low and closes strictly above that low; a bearish C2 trades above C1's high and closes strictly below that high. A bar satisfying both directions is excluded. Zero-range C1 or C2 bars are excluded. A close beyond the opposite C1 extreme is allowed, so RS can exceed 100%.

- **RS:** bullish `(C2 close − C1 low) / C1 range × 100`; bearish `(C1 high − C2 close) / C1 range × 100`.
- **Sweep:** distance beyond the swept C1 extreme divided by C2's range. This is sweep depth, not the entire candle wick.
- **N:** number of setups with a closed C4 in that RS bucket. Bullish and bearish setups are pooled; overlapping setups are included.
- **Reach C4:** percentage that held the C2 extreme throughout C3. This means survival into C4, not reaching a price target.
- **Full C4:** percentage that held the C2 extreme throughout both C3 and C4.
- **XC2:** percentage that breached the C2 extreme in C3 or C4. `Full C4 + XC2 = 100%`, apart from display rounding.
- **Reach Δ:** bucket Reach C4 minus the whole sample's BASE Reach C4, in percentage points (`pp`). For example, 80% minus 60% is `+20 pp`.

A breach requires a strictly lower low (bullish) or higher high (bearish). Equality holds. RS buckets are `[0,10)`, `[10,25)`, `[25,50)`, `[50,75)`, `[75,100)`, and `[100,∞)`; a boundary value enters the higher bucket.

## Live behavior

A setup is established only at C2 close. Its swept C1 level and C2 extreme are drawn through C4; a breach changes the extreme line's color intrabar. At C4 close the setup leaves LIVE status and its lines disappear, even if the next bar has not opened.

Only the latest confirmed setup is drawn. Before replacing it with a new C2, the old setup's breach is checked and its state is recorded in the **Previous** row. `Replaced in C3 (unfinished)` describes its state at replacement, not its final outcome. Historical statistics independently measure every eligible setup at its own C4 close, including ones replaced on the live board. **Previous** is a replacement snapshot, not a trade log.

## Sample scope: chart data, not the offline research sample

The table computes directly from this chart's loaded bars, symbol/feed, timeframe, and session configuration. It does **not** import the 2019–2025 research dataset or reproduce its strict minute-completeness filter. The offline study required every minute in the C1–C4 calendar-aligned window; this indicator uses consecutive available chart bars, including bars adjacent across session gaps. These choices can materially change both N and the reported rates. Synthetic chart types also change the input OHLC; use standard candles for ordinary market-bar interpretation.

**All Available Bars** counts all eligible setups with C4 closed in the loaded chart history. **Last N Bars** selects C2 within exactly the latest N **closed** chart bars, ending at the latest confirmed bar. C2 must be no older than N−1 bars, and its C4 must have closed. The newest two C2 candidates are therefore not yet counted. Counters update on bar close and remain unchanged during the next open bar. Loading additional history can change the all-history sample.

Counters update incrementally. Windowed modes keep a fixed ring of N slots; all-history mode stores only six sets of counters. No growing event-history scan is performed on each bar.

Rates are descriptive and in-sample. They measure survival of an extreme, not trade wins, returns, or proven edge. Small buckets are less informative and overlapping observations are dependent. No CISD, entry, target, execution ordering, costs, or PnL is measured.

## Verification

Run `python scripts/verify_pine_algorithm.py` with Python 3. The dependency-free regression checks cover bucket boundaries, direction symmetry, strict reclaim/breach rules, C4 maturation, exact window expiry, bounded storage, and incremental counts against direct enumeration across 12,050 synthetic bars.

Run `python scripts/build_pine_regression.py regression.pine` to generate a separate TradingView test indicator from the production code. Compile it on a 15m-or-higher chart with default display inputs. It replaces market prices with controlled candles and asserts bullish/bearish replacement, unfinished replacement, C4 failure, and line cleanup at C4 close. Its green header reports the number of lifecycle checks passed. Use the original indicator for market charts.

For a separate arithmetic comparison, export closed, chronological chart bars as `{"bars": [{"high": 12, "low": 10, "close": 11}, ...]}` and run `python scripts/verify_pine_algorithm.py --ohlcv-json bars.json --window 500`. Omit `--window` for all history. This reference does not emulate TradingView's compiler or live tick engine; compile and check the Pine script in TradingView as well.
