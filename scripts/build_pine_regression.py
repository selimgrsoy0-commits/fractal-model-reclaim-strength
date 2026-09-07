"""Generate a synthetic-OHLC harness around the production Pine implementation.

python scripts/build_pine_regression.py output.pine
Compile the output separately on a >=15m TradingView chart. Runtime assertions
exercise the actual setup/line lifecycle on confirmed historical bars, not a
Python copy. This fixture is a test indicator, not a market signal.
"""

from pathlib import Path
import re
import sys


def build():
    source = (Path(__file__).parent / 'fractal_reclaim_strength.pine').read_text(encoding='utf-8')
    declaration = 'indicator("Fractal Reclaim Strength",'
    if source.count(declaration) != 1:
        raise ValueError('Production indicator declaration changed; update the fixture generator')
    source = source.replace(declaration, 'indicator("Fractal Reclaim Regression",', 1)
    # Replace price series only; assertions below use the production variables.
    source = re.sub(r'\b(high|low|close)\b', lambda m: 'fixture_' + m[0], source)
    bars = [(10., 10., 10.)] * 32
    # Bull replacement breaks old C3; new setup then holds through C4.
    bars[0:5] = [(12., 10., 11.), (11.5, 9., 10.5), (11., 8., 10.), (11., 8., 10.), (11., 8., 10.)]
    # C4 breaks, without a new setup; it must expire at that close.
    bars[8:12] = [(12., 10., 11.), (11.5, 9., 10.5), (11., 9., 10.), (11., 8., 8.5)]
    # Replacement while the old setup is intact must be marked unfinished.
    bars[16:21] = [(12., 10., 11.), (11.5, 9., 10.5), (12., 9.5, 11.), (12., 9.5, 11.), (12., 9.5, 11.)]
    # Mirror the first sequence to exercise bearish replacement and equality.
    bars[24:29] = [(30-hlc[1], 30-hlc[0], 30-hlc[2]) for hlc in bars[:5]]
    fixture = '\nint fixture_phase = bar_index % 32\n'
    for col, name in enumerate(('high', 'low', 'close')):
        values = ', '.join(str(b[col]) for b in bars)
        fixture += f'var float[] fixture_{name}_values = array.from({values})\n'
        fixture += f'float fixture_{name} = array.get(fixture_{name}_values, fixture_phase)\n'
    lines = source.splitlines(keepends=True)
    source = ''.join(lines[:2]) + fixture + ''.join(lines[2:])
    source += '''

// Assertions run after the production state update, line cleanup and table.
var int fixture_checks = 0
if barstate.isconfirmed and not is_too_low
    if fixture_phase == 2 or fixture_phase == 26
        string expected_dir = fixture_phase == 2 ? "Bull" : "Bear"
        if previous_setup != "Previous: " + expected_dir + " · Invalidated C3" or active_dir != expected_dir or active_c2_bar != bar_index or active_failed
            runtime.error("Replacement lost the old C3 breach or tainted the new setup")
        fixture_checks += 1
    if fixture_phase == 4 or fixture_phase == 20 or fixture_phase == 28
        if not is_setup_expired or active_failed or not na(l_swept) or not na(l_extreme) or not na(lbl_extreme)
            runtime.error("Held C4 did not expire and remove its lines at close")
        fixture_checks += 1
    if fixture_phase == 11
        if not is_setup_expired or not active_failed or active_failed_bar != bar_index or not na(l_swept) or not na(l_extreme) or not na(lbl_extreme)
            runtime.error("Broken C4 did not retain failure and expire at close")
        fixture_checks += 1
    if fixture_phase == 18
        if previous_setup != "Previous: Bull · Replaced in C3 (unfinished)" or active_dir != "Bear" or active_failed
            runtime.error("Unfinished replacement was reported as a completed outcome")
        fixture_checks += 1
if barstate.islast and not na(t)
    table.cell(t, 0, 0, "REGRESSION: " + str.tostring(fixture_checks) + " checks passed", bgcolor=color.green, text_color=color.white)
'''
    return source


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python scripts/build_pine_regression.py output.pine')
    Path(sys.argv[1]).write_text(build(), encoding='utf-8')
