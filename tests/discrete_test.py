import collect
from pathlib import Path


def test_reading_files():
    lvls = collect.ripl.DiscreteLevels(A=56,Z=26)
    assert lvls.X == 'Fe'
    assert len(lvls.lines) == 297+426
    assert lvls.Sn == 11.19706
