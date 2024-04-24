import collect
from collect.ripl.discrete_levels import Transition, Level
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
    assert len(lvls.levels) == 297
    assert len(lvls.levels[5].transitions) == 2
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


def test_reading_level():
    line = "  5   0.386700   6.5 -1             2                   (13/2-)  0                                                                                                                                                                                                                              0.000000  2    "
    obj = Level(line)
    assert obj.index == 5
    assert obj.energy == 0.3867
    assert obj.num_transitions == 2
    assert obj.spin == 6.5
    assert obj.parity == -1
    assert obj.half_life == 0.0


def test_level_transitions():
    level_line = "  5   2.285240   2.5  1  2.430E-13  3 c             (5/2+,7/2+)  0                                                                                                                                                                                                                              0.000000      "
    gamma_lines = [
        "                                          3     0.9050  3.702E-02  3.703E-02  4.330E-05",
        "                                          2     0.9144  3.702E-02  3.703E-02  1.016E-04",
        "                                          1     2.2852  9.256E-01  9.259E-01  3.820E-04",
    ]
    obj = Level(level_line)
    obj.parse_transitions(gamma_lines)
    assert len(obj.transitions) == obj.num_transitions
    assert obj.transitions[0].final_index == 3
    assert obj.transitions[1].energy == 0.9144


@pytest.mark.fishing
def test_all_level_lines(ripl_path):
    """Parse all level lines in all RIPL discrete files

    This is a very slow test

    """
    for fle in ripl_path.glob("*.dat"):
        with open(fle, "r") as f:
            lines = f.readlines()
        for line in lines:
            if len(line) > 2:
                try:
                    index = int(line[:5])
                    obj = Level(line)
                    print(line)
                except ValueError:
                    continue


@pytest.mark.fishing
def test_all_isotopes(ripl_path):
    """Parse all isotopes in the ripl database

    This is a very slow test

    """
    for fle in ripl_path.glob("*.dat"):
        with open(fle, "r") as f:
            lines = f.readlines()
        for line in lines:
            if len(line) > 2 and line[:2] != "  ":
                try:
                    index = int(line[:5])
                    continue
                except ValueError:
                    values = line.split()
                    print(values)
                    obj = collect.ripl.DiscreteLevels(
                        Z=int(values[2]), A=int(values[1])
                    )
                    print(line)
