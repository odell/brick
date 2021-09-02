import numpy as np

from brick.azr import AZR

azr = AZR('12C+p.azr')
azr.use_gsl = True
azr.ext_capture_file = 'output/intEC.dat'

theta = azr.config.get_input_values()

mu = azr.predict(theta, dress_up=False)[0]
azure2_output = np.loadtxt('output/AZUREOut_aa=1_R=2.out')

_, n = mu.shape

for i in range(n):
    print(i, np.linalg.norm(mu[:, i] - azure2_output[:, i]))

print(f'{np.linalg.norm(mu - azure2_output):.8e}')
