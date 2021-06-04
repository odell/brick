class Parameter:
    '''
    Defines a sampled (or "free") parameter by spin, parity, channel,
    rank, and whether it's an energy or width (kind).
    kind    : "energy" or "width"
              "width" can be the partial width or ANC (depending on how it was
              set up in AZURE2)
    channel : channel pair (defined in AZURE2; consistent with AZURE2,
              these are one-based)
    rank    : Which spin^{parity} level is this? (There are frequently
              more than one. Consistent with AZURE2, these are 
              one-based.)
    '''
    def __init__(self, spin, parity, kind, channel, rank=1, is_anc=False):
        self.spin = spin
        self.parity = parity
        self.kind = kind
        self.channel = int(channel)
        self.rank = rank
        
        jpi_label = '+' if self.parity == 1 else '-'
        subscript = f'{rank:d},{channel:d}'
        superscript = f'({jpi_label:s}{spin:.1f})'
        if self.kind == 'energy':
            self.label = r'$E_{%s}^{%s}$' % (subscript, superscript)
        elif self.kind == 'width':
            if is_anc:
                self.label = r'$C_{%s}^{%s}$' % (subscript, superscript)
            else:
                self.label = r'$\Gamma_{%s}^{%s}$' % (subscript, superscript)
        else:
            print('"kind" attribute must be either "energy" or "width"')


    def string(self):
        parity = '+' if self.parity == 1 else '-'
        return f'{self.spin}{parity} {self.kind} (number {self.rank}) in \
particle pair {self.channel}, {self.label}'


    def print(self):
        print(self.string())


class NormFactor:
    '''
    Defines a sampled normalization factor (n_i in the AZURE2 manual).
    '''
    def __init__(self, dataset_index):
        self.index = dataset_index
        self.label = r'$n_{%d}$' % (self.index)
