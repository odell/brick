'''
Class to read and write the contents of an AZURE2 input file.
The purpose is to remove as much of this work from AZR as possible.
'''

from . import utility
from .data import Data
from .nodata import Test
from .parameter import Parameter

class Config:
    def __init__(self, input_filename, parameters=None):
        self.input_filename = input_filename
        self.input_filename = input_filename
        self.input_file_contents = utility.read_input_file(input_filename)
        self.initial_levels = utility.read_levels(input_filename)
        self.data = Data(self.input_filename)
        self.test = Test(self.input_filename)

        if parameters is None:
            self.parameters = []
            jpis = []
            for group in self.initial_levels:
                # grab the J^pi from the first row in the group
                jpi = group[0].spin*group[0].parity
                # add it to the list
                jpis.append(jpi)
                for (i, sublevel) in enumerate(group):
                    spin = sublevel.spin
                    parity = sublevel.parity
                    rank = jpis.count(jpi)
                    if i == 0:
                        if not sublevel.energy_fixed:
                            self.parameters.append(Parameter(spin, parity, 'energy', i+1, rank=rank))
                    if not sublevel.width_fixed:
                        if sublevel.energy < sublevel.separation_energy:
                            self.parameters.append(
                                Parameter(spin, parity, 'width', i+1, rank=rank,
                                          is_anc=True)
                            )
                        else:
                            self.parameters.append(
                                Parameter(spin, parity, 'width', i+1, rank=rank)
                            )
        else:
            self.parameters = parameters

        Jpi = [l[0].spin*l[0].parity for l in self.initial_levels]
        self.addresses = []
        for p in self.parameters:
            jpi = p.spin*p.parity
            i = Jpi.index(jpi)
            i += p.rank-1 # convert from one-based count to zero-based index
            j = p.channel-1 # convert from one-based count to zero-based index
            self.addresses.append([i, j, p.kind])

        self.n1 = len(self.parameters)
        self.n2 = len(self.data.norm_segment_indices)
        # number of free parameters
        self.nd = self.n1 + self.n2

        self.labels = []
        for i in range(self.n1):
            self.labels.append(self.parameters[i].label)
        for i in self.data.norm_segment_indices:
            self.labels.append(self.data.all_segments[i].nf.label)


    def generate_levels(self, theta):
        levels = self.initial_levels.copy()
        for (theta_i, address) in zip(theta, self.addresses):
            i, j, kind = address
            if kind == 'energy':
                '''
                Set the energy for each channel in this level to the prescribed
                energy.
                '''
                for sl in levels[i]:
                    sl.energy = theta_i
            else:
                setattr(levels[i][j], kind, theta_i)
        return [l for sublevel in levels for l in sublevel]


    def get_input_values(self):
        '''
        Returns the values of the sampled parameters in the input file.
        '''
        values = [getattr(self.initial_levels[i][j], kind) for (i, j, kind) in
                  self.addresses]
        for i in self.data.norm_segment_indices:
            values.append(self.data.all_segments[i].norm_factor)
        return values


    def update_data_directories(self, new_dir, contents):
        '''
        The data needs to be stored in a new location (new_dir), so the input
        has to reflect that. In preparation, the contents of the input file are
        updated here.
        '''
        contents = self.data.update_all_dir(new_dir, contents)
        return self.data.write_segments(contents)


    def generate_workspace(self, theta, prepend='', mod_data=None):
        '''
        Config handles the configuration of the calculation. That includes:
        * mapping theta to the relevant values in the input file
        * setting up the appropriate workspace for AZR to operate in
        '''
        contents = self.input_file_contents.copy()

        new_levels = self.generate_levels(theta[:self.n1])
        contents = self.data.update_norm_factors(theta[self.n1:self.n1+self.n2],
            contents)

        input_filename, output_dir, data_dir = utility.random_workspace(prepend=prepend)


        if mod_data is not None:
            utility.write_input_file(contents, new_levels, input_filename,
                output_dir, data_dir=data_dir)
            self.data.update_all_dir(data_dir, contents)
            for (i, data) in mod_data:
                self.data.segments[i].update_dir(data_dir, data)
        else:
            utility.write_input_file(contents, new_levels, input_filename,
                output_dir)

        return input_filename, output_dir, data_dir

    def generate_workspace_extrap(self, theta, segment_indices=None):
        '''
        Similar to generate_workspace, except the test segments are updated
        rather than the data segments.
        '''
        contents = self.input_file_contents.copy()

        # Map theta to a new list of levels.
        new_levels = self.generate_levels(theta)

        # What extrapolation files need to be read?
        # If the user specifies the indices of the segments, then make sure
        # those are "include"d in the calculation and everything else is
        # excluded.
        t = Test('', contents=contents)
        if segment_indices is not None:
            for (i, test_segment) in enumerate(t.all_segments):
                test_segment.include = i in segment_indices
            t.write_segments(contents)

        # Write the updated contents to the input file and run.
        input_filename, output_dir = utility.random_output_dir_filename()
        utility.write_input_file(contents, new_levels, input_filename,
                                 output_dir)
        return input_filename, output_dir, t.get_output_files()
