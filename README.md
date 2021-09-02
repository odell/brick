# BRICK

**B**ayesian **R**-Matrix **I**nference **C**ode **K**it

BRICK is a Python package that serves as an interface to AZURE2 and readily
permits the sampling of R-matrix parameters.

It _accompanies_ AZURE2. The **primary** goal is to allow the user to deploy
Markov Chain Monte Carlo (MCMC) to sample parameters that are typically
optimized in a &chi;<sup>2</sup>-minimization analysis.

## Requirements

[AZURE2](https://azure.nd.edu) must be installed and available at the command
line via `AZURE2`. Currently, command-line execution is not available on Windows
or macOS.

[NumPy](https://numpy.org) and [Matplotlib](https://matplotlib.org/) must be
available in order to run the test script in `test` directory.

[emcee](https://pypi.org/project/emcee/) is the MCMC sampler that is used in the
test scripts. BRICK is intentionally designed such that other samplers can be
used with little effort.

## Overview

The classes defined in this module are:

1. AZR
2. Parameter
3. Level
4. Output
5. Segment
6. Data

### AZR

Handles communication with AZURE2 and its output.

### Parameter

Defines a sampled or "free" parameter.

### Level

Defines an R-matrix level (a line in the `<levels>` section of the .azr file).

### Output

Data structure for accessing output data. (I got tired of consulting the
extremely well-documented manual for the output file format.)

### Segment

Data structure to organize the information contained in line of the
`<segmentsData>` section of the .azr file.

### Data

Data structure that holds a list of Segments and provides some convenient
functions for applying actions to all of them.

## Example

In the `test` directory there is a Python script (`test.py`) that predicts the
12C(p,gamma) cross section and compares it to the Vogl data.

Note that the script uses NumPy and Matplotlib.

## Installation

The simplest way to install `brick` is to use `pip` via:

```
pip install brick-james
```

Alternatively, one may clone the repository on
[GitHub](https://github.com/odell/brick).

## Tests

BRICK includes a suite of basic funcationality tests in the `tests/12Cpg`
directory. The tests perform calculations of the 12C(p,gamma) reaction with two
data sets. To run them, within the `tests/12Cpg` directory, use

```
python -m unittests -v tests.py
```


## Use

Once installed, `brick` allows the user to access the relevant classes and
functions by:

```
import brick

azr_object = brick.azr.AZR('input.azr')
```

More instructive test are forthcoming.
