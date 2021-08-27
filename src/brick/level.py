'''
Defines the Level class.
'''

from .constants import *

class Level:
    '''
    Simple data structure for storing the spin (total J), parity (+/-1),
    energy (MeV, excitation), and width (eV) of a level used in an AZURE2
    calculation.

    channel : channel pair (defined in AZURE2)
    radius  : channel radius
    index   : Which spin^{parity} level is this? (There are frequently more than
              one. Consistent with the language, these are zero-based.)
    '''
    def __init__(self, row_str):
        row = row_str.split()
        self.spin = float(row[J_INDEX])
        self.parity = int(row[PI_INDEX])
        self.energy = float(row[ENERGY_INDEX])
        self.energy_fixed = int(row[ENERGY_FIXED_INDEX])
        self.width = float(row[WIDTH_INDEX])
        self.width_fixed = int(int(row[WIDTH_FIXED_INDEX]) or self.width == 0)
        self.channel_radius = float(row[CHANNEL_RADIUS_INDEX])
        self.channel = int(row[CHANNEL_INDEX])
        self.separation_energy = float(row[SEPARATION_ENERGY_INDEX])
        self.include = int(row[LEVEL_INCLUDE_INDEX])

    def print(self):
        '''
        Prints a description of the level.
        '''
        sign = '+' if self.parity > 0 else '-'
        print(f'{self.spin}{sign} | \
{self.energy} MeV | {self.width} eV | channel {self.channel}')
