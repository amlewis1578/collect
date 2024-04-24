import fortranformat as ff
import mendeleev
import sys
from pathlib import Path

class DiscreteLevels:
    """ Class to hold a full level scheme """

    def __init__(self,A,Z=None,X=None):
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

        self.symbol = f'{self.A}{self.X}'

        self.parse_ripl()

    
    def parse_ripl(self):
        """ method documentation """

        filename = f'z{self.Z:003}.dat'
        
        data_directory = Path(__file__).parent.parent / "data"  / "ripl" / "levels"
        
        data_file = data_directory / filename

        with open(data_file, 'r') as f:
            lines = f.readlines()

        # set up fortran read statements
        isotope_read_statement = ff.FortranRecordReader('(a5,6i5,2f12.6)')
        level_read_statement = ff.FortranRecordReader('(i3,1x,f10.6,1x,f5.1,i3,1x,(e10.3),i3,1x,a1)') 
        gamma_read_statement = ff.FortranRecordReader('(39x,i4,1x,f10.4,3(1x,e10.3))')

        # these files cover all isotopes of the element, so have to 
        # loop through to find the isotope of interest
        for i,line in enumerate(lines):
            if self.symbol in line:
                _, _, _, Nl, Ng, Nc, _, Sn, _ = isotope_read_statement.read(line)
                break
        
        # get isotope information 
        self.num_levels = Nl
        self.num_gammas = Ng
        self.num_complete = Nc
        self.Sn = Sn

        # grab just the lines relating to this isotope
        self.lines = lines[i+1:i+1+Nl+Ng]
        
        
                
