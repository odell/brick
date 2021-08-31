'''
Tests the implementation of normalization factors in BRICK.

The test relies on a comparison of cross sections. The first result has the
normalization factor applied explicitly (to cross sections and cross section
uncertainties). The second relies on BRICK to write the normalization factor in
the correct location in the .azr file and pass it to AZURE2. The norm of the
relative difference between the two methods must be less than 1e-14.
'''

import numpy as np

from brick.azr import AZR

azr = AZR('12C+p.azr')

f = 1.1

theta = azr.config.get_input_values()
thetap = np.copy(theta)
thetap[-2] = f
thetap[-1] = f

mu1 = np.hstack(azr.predict(theta, dress_up=False))
sigma1 = mu1[:, [5, 6]]
sigma1 *= f

mu2 = np.hstack(azr.predict(thetap, dress_up=False))
sigma2 = mu2[:, [5, 6]]

# print('Column | Norm(Diff) | Norm(Relative Difference)')
# for i in range(9):
#     diff = mu1[:, i] - mu2[:, i]
#     rel_diff = diff / mu1[:, i]
#     print(f'{i+1} | {np.linalg.norm(diff):.4e} | {np.linalg.norm(rel_diff):.4e}')

rel_diff = np.linalg.norm((sigma1 - sigma2) / sigma1)

assert rel_diff < 1e-14, f'''
Normalization factor test failed. Relative differenece between applying
normalization factors explicitly and applying them via BRICK is {rel_diff}.
'''
