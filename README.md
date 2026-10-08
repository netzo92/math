# Math

An open lab for algorithmic complexity and Zcash-related cryptography questions. Each iteration should leave behind a reproducible experiment, a careful claim, and a next question.

## Zcash-relevant complexity

[Attack and defender complexity research](notes/003-zcash-relevant-complexity.md) guides the work for ZEC, including shielded transactions. The first lab compares three generic elliptic-curve discrete-log attacks on tiny public groups. [The second lab](notes/004-pasta-endomorphism.md) checks a known Pasta-like endomorphism on tiny curves and explains why it is already included in published attack-cost estimates. These are baselines for new complexity ideas, not an assessment of any wallet.

## Priorities

[My top 5 problems](notes/priorities.md) sets the research order: elliptic-curve discrete logarithms, Halo 2 proof optimization, Pallas/Vesta curve arithmetic, elliptic-curve scalar multiplication, and hash-based post-quantum signatures. Each has a first measurable question and a next loop.

## Tracks

- [Matrix multiplication](notes/001-matrix-multiplication.md): classical versus Strassen, operation counts versus measured time.
- [Zcash cryptography](notes/002-zcash-cryptography.md): Orchard commitment-tree witnesses and a toy finite-field polynomial experiment motivated by Halo 2.

The toy examples are **not** production Zcash cryptography or claims about protocol security.

## Loop

1. Copy [the note template](notes/template.md). Define the question and assumptions.
2. Work a tiny example and hunt for counterexamples.
3. Make a runnable experiment in `experiments/`; pin random seeds and report the machine for benchmarks.
4. Separate proof from measurement. Record whether the conclusion is proved, disproved, or still open.
5. End with one concrete next step.

## Run

Python 3.11+; no third-party dependencies.

```sh
python3 -m unittest discover -s tests
python3 experiments/matrix_multiply.py
python3 experiments/polynomial_eval.py
python3 experiments/toy_ecdlp.py
python3 -m experiments.toy_endomorphism
```

Start with the matrix multiplication cutoff question or propose a new problem in either track.
