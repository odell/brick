# with open('../../setup.cfg', 'r') as f:
#     cfg = f.read()
# 
# version_string = list(filter(
#     lambda s: 'version' in s, cfg.split('\n')
# ))[0].split()[2]

from .azr import AZR

__version__ = '0.2.3'
