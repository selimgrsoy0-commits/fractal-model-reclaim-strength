"""Independent OHLC reference and ring-window regressions (stdlib only).

Tests: python scripts/verify_pine_algorithm.py
Chart comparison: python scripts/verify_pine_algorithm.py --ohlcv-json bars.json
JSON: {"bars": [{"high": 12, "low": 10, "close": 11}, ...]}
Provide CLOSED chronological chart bars; no resampling or coverage filter.
Checks arithmetic/window design, not the Pine compiler or live tick engine.
"""

import argparse
from bisect import bisect_right
from dataclasses import dataclass
import json
from pathlib import Path
import random
import unittest


@dataclass(frozen=True)
class Candle:
    high: float
    low: float
    close: float


def setup(c1, c2):
    if c1.high <= c1.low or c2.high <= c2.low:
        return None
    bull = c2.low < c1.low < c2.close
    bear = c2.close < c1.high < c2.high
    if bull == bear:
        return None
    rs = 100 * ((c2.close - c1.low) if bull else (c1.high - c2.close)) / (c1.high - c1.low)
    return bull, bisect_right([10, 25, 50, 75, 100], rs)


def event(c1, c2, c3, c4):
    candidate = setup(c1, c2)
    if candidate is None:
        return None
    bull, bucket = candidate
    holds3 = c3.low >= c2.low if bull else c3.high <= c2.high
    holds4 = c4.low >= c2.low if bull else c4.high <= c2.high
    return bucket, holds3, holds3 and holds4, not (holds3 and holds4)


def reference(bars, window=0):
    """Directly enumerate eligible C2s, independently of ring storage."""
    counts = [[0] * 4 for _ in range(6)]
    start = max(1, len(bars) - window) if window else 1
    for c2_index in range(start, len(bars) - 2):
        outcome = event(*bars[c2_index - 1:c2_index + 3])
        if outcome is not None:
            b, reach, full, broken = outcome
            for col, value in enumerate((1, reach, full, broken)):
                counts[b][col] += int(value)
    return counts


