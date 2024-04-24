import collect
from collect.ripl.discrete_levels import Transition
from pathlib import Path
import pytest


@pytest.fixture
def ripl_path():
    ripl_path = Path(__file__).parent.parent.absolute()
    ripl_path = ripl_path / "src" / "collect" / "data" / "ripl" / "levels"
    return ripl_path


def test_reading_files():
    lvls = collect.ripl.DiscreteLevels(A=56, Z=26)
    assert lvls.X == "Fe"
    assert len(lvls.lines) == 297 + 426
    assert lvls.Sn == 11.19706


def test_reading_gamma():
    line = "                                         15     0.9459  9.342E-01  9.346E-01  3.810E-04"
    obj = Transition(17, line)
    assert obj.energy == 0.9459
    assert obj.alpha == 3.81e-04
    assert obj.final_index == 15
    assert obj.intial_index == 17


@pytest.mark.fishing
def test_all_gamma_lines(ripl_path):
    """Parse all gamma lines in all RIPL discrete files

    This is a very slow test

    """
    for fle in ripl_path.glob("*.dat"):
        with open(fle, "r") as f:
            lines = f.readlines()
        for line in lines:
            if len(line) > 2 and line[:5] == " " * 5:
                obj = Transition(100, line)
                print(line)
