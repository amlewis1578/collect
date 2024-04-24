import fortranformat as ff
import mendeleev
import sys
from pathlib import Path


class DiscreteLevels:
    """Class to hold a full level scheme"""

    def __init__(self, A, Z=None, X=None):
        self.A = int(A)

        if Z is not None:
            self.Z = Z
            self.X = mendeleev.element(self.Z).symbol
        elif X is not None:
            self.X = X.captialize()
            self.Z = mendeleev.element(X).atomic_number
        else:
            print("Need to supply Z or X.")
            sys.exit()

        self.symbol = f"{self.A}{self.X}"

        self.parse_ripl()

    def parse_ripl(self):
        """method documentation"""

        filename = f"z{self.Z:003}.dat"

        data_directory = Path(__file__).parent.parent / "data" / "ripl" / "levels"

        data_file = data_directory / filename

        with open(data_file, "r") as f:
            lines = f.readlines()

        # set up fortran read statements
        isotope_read_statement = ff.FortranRecordReader("(a5,6i5,2f12.6)")

        # these files cover all isotopes of the element, so have to
        # loop through to find the isotope of interest
        for i, line in enumerate(lines):
            if self.symbol in line:
                _, _, _, Nl, Ng, Nc, _, Sn, _ = isotope_read_statement.read(line)
                break

        # get isotope information
        self.num_levels = Nl
        self.num_gammas = Ng
        self.num_complete = Nc
        self.Sn = Sn

        # grab just the lines relating to this isotope
        self.lines = lines[i + 1 : i + 1 + Nl + Ng]


class Level:
    """Class to hold a single level in a level scheme. All energies are in MeV.

    Parameters
    ----------
    line : str
        The RIPL file line for the level

    Attributes
    ----------
    index : int
        Index of the level

    energy : float
        Energy of the level in MeV

    spin : float
        Spin of the level

    parity : int
        Parity of the level (-1 or 1)

    half_life : float
        half-live of the level in sections, if known. 0 if unknown.

    num_transitions : int
        number of transitions from this level

    Methods
    -------
    parse_line
        Function to parse the RIPL file line

    """

    def __init__(self, line):
        self.parse_line(line)

    def parse_line(self, line):
        """Function to parse the RIPL file line

        Parameters
        ----------
        line : str
            the line from the RIPL file

        Returns
        -------
        None

        """

        # set up gamma fortran read statement
        level_read_statement = ff.FortranRecordReader(
            "(i3,1x,f10.6,1x,f5.1,i3,1x,(e10.3),i3)"
        )

        # parse line
        Nl, Elv, J, p, T, Ng = level_read_statement.read(line)

        self.index = Nl
        self.energy = Elv
        self.spin = J
        self.parity = p
        self.half_life = T
        self.num_transitions = Ng


class Transition:
    """Class to hold a transition between two levels in a level scheme. All energies are in MeV

    Parameters
    ----------
    initial : int
        Index of the initial level

    line : str
        The RIPL file line for the transition

    Attributes
    ----------
    initial_index : int
        Index of the initial level

    final_index : int
        Index of the final level

    energy : float
        Energy of the transition in MeV

    probability : float
        Probability that the initial level will decay by this transition

    gamma_probability : float
        Probability that the intial level will decay by this transition, and by
        emission of a gamma (not internal conversion)

    alpha : float
        Internal conversion coefficient known as alpha

    Methods
    -------
    parse_line
        Function to parse the RIPL file line


    """

    def __init__(self, initial, line):
        self.intial_index = initial
        self.parse_line(line)

    def parse_line(self, line):
        """Function to parse the RIPL file line

        Parameters
        ----------
        line : str
            the line from the RIPL file

        Returns
        -------
        None

        """

        # set up gamma fortran read statement
        gamma_read_statement = ff.FortranRecordReader("(39x,i4,1x,f10.4,3(1x,e10.3))")

        # parse the line
        Nf, Eg, Pg, Pe, ICC = gamma_read_statement.read(line)

        self.final_index = Nf
        self.energy = Eg
        self.gamma_prob = Pg
        self.probability = Pe
        self.alpha = ICC