class RingCounter:
    """Model of Pine's bounded storage, checked against direct enumeration."""

    def __init__(self, window=0):
        if window and window < 3:
            raise ValueError('Window must include C2 through C4')
        self.window = window
        self.slots = [-1] * window
        self.counts = [[0] * 4 for _ in range(6)]

    def adjust(self, code, change):
        b = code % 8
        for col, flag in enumerate((1, (code // 8) % 2, (code // 16) % 2, (code // 32) % 2)):
            self.counts[b][col] += change * flag

    def close(self, index, outcome):
        if index < 3:
            return
        if self.window:
            slot = index % self.window
            if self.slots[slot] >= 0:
                self.adjust(self.slots[slot], -1)
            self.slots[slot] = -1
        if outcome is not None:
            b, reach, full, broken = outcome
            code = b + 8 * reach + 16 * full + 32 * broken
            self.adjust(code, 1)
            if self.window:
                self.slots[(index - 2) % self.window] = code


def reach_delta(row, counts):
    total = sum(r[0] for r in counts)
    if not row[0] or not total:
        return None
    return 100 * row[1] / row[0] - 100 * sum(r[1] for r in counts) / total


def print_table(counts):
    print('RS | N | Reach C4 | Full C4 | XC2 | Reach delta (pp)')
    labels = ['0-10%', '10-25%', '25-50%', '50-75%', '75-100%', '>=100%']
    for label, row in zip(labels, counts):
        if row[0]:
            rates = ' | '.join(f'{100 * k / row[0]:.1f}%' for k in row[1:])
            print(f'{label} | {row[0]} | {rates} | {reach_delta(row, counts):+.1f} pp')
        else:
            print(f'{label} | 0 | - | - | - | -')
    base = [sum(row[c] for row in counts) for c in range(4)]
    rates = ' | '.join(f'{100 * k / base[0]:.1f}%' for k in base[1:]) if base[0] else '- | - | -'
    print(f'BASE | {base[0]} | {rates}')


class RegressionTests(unittest.TestCase):
    def test_bin_boundaries_and_direction_symmetry(self):
        c1 = Candle(200, 100, 150)
        mirror = lambda c: Candle(400 - c.low, 400 - c.high, 400 - c.close)
        for rs, expected in [(0.5, 0), (9.5, 0), (10, 1), (25, 2), (50, 3), (75, 4), (100, 5), (125, 5)]:
            c2 = Candle(max(190, 100 + rs), 90, 100 + rs)
            self.assertEqual(setup(c1, c2), (True, expected))
            self.assertEqual(setup(mirror(c1), mirror(c2)), (False, expected))

    def test_dual_zero_range_and_strict_reclaim(self):
        c1 = Candle(12, 10, 11)
        for c2 in [Candle(13, 9, 11), Candle(11, 11, 11), Candle(11, 9, 10), Candle(12, 10, 11)]:
            self.assertIsNone(setup(c1, c2))
        self.assertIsNone(setup(Candle(10, 10, 10), Candle(11, 9, 10.5)))

    def test_extreme_equality_and_outcome_definitions(self):
        c1, c2 = Candle(12, 10, 11), Candle(11.5, 9, 10.5)
        held, broken = Candle(11, 9, 10), Candle(11, 8, 10)
        self.assertEqual(event(c1, c2, held, held)[1:], (True, True, False))
        self.assertEqual(event(c1, c2, held, broken)[1:], (True, False, True))
        self.assertEqual(event(c1, c2, broken, held)[1:], (False, False, True))

    def test_maturation_requires_c4(self):
        bars = [Candle(12, 10, 11), Candle(11.5, 9, 10.5), Candle(11, 9, 10), Candle(11, 9, 10)]
        self.assertEqual(sum(r[0] for r in reference(bars[:3])), 0)
        self.assertEqual(sum(r[0] for r in reference(bars)), 1)

    def test_expiry_exactly_n_bars_without_new_event(self):
        for window in (500, 1000, 5000):
            ring = RingCounter(window)
            ring.close(3, (1, True, True, False))  # C2 at index 1
            for i in range(4, window + 1):
                ring.close(i, None)
            self.assertEqual(ring.counts[1], [1, 1, 1, 0])  # age N-1
            ring.close(window + 1, None)
            self.assertEqual(ring.counts[1], [0, 0, 0, 0])  # age N

    def test_random_stream_matches_direct_enumeration(self):
        rng = random.Random(20260907)
        bars = []
        price = 1000
        for _ in range(12050):
            close = price + rng.randint(-8, 8)
            bars.append(Candle(max(price, close) + rng.randint(0, 6), min(price, close) - rng.randint(0, 6), close))
            price = close
        for window in (0, 500, 1000, 5000):
            ring = RingCounter(window)
            for i in range(len(bars)):
                ring.close(i, event(*bars[i-3:i+1]) if i >= 3 else None)
                if i % 251 == 0 or i in (499, 500, 501, 999, 1000, 4999, 5000, 5001, len(bars)-1):
                    self.assertEqual(ring.counts, reference(bars[:i+1], window), (window, i))
                    for n, reach, full, broken in ring.counts:
                        self.assertTrue(0 <= full <= reach <= n)
                        self.assertEqual(full + broken, n)
            self.assertEqual(len(ring.slots), window)

    def test_reach_delta_uses_reach_percentage_points(self):
        counts = [[10, 8, 2, 8], [10, 4, 4, 6]] + [[0] * 4 for _ in range(4)]
        self.assertAlmostEqual(reach_delta(counts[0], counts), 20)
        self.assertIsNone(reach_delta(counts[2], counts))

    def test_all_history_has_no_event_storage(self):
        ring = RingCounter()
        for i in range(3, 100103):
            ring.close(i, (5, True, True, False))
        self.assertEqual(ring.counts[5], [100100, 100100, 100100, 0])
        self.assertEqual(ring.slots, [])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ohlcv-json', type=Path)
    parser.add_argument('--window', type=int, choices=(0, 500, 1000, 5000), default=0)
    args = parser.parse_args()
    if args.ohlcv_json:
        payload = json.loads(args.ohlcv_json.read_text(encoding='utf-8-sig'))
        bars = [Candle(float(b['high']), float(b['low']), float(b['close'])) for b in payload['bars']]
        print_table(reference(bars, args.window))
    else:
        unittest.main(argv=['verify_pine_algorithm'], verbosity=2)
