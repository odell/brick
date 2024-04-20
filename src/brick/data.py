'''
Classes to hold Data segments as found in .azr files.
'''

import numpy as np
from . import utility
from .parameter import NormFactor
from .constants import *

class Segment:
    '''
    Structure to organize the information contained in a line in the
    <segmentsData> section of an AZURE2 input file.
    '''
    def __init__(self, row, index):
        self.row = row.split()
        self.index = index
        self.include = (int(self.row[INCLUDE_INDEX]) == 1)
        self.in_channel = int(self.row[IN_CHANNEL_INDEX])
        self.out_channel = int(self.row[OUT_CHANNEL_INDEX])
        self.reaction_type = int(self.row[REACTION_TYPE])

        if self.reaction_type == 2:
            self.norm_factor = float(self.row[NORM_FACTOR_INDEX + 2])
            self.vary_norm_factor = int(self.row[VARY_NORM_FACTOR_INDEX + 2])
            self.filepath = self.row[FILEPATH_INDEX + 2]
        else:
            self.norm_factor = float(self.row[NORM_FACTOR_INDEX])
            self.vary_norm_factor = int(self.row[VARY_NORM_FACTOR_INDEX])
            self.filepath = self.row[FILEPATH_INDEX]

        i = self.filepath.rfind('/')
        self.filename = self.filepath[i+1:]

        if self.vary_norm_factor:
            self.nf = NormFactor(self.index)
        else:
            self.nf = None
        
        self.values_original = np.loadtxt(self.filepath)
        self.values = np.copy(self.values_original)
        self.n = self.values.shape[0] if self.values.ndim > 1 else 1

        if self.out_channel != -1:
            self.output_filename = f'AZUREOut_aa={self.in_channel}_R={self.out_channel}.out'
        else:
            self.output_filename = f'AZUREOut_aa={self.in_channel}_TOTAL_CAPTURE.out'

   
    def string(self):
        '''
        Returns a string of the text in the segment line.
        '''
        row = self.row.copy()
        # Are these lines...
        # row[INCLUDE_INDEX] = '1' if self.include else '0'
        # row[IN_CHANNEL_INDEX] = str(self.in_channel)
        # row[OUT_CHANNEL_INDEX] = str(self.out_channel)
        if self.reaction_type == 2:
            row[FILEPATH_INDEX + 2] = str(self.filepath)
            row[NORM_FACTOR_INDEX + 2] = str(self.norm_factor)
        else:
            row[FILEPATH_INDEX] = str(self.filepath)
            row[NORM_FACTOR_INDEX] = str(self.norm_factor)
        # necessary?
        
        return ' '.join(row)


    def print(self):
        '''
        Prints description of the data segment.
        '''
        print(self.string())


    def update_dir(self, new_dir, values=None):
        '''
        Updates the path directory of the segment.
        If modifications are made to the data, the modified data is written to
        an ephemeral directory so that multiple processes can do so
        simultaneously.
        '''
        filepath = new_dir + '/' + self.filename
        if values is not None:
            np.savetxt(filepath, values)
        else:
            np.savetxt(filepath, self.values)


    def shift_energies(self, shift):
        values = np.copy(self.values_original)
        values[:, 0] += shift
        return values


class Data:
    '''
    Structure to hold all of the data segments in a provided AZURE2 input file.
    '''
    def __init__(self, filename):
        self.contents = utility.read_input_file(filename)
        i = self.contents.index('<segmentsData>')+1
        j = self.contents.index('</segmentsData>')

        # All segments listed in the file.
        self.segments = []
        k = 0
        for row in self.contents[i:j]:
            if row != '':
                row_list = row.split()
                include = (int(row_list[INCLUDE_INDEX]) == 1)
                if include:
                    self.segments.append(Segment(row, k))
                k += 1

        # Indices of segments with varied normalization constants.
        self.norm_segment_indices = []
        for (i, seg) in enumerate(self.segments):
            if seg.include and seg.vary_norm_factor:
                self.norm_segment_indices.append(i)

        # Number of data points for each included segment.
        self.ns = [seg.n for seg in self.segments] 

        # Output files that need to be read.
        self.output_files = []
        for seg in self.segments:
            self.output_files.append(seg.output_filename)
        # Eliminates repeated output files AND SORTS them:
        # (1, 2, 3, ..., TOTAL_CAPTURE)
        self.output_files = list(np.unique(self.output_files))


    def update_all_dir(self, new_dir, contents):
        '''
        Updates all the path directories of the segments.
        '''
        start = contents.index('<segmentsData>')+1
        stop = contents.index('</segmentsData>')

        new_contents = contents.copy()

        for i in range(start, stop):
            row = contents[i].split()
            old_path = row[FILEPATH_INDEX]
            j = old_path.rfind('/') + 1
            row[FILEPATH_INDEX] = new_dir + '/' + old_path[j:]
            new_contents[i] = ' '.join(row)
        
        for seg in self.segments:
            seg.update_dir(new_dir)

        return new_contents



    def write_segments(self, contents):
        '''
        Writes the segments to contents.
        "contents" is a representation of the .azr file (list of strings)
        This is typically done in preparation for writing a new .azr file.
        '''
        start = contents.index('<segmentsData>')+1
        stop = contents.index('</segmentsData>')

        for segment in self.segments:
            contents[start+segment.index] = segment.string()

        return contents


    def update_norm_factors(self, theta_norm, contents):
        assert len(theta_norm) == len(self.norm_segment_indices), '''
Number of normalization factors does not match the number of data segments
indicating the normalization factor should be varied.
'''
        for (f, i) in zip(theta_norm, self.norm_segment_indices):
            self.segments[i].norm_factor = f

        self.write_segments(contents)
        
        return contents
