# Zcash cryptography questions

## Question A: Orchard commitment-tree witness updates

Orchard uses a fixed-depth 32 commitment tree, appends commitments in block order, and instantiates its Merkle hash with Sinsemilla. [Orchard Book: commitment tree](https://zcash.github.io/orchard/design/commitment-tree.html).

How much work is needed to update many witnesses as new commitments arrive? Compare a simple recomputation baseline with a batched incremental method. State whether the result is for a toy tree or a protocol-faithful implementation. Do not call a generic hash an Orchard Merkle hash.

## Question B: finite-field polynomial evaluation

Halo 2 circuits involve polynomial representations and commitments. [Halo 2 Book: circuit commitments](https://zcash.github.io/halo2/design/proving-system/circuit-commitments.html). The accompanying `experiments/polynomial_eval.py` compares naive evaluation and Horner's rule over the **toy field F_97**. It demonstrates arithmetic-operation savings; it neither implements Halo 2 nor uses Zcash's production field parameters.

## Next loop

- Prove Horner's recurrence and exact operation count.
- Measure field multiplication cost independently of Python loop overhead.
- Choose a specific protocol subroutine, confirm its current specification and implementation, then state an optimization hypothesis with correctness tests.
