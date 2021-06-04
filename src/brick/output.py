import numpy as np

class Output:
    '''
    Packages AZURE2 output.
    (See the Section 8 of the AZURE2 Manual.)

    filename : Either the filename where the data can be read OR a NumPy array
               with the data.
    is_array : Is filename actually an array?

    e_com = center-of-mass energy
    e_x = excitation energy
    xs = cross section
    sf = S-factor
    com = center-of-mass
    err = error/uncertainty
    fit = AZURE2 calculation
    data = original data
    '''
    def __init__(self, filename, is_array=False):
        if is_array:
            self.contents = filename
        else:
            self.contents = np.loadtxt(filename)
        self.e_com = self.contents[:, 0]
        self.e_x = self.contents[:, 1]
        self.angle_com = self.contents[:, 2]
        self.xs_com_fit = self.contents[:, 3]
        self.sf_com_fit = self.contents[:, 4]
        self.xs_com_data = self.contents[:, 5]
        self.xs_err_com_data = self.contents[:, 6]
        self.sf_com_data = self.contents[:, 7]
        self.sf_err_com_data = self.contents[:, 8]


class OutputList:
    '''
    List of Output objects.
    '''
    def __init__(self, filename):
        with open(filename, 'r') as f:
            contents = f.read()
        self.data = []
        for section in contents.split('\n\n '):
            data_set = np.array([])
            for (i, row) in enumerate(section.split('\n')):
                data_row = np.array(list(map(float, row.split())))
                if data_row.shape[0] > 0:
                    if i == 0:
                        data_set = data_row
                    else:
                        data_set = np.vstack((data_set, data_row))
            self.data.append(Output(data_set, is_array=True))

        self.ns = list(map(lambda d: d.shape[0], self.data))
        self.ntot = sum(self.ns)
