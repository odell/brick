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
    def __init__(self, spin, parity, energy, energy_fixed, width, width_fixed,
                 radius, channel, separation_energy):
        self.spin = spin
        self.parity = parity
        self.energy = energy
        self.energy_fixed = energy_fixed
        self.width = width
        self.width_fixed = width_fixed
        self.channel_radius = radius
        self.channel = channel
        self.separation_energy = separation_energy


    def describe(self):
        sign = '+' if self.parity > 0 else '-'
        print(f'{self.spin}{sign} | \
{self.energy} MeV | {self.width} eV | channel {self.channel}')
