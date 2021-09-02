'''
Tests the implementation of various features of BRICK.

* normalization factors
* energy shifts
'''

import unittest
import numpy as np

from brick.azr import AZR

class BRICKTests(unittest.TestCase):
    '''
    Suite of BRICK tests.
    '''

    def setUp(self):
        self.azr = AZR('12C+p.azr')


    def test_output(self):
        '''
        Tests the consistency of AZURE2 and BRICK output.

        The test runs BRICK at parameter point theta. The AZURE2-generated
        output is stored in the output directory. The absolute difference ought
        to be 0.
        '''
        theta = self.azr.config.get_input_values()
        self.azr.use_gsl = True
        self.azr.ext_capture_file = 'output/intEC.dat'
        mu = self.azr.predict(theta, dress_up=False)[0]
        azure2_output = np.loadtxt('output/AZUREOut_aa=1_R=2.out')

        abs_diff = np.linalg.norm(mu - azure2_output)

        self.assertTrue(abs_diff == 0, msg=f'''
Output test failed. The output generated with AZURE2 with the values in the
input file does not match the output generated with BRICK with the same values.
The norm of the absolute difference is {abs_diff}.
''')


    def test_norm_factors(self, norm_factor=1.1):
        '''
        Tests the implementation of normalization factors in BRICK.

        The test relies on a comparison of cross sections. The first result has the
        normalization factor applied explicitly (to cross sections and cross section
        uncertainties). The second relies on BRICK to write the normalization factor in
        the correct location in the .azr file and pass it to AZURE2. The norm of the
        relative difference between the two methods must be less than 1e-14.
        '''

        theta0 = self.azr.config.get_input_values()
        theta1 = np.copy(theta0)
        theta1[-2] = norm_factor
        theta1[-1] = norm_factor

        # Data with normalization factors set to 1.
        mu1 = np.hstack(self.azr.predict(theta0, dress_up=False))
        sigma1 = mu1[:, [5, 6]]
        # Apply normalization factor explicitly.
        sigma1 *= norm_factor

        # Data with normalization factor set to norm_factor.
        mu2 = np.hstack(self.azr.predict(theta1, dress_up=False))
        sigma2 = mu2[:, [5, 6]]

        # Compute the norm of the relative difference.
        rel_diff = np.linalg.norm((sigma1 - sigma2) / sigma1)

        self.assertTrue(rel_diff < 1e-14, msg=f'''
Normalization factor test failed. Relative differenece between applying
normalization factors explicitly and applying them via BRICK is {rel_diff}.
''')


    def test_energy_shift(self):
        '''
        Tests the implementation of energy shifts in BRICK.

        The test relies on a comparison of energies. The first result shifts the
        Vogl energies through BRICK. The second uses a copy of the Vogl data
        with the shift applied pre-AZURE2. The norm of the relative difference
        between the two methods must be less than 1e-14.
        '''
        SHIFT = 0.001 # MeV, lab

        vogl_data = np.loadtxt('data/vogl.dat')
        n = vogl_data.shape[0]
        vogl_data[:, 0] += SHIFT
        np.savetxt('data/vogl_shifted.dat', vogl_data)

        azr = AZR('12C+p_1.azr')

        theta = np.hstack((azr.config.get_input_values(), [SHIFT]))
        shifted_data = [(0, azr.config.data.segments[0].shift_energies(SHIFT))]

        mu = azr.predict(theta, mod_data=shifted_data, dress_up=False)[0]

        energies_1 = mu[:n, 0]
        energies_2 = mu[n:, 0]

        rel_diff = np.linalg.norm((energies_1 - energies_2) / energies_1)
        self.assertTrue(rel_diff < 1e-14, msg=f'''
Energy shift test failed. Relative difference between BRICK-shifted and
explicitly shifted energies is {rel_diff}.
''')


if __name__ == 'main':
    unittest.main()
