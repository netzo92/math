# When does Strassen multiplication help?

## Question

Classical square matrix multiplication uses n³ scalar multiplications. Strassen uses seven half-size products per recursion instead of eight. At what size, in which language and for which integer range, does the recursive method actually get faster?

## Result so far

The seven-product identity is checked against classical multiplication over random signed integer matrices for small powers of two. The accompanying program counts scalar multiplications and additions and reports median local wall-clock times. It makes no claim about all matrix sizes or hardware.

## Next loop

- Add a classical cutoff at size k. Measure k on the same machine.
- Handle odd dimensions by padding, then compare allocated memory as well as time.
- Separate arithmetic-operation complexity from cache and allocation costs.
- Prove the seven-product identity symbolically, then derive its recurrence.

## Reproduce

`python3 experiments/matrix_multiply.py`
