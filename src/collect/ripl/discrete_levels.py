import fortranformat as ff
import mendeleev
import sys
from pathlib import Path


class DiscreteLevels:
    """Class to hold a full level scheme
    
    Parameters
    ----------
    A : int
        Mass number of the isotope

    Z : int, optional
        Z of the isotope

    X : str, optional
        Chemical symbol of the isotope

    Attributes
    ----------
    A : int
        Mass number of the isotope

    Z : int
        Z of the isotope

    X : str
        Chemical symbol of the isotope   

    symbol : str
        Symbol for the isotope, AAAXX

    levels : list of Level objects
        The levels in the isotope

    num_levels  : int
        Number of levels

    num_transitions : int
        Total number of gammas

    num_complete : int
        Number of levels in the RIPL "complete" level scheme

    Sn : float
        Neutron separation energy in MeV

    Methods
    -------
    parse_ripl
        Function to collect and parse the RIPL file
    
    
    """

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
        """ Function to collect and parse the RIPL file
        
        Parameters
        ----------
        None

        Results
        -------
        None

        """

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
        self.num_transitions = Ng
        self.num_complete = Nc
        self.Sn = Sn

        # grab just the lines relating to this isotope
        self.lines = lines[i + 1 : i + 1 + Nl + Ng]
        self.levels = []

        while len(self.lines) > 0:
            lvl_line = self.lines.pop(0)
            self.levels.append(Level(lvl_line))

            if self.levels[-1].num_transitions > 0:
                gamma_lines = self.lines[: self.levels[-1].num_transitions]
                self.levels[-1].parse_transitions(gamma_lines)
                self.lines = self.lines[self.levels[-1].num_transitions :]

    def __repr__(self):
        rep = f"RIPL level scheme for {self.symbol}\n\t{self.num_levels} total levels\n"
        rep += f"\t{self.num_complete} levels in the complete level scheme"
        return rep


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
        half-live of the level in seconds, if known. 0 if unknown.

    num_transitions : int
        number of transitions from this level

    transitions : list of Transition objects
        The transitions from this level

    Methods
    -------
    parse_line
        Function to parse the RIPL file line

    parse_transitions
        Function to parse the transition lines
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
        self.transitions = []

    def parse_transitions(self, transition_lines):
        """Function to parse the transition lines

        Parameters
        ----------
        transition_lines : list of str
            the RIPL file lines

        Returns
        -------
        None

        """

        for line in transition_lines:
            self.transitions.append(Transition(self.index, line))

    def __repr__(self):
        rep = f"Level {self.index} at {self.energy} MeV with {self.num_transitions} transitions"
        for transition in self.transitions:
            rep += f"\n\t{transition.final_index}: {round(100*transition.probability,3)}%"
        return rep

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
        Probability that the initial level will decay by this transition, and by
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

    def __repr__(self):
        rep = f"Transition from level {self.intial_index} to level {self.final_index}\n\tenergy: {self.energy} MeV\n"
        rep += f"\tinternal conversion coefficent: {self.alpha}\n"
        rep += f"\tchance of gamma emission: {round(100*self.gamma_prob/self.probability,2)}%"
        return rep