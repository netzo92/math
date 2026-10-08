# Zcash-relevant algorithmic complexity

## Objective

Look for mathematically meaningful complexity improvements or failures in algorithms and assumptions that matter to ZEC, including shielded transactions. This is **algorithm research**, not an inspection of anyone's wallet. No keys, addresses, balances, or transactions are needed. The goal is to identify a precise problem, establish the best relevant baseline, and test a proposed improvement with reproducible evidence.

Two directions are distinct:

- **Attack complexity:** Can a mathematical attack on an assumption used by Zcash require asymptotically fewer operations, less memory, or a materially smaller concrete cost than established attacks?
- **Defender complexity:** Can Zcash-related proving, verification, or wallet algorithms do less work while preserving the same statement and security properties?

An improvement to proof generation is useful performance work. It is not, by itself, a break in funds security. Conversely, a toy attack does not show a production curve is vulnerable.

## First attack target: elliptic-curve discrete logarithm

The [Halo 2 Book](https://zcash.github.io/halo2/background/curves.html) describes the elliptic-curve discrete-log assumption; the [Orchard Book](https://zcash.github.io/orchard/design/keys.html) describes Orchard's Pallas keys. For a prime-order group of size q, generic exhaustive search takes work proportional to q. Baby-step/giant-step and Pollard rho provide square-root-scale generic baselines with different memory needs. [Shoup's lower-bound paper](https://www.shoup.net/papers/dlbounds1.pdf) explains why beating square-root work in the **generic group model** requires a different kind of idea. That model does not prove a lower bound for every specific curve.

**Research question:** Is there exploitable non-generic structure in a precisely named Zcash-relevant group, or a new time/memory/parallelism trade-off, that changes the attack cost under a stated model? Separate a genuine asymptotic result from a constant-factor improvement. Check every purported discrete log by scalar multiplication.

### Bounded baseline, completed

`experiments/toy_ecdlp.py` implements exhaustive search, baby-step/giant-step, and a deterministic-restart Pollard-rho variant over deliberately tiny elliptic-curve subgroups. It rejects fields larger than 1000 and accepts no real wallet or production-curve input. Every secret in the q=199 sample subgroup is recovered by all three algorithms in the tests. The command sweeps **every** target in each group and reports the median group-addition count; rho also reports its 95th-percentile count.

| Toy field p | Group order q | Exhaustive median adds | BSGS median adds / stored points | Rho median / p95 adds |
| ---: | ---: | ---: | ---: | ---: |
| 223 | 7 | 3 | 4 / 3 | 10 / 22 |
| 307 | 109 | 54 | 15 / 11 | 43 / 94 |
| 211 | 199 | 99 | 21 / 15 | 58 / 109 |

These tiny observations confirm correctness and expose time/memory trade-offs. They are not production security estimates. At these sizes, rho's overhead and restarts can outweigh its memory advantage.

**Second loop:** [the Pasta-like endomorphism experiment](004-pasta-endomorphism.md) checks a structural hypothesis on tiny public curves. Its six-point automorphism classes give an idealized constant-factor search-space discount, but this is known prior art and already reflected in published Vesta attack-cost estimates. The next loop must look for a distinct, precisely specified property or switch to a named defender-side cost question. Do not extrapolate from a small q to a production key size.

## Other complexity targets from the top-five list

1. **Halo 2 prover/verifier algorithms:** count field operations, multi-scalar multiplication work, memory, and proof size for a named subroutine. Compare with a verified implementation. [Halo 2 protocol](https://zcash.github.io/halo2/design/protocol.html).
2. **Pallas/Vesta arithmetic:** compare complete formulas and coordinate systems under identical input and constant-time requirements; count field multiplications *and* inversions, squarings, memory, and special cases. [Orchard keys](https://zcash.github.io/orchard/design/keys.html).
3. **Scalar multiplication:** compare fixed-base and variable-base algorithms, precomputation and memory, and the exact domain for a named Zcash call site. [Halo 2 fixed-base gadget](https://zcash.github.io/halo2/design/gadgets/ecc/fixed-base-scalar-mul.html).
4. **Post-quantum signatures:** compare signature size, signing and verification work, and lifetime/use constraints under an explicit security target. [NIST FIPS 205](https://csrc.nist.gov/pubs/fips/205/final) is one standard baseline; no protocol switch is implied.

## Evidence levels

- **Toy observation:** correct for the stated small inputs and model only.
- **Asymptotic argument:** proves a complexity claim under explicitly stated assumptions.
- **Protocol-relevant implementation result:** matches a current Zcash specification and code path, with independent correctness checks and reproducible costs.
- **Security finding:** demonstrates a concrete violation of a stated security property under real protocol conditions. This requires independent review and responsible disclosure before publication.

**Current conclusion:** No new attack or production-curve weakness has been found. The completed work includes a tested generic baseline and a tested toy endomorphism check. The latter reproduces known structure; the next goal is a distinct hypothesis that could beat an already-accounted-for baseline or improve a defender algorithm without weakening it.
