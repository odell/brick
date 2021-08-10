'''
Defines classes for interacting with AZURE2.
'''

import os
import shutil
import numpy as np
from . import level
from . import utility
from .parameter import Parameter
from .output import Output
from .data import Data
from .nodata import Test
from .configuration import Config

class AZR:
    '''
    Object that manages the communication between Python and AZURE2.

    Attributes specified at instantiation:
    input_filename          : .azr file
    parameters              : list of Parameter instances (sampled parameters)
    output_filenames        : Which output files (AZUREOut_*.out) are read?
    extrap_filenames        : Which output files (AZUREOut_*.extrap) are read?

    Other attributes (given default values below):
    use_brune               : Bool that indicates the use of the Brune
                              parameterization.
    use_gsl                 : Bool that indicates the use of GSL Coulomb functions.
    ext_par_file            : Filename where parameter values can be read.
    ext_capture_file        : Filename where external capture integral results have
                              been stored.
    command                 : Name of AZURE2 binary.
    '''
    def __init__(self, input_filename, parameters=None, output_filenames=None,
                 extrap_filenames=None):
        # Give default values to attributes that are not specified at
        # instantiation. These values must be changed *after* instantiation.
        self.use_brune = True
        self.use_gsl = True
        self.ext_par_file = '\n'
        self.ext_capture_file = '\n'
        self.ext_capture_file_extrap = '\n'
        self.command = 'AZURE2'
        self.root_directory = ''
        
        self.config = Config(input_filename, parameters=parameters)

        '''
        If parameters are not specified, they are inferred from the input file.
        '''
        if parameters is None:
            self.parameters = self.config.parameters.copy()
        else:
            self.parameters = parameters.copy()

        '''
        If output files are not specified, they are inferred from the input file.
        '''
        if output_filenames is None:
            self.output_filenames = self.config.data.output_files
        else:
            self.output_filenames = output_filenames

        '''
        If extrapolation files are not specified, they are inferred from the input file.
        '''
        if extrap_filenames is None:
            self.extrap_filenames = self.config.test.output_files
        else:
            self.extrap_filenames = extrap_filenames


    def predict(self, theta, mod_data=None, dress_up=True, full_output=False):
        '''
        Takes:
            * a point in parameter space, theta.
            * dress_up    : Use Output class.
            * full_output : Return reduced width amplitudes as well.
            * mod_data    : Do any parametes in theta modify the original data?
        Does:
            * creates a random filename ([rand].azr)
            * creates a (similarly) random output directory (output_[rand]/)
            * writes the new Levels to a [rand].azr
            * writes output directory to [rand].azr
            * runs AZURE2 with [rand].azr
            * reads observable from output_[rand]/output_filename
            * deletes [rand].azr
            * deletes output_[rand]/
            * deletes data_[rand]/
        Returns:
            * predicted values and (optionally) reduced width amplitudes.
        '''

        workspace = self.config.generate_workspace(
            theta,
            prepend=self.root_directory,
            mod_data=mod_data
        )
        input_filename, output_dir, data_dir = workspace

        try:
            response = utility.run_AZURE2(input_filename, choice=1,
                use_brune=self.use_brune, ext_par_file=self.ext_par_file,
                ext_capture_file=self.ext_capture_file, use_gsl=self.use_gsl,
                command=self.command)
        except:
            shutil.rmtree(output_dir)
            shutil.rmtree(data_dir)
            os.remove(input_filename)
            print('AZURE2 did not execute properly.')
            raise

        try:
            if dress_up:
                output = [Output(output_dir + '/' + of) for of in
                          self.output_filenames]
            else:
                output = [np.loadtxt(output_dir + '/' + of) for of in
                          self.output_filenames]

            if full_output:
                output = (output, utility.read_rwas_jpi(output_dir))

            shutil.rmtree(output_dir)
            shutil.rmtree(data_dir)
            os.remove(input_filename)

            return output
        except:
            shutil.rmtree(output_dir)
            shutil.rmtree(data_dir)
            os.remove(input_filename)
            print('Output files were not properly read.')
            print('AZURE output:')
            print(response)
            raise


    def extrapolate(self, theta, segment_indices=None, use_brune=None,
                    use_gsl=None, ext_capture_file=None):
        '''
        See predict() documentation.
        '''
        workspace = self.config.generate_workspace_extrap(theta,
            segment_indices=segment_indices)
        input_filename, output_dir, output_files = workspace

        try:
            response = utility.run_AZURE2(input_filename, choice=3,
                use_brune=use_brune if use_brune is not None else self.use_brune,
                use_gsl=use_gsl if use_gsl is not None else self.use_gsl,
                ext_par_file=self.ext_par_file,
                ext_capture_file=(ext_capture_file if ext_capture_file is not
                    None else self.ext_capture_file_extrap),
                command=self.command)
        except:
            shutil.rmtree(output_dir)
            os.remove(input_filename)
            print('AZURE2 did not execute properly.')
            raise

        try:
            output = [np.loadtxt(output_dir + '/' + of) for of in output_files]
            shutil.rmtree(output_dir)
            os.remove(input_filename)
            return output
        except:
            shutil.rmtree(output_dir)
            os.remove(input_filename)
            print('Output files could not be read.')
            raise


    def rwas(self, theta):
        '''
        Returns the reduced width amplitudes (rwas) and their corresponding J^pi
        at the point in parameter space, theta.
        '''
        input_filename, output_dir = utility.random_output_dir_filename()
        new_levels = self.config.generate_levels(theta)
        utility.write_input_file(self.config.input_file_contents, new_levels,
                                 input_filename, output_dir)
        response = utility.run_AZURE2(input_filename, choice=1,
            use_brune=self.use_brune, ext_par_file=self.ext_par_file,
            ext_capture_file=self.ext_capture_file, use_gsl=self.use_gsl,
            command=self.command)

        rwas = utility.read_rwas_jpi(output_dir)

        shutil.rmtree(output_dir)
        os.remove(input_filename)

        return rwas

    
    def ext_capture_integrals(self, use_gsl=False, mod_data=False):
        '''
        Returns the AZURE2 output of external capture integrals.
        '''
        input_filename, output_dir, data_dir = utility.random_workspace()

        if mod_data:
            self.config.update_data_directories(data_dir)

        new_levels = self.config.initial_levels.copy()
        new_levels = [l for sl in new_levels for l in sl]
        utility.write_input_file(self.config.input_file_contents, new_levels,
                                 input_filename, output_dir)
        response = utility.run_AZURE2(input_filename, choice=1,
            use_brune=self.use_brune, ext_par_file=self.ext_par_file,
            ext_capture_file='\n', use_gsl=use_gsl,
            command=self.command)

        ec = utility.read_ext_capture_file(output_dir + '/intEC.dat')

        shutil.rmtree(output_dir)
        shutil.rmtree(data_dir)
        os.remove(input_filename)

        return ec

    
    def update_ext_capture_integrals(self, segment_indices, shifts, use_gsl=False):
        '''
        Takes:
          * a list of indices to identification which data segment is being
            shifted
          * a list of shifts to be applied (in the same order as the indices are
            provided)
        * Adjusts the energies of data segments (identified by index) by the
        provided shifts (MeV, lab).
        * Evaluates the external capture (EC) integrals.
        * Returns the values from the EC file.
        '''
        for (i, shift) in zip(segment_indices, shifts):
            self.config.data.segments[i].shift_energies(shift)

        return self.ext_capture_integrals(use_gsl=use_gsl, mod_data=True)
