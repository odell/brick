'''
Utility functions stored here to keep other class definitions uncluttered.
'''

import string
import random
import os
from subprocess import Popen, PIPE
import numpy as np
from .level import Level

'''
The rows of levels in the .azr file are converted to list of strings. These
indices make it more convenient to access the desired parameter.
'''
J_INDEX = 0
PI_INDEX = 1
ENERGY_INDEX = 2
ENERGY_FIXED_INDEX = 3
CHANNEL_INDEX = 5
WIDTH_INDEX = 11
WIDTH_FIXED_INDEX = 10
SEPARATION_ENERGY_INDEX = 21
CHANNEL_RADIUS_INDEX = 27
OUTPUT_DIR_INDEX = 2
DATA_FILEPATH_INDEX = 11

def read_input_file(filename):
    '''
    Reads AZURE2 input file (.azr file) – purely for convenience.
    Takes a filename (str).
    Returns a list of strings.
    '''
    with open(filename, 'r') as f:
        contents = f.read().split('\n')
    return contents


def read_level_contents(infile):
    '''
    Reads rows between <levels> and </levels>.
    '''
    contents = read_input_file(infile)
    start = contents.index('<levels>')+1
    stop = contents.index('</levels>')
    return contents[start:stop]


def read_levels(infile):
    '''
    Packages the contents of the input file (infile, str) into instances of
    Level.
    Takes an input filename (str).
    Returns a list of Level instances.
    '''
    level_contents = read_level_contents(infile)

    levels = []
    sublevels = []
    for row in level_contents:
        if row != '':
            row = row.split()
            spin = float(row[J_INDEX])
            parity = int(row[PI_INDEX])
            energy = float(row[ENERGY_INDEX])
            energy_fixed = int(row[ENERGY_FIXED_INDEX])
            width = float(row[WIDTH_INDEX])
            width_fixed = int(int(row[WIDTH_FIXED_INDEX]) or width == 0)
            radius = float(row[CHANNEL_RADIUS_INDEX])
            channel = int(row[CHANNEL_INDEX])
            separation_energy = float(row[SEPARATION_ENERGY_INDEX])
            sublevels.append(Level(spin, parity, energy, energy_fixed, width,
                                   width_fixed, radius, channel,
                                   separation_energy))
        else:
            levels.append(sublevels)
            sublevels = []

    return levels


LETTERS = string.ascii_lowercase
NUMBERS = ''.join(map(str, range(10)))
CHARACTERS = LETTERS+NUMBERS


def random_string(length=8):
    return ''.join(random.choice(CHARACTERS) for i in range(length))


def random_output_dir_filename():
    s = 'mcazure_' + random_string()
    output_dir = 'output_' + s
    os.mkdir(output_dir)
    input_filename = s + '.azr'
    return input_filename, output_dir


def random_workspace(prepend=''):
    s = 'mcazure_' + random_string()
    output_dir = prepend + 'output_' + s
    data_dir = prepend + 'data_' + s
    os.mkdir(output_dir)
    os.mkdir(data_dir)
    input_filename = prepend + s + '.azr'
    return input_filename, output_dir, data_dir


def update_segmentsData_dir(contents0, data_dir):
    contents = contents0.copy()
    start = contents0.index('<segmentsData>')+1
    stop = contents0.index('</segmentsData>')

    for i in range(start, stop):
        row = contents[i].split()
        row[11] = row[11].replace('data', data_dir)
        contents[i] = ' '.join(row)
    
    return contents


def write_input_file(old_input_file_contents, new_levels, input_filename,
    output_dir, data_dir=None):
    '''
        Takes:
            * contents of an old .azr file (see read_input_file function)
            * list of new Levels
        Does:
            * replaces the level parameters of the old .azr files with the
              parameters of the new levels
            * generates a random filename
            * writes the new level parameters (along with everything else in the
              old .azr file) to the random filename
            * returns random filename
    '''
    start = old_input_file_contents.index('<levels>')+1
    stop = old_input_file_contents.index('</levels>')
    old_levels = old_input_file_contents[start:stop]
    nlines = len(old_levels)
    level_indices = [i for (i, line) in enumerate(old_levels) if line != '']
    nlevels = len(level_indices)
    blank_indices = [i for i in range(nlines) if i not in level_indices]
    assert (nlevels == len(new_levels)), '''
The number of levels passed in does not match the number of existing levels.'''

    # Replace the old level parameters with the new parameters.
    new_level_data = []
    j = 0
    for i in range(nlines):
        if i in blank_indices:
            new_level_data.append('')
        else:
            level = new_levels[j]
            nlevel = old_levels[i].split()
            nlevel[J_INDEX] = str(level.spin)
            nlevel[PI_INDEX] = str(level.parity)
            nlevel[ENERGY_INDEX] = str(level.energy)
            nlevel[WIDTH_INDEX] = str(level.width)
            nlevel[CHANNEL_RADIUS_INDEX] = str(level.channel_radius)
            new_level_data.append(str.join('  ', nlevel))
            j += 1

    # If the data directory is specified, then we'll update it.
    if data_dir is not None:
        old_input_file_contents = update_segmentsData_dir(old_input_file_contents, data_dir)

    # Write the new parameters to the same input file.
    with open(input_filename, 'w') as f:
        f.write(old_input_file_contents[0]+'\n')
        f.write(old_input_file_contents[1]+'\n')
        f.write(output_dir+'/\n')
        for row in old_input_file_contents[OUTPUT_DIR_INDEX+1:start]:
            f.write(row+'\n')
        for row in new_level_data:
            f.write(row+'\n')
        f.write('</levels>\n')
        for row in old_input_file_contents[stop+1:]:
            f.write(row+'\n')


def read_rwas_alt(output_dir):
    with open(output_dir + '/parameters.out', 'r') as f:
        pars = f.read().split('\n')
    rwas = []
    for row in pars:
        if row.find('g_int') >= 0:
            elements = row.split()
            ii = elements.index('g_int')
            rwas.append(float(elements[ii+2]))
    return rwas


def read_rwas_jpi(output_dir):
    with open(output_dir + '/parameters.out', 'r') as f:
        pars = f.read().split('\n')
    rwas = []
    for row in pars:
        if row.find('J =') == 0:
            Jpi = row.split()[2]
        if row.find('g_int') >= 0:
            elements = row.split()
            ii = elements.index('g_int')
            channel = int(elements[2])
            rwas.append([Jpi, channel, float(elements[ii+2])])
    return rwas


def read_ext_capture_file(filename):
    ext_capture_data = []
    with open(filename, 'r') as f:
        for line in f:
            i = line.find('(')
            j = line.find(',')
            k = line.find(')')
            x = float(line[i+1:j])
            y = float(line[j+1:k])
            ext_capture_data.append([x, y])
    return np.array(ext_capture_data)


def write_ext_capture_file(filename, data):
    '''
    data is expected to be 2-column matrix
    '''
    with open(filename, 'w') as f:
        for row in data:
            x, y = row
            f.write(f'({x:.5e},{y:.5e})\n')
        
    
def run_AZURE2(input_filename, choice=1, use_brune=False, ext_par_file='\n',
        ext_capture_file='\n', use_gsl=False, command='AZURE2'):
    cl_args = [command, input_filename, '--no-gui', '--no-readline']
    if use_brune:
        cl_args += ['--use-brune']
    if use_gsl:
        cl_args += ['--gsl-coul']
    p = Popen(cl_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    options = str(choice) + '\n' + ext_par_file + ext_capture_file
    response = p.communicate(options.encode('utf-8'))
    return (response[0].decode('utf-8'), response[1].decode('utf-8'))
