import numpy as np

from brick.azr import AZR

azr1 = AZR('12C+p.azr')
azr2 = AZR('12C+p_1.azr')

theta = azr2.config.get_input_values()

mu1 = np.hstack(azr1.predict(theta, dress_up=False))
mu2 = np.hstack(azr2.predict(theta, dress_up=False))
abs_diff = np.linalg.norm(mu1-mu2)

print(f'Absolute difference = {abs_diff}.')
print('Expected diffierence is 0.')
