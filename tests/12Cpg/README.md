# Tests

Basic functionality tests are written in `tests.py`. To run them, use

```
python -m unittests -v tests.py
```

Currently, there are three tests that compare outputs to assure that

1. BRICK and AZURE2 generate the same output with the same input values
   (`test_output`)
2. normalization factors are written to the input file correctly
   (`test_norm_factors`)
3. energy shifts are applied to the data correctly (`test_energy_shift`)
