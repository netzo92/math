# My top 5 problems

These are the owner's research priorities, in the order supplied. They are questions to investigate, not claims that a cryptographic assumption has failed or that an optimization is safe for Zcash. Each project needs a precise model, a baseline, an independently checked result, and a note describing what remains unproved.

| Rank | Problem | What to optimize | Zcash relevance |
| --- | --- | --- | --- |
| 1 | Elliptic-curve discrete logarithms | Attack complexity | Fundamental security assumptions |
| 2 | Halo 2 proof optimization | Constraint count / prover time | Faster shielded transactions |
| 3 | Pallas/Vesta curve arithmetic | Field multiplications per operation | Orchard performance |
| 4 | Elliptic-curve scalar multiplication | Operation count | Wallet and proof performance |
| 5 | Hash-based post-quantum signatures | Signature size / verification cost | Future quantum resistance |

## 1. Elliptic-curve discrete logarithms

**First question:** For explicitly chosen toy prime-order curves, how do generic attack time and memory scale with group order? State the threat model and compare measured work with the known algorithms before drawing any broader conclusion. Do not infer anything about production curve security from small examples. The [Halo 2 Book's elliptic-curve background](https://zcash.github.io/halo2/background/curves.html) describes the discrete-log assumption used in this area.

**Next loop:** Define the toy groups and operation counter; implement exhaustive search and a second generic algorithm; check every recovered logarithm; report time and memory separately.

## 2. Halo 2 proof optimization

**First question:** For one named Halo 2 gadget, can an equivalent constraint formulation use fewer rows or reduce prover time without changing the statement being proved? Fix a baseline implementation, tests, and benchmark environment. Halo 2 uses polynomial constraints and has distinct circuit and proof-system costs; see the [Halo 2 concepts](https://zcash.github.io/halo2/concepts/proofs.html) and [circuit commitments](https://zcash.github.io/halo2/design/proving-system/circuit-commitments.html).

**Next loop:** Select an existing gadget and record row count, proof generation time, peak memory, and verification behavior before proposing a change.

## 3. Pallas/Vesta curve arithmetic

**First question:** Which field multiplications, squarings, inversions, and allocations dominate one chosen point operation? Compare formulas only under the same coordinate model and constant-time requirements. Orchard keys use **Pallas**, while Halo 2 proofs are computed on **Vesta**; the curves have different roles. See the [Orchard Book on keys](https://zcash.github.io/orchard/design/keys.html).

**Next loop:** Choose a point-addition or doubling path in a current implementation, count operations, and verify candidate formulas against identity, inverse, doubling, and random points.

## 4. Elliptic-curve scalar multiplication

**First question:** For a specific fixed-base or variable-base scalar multiplication use, can we reduce the total point operations and measured latency while retaining the same scalar domain and side-channel behavior? This differs from #3: it studies the higher-level sequence of point operations rather than one field-level operation. The [Halo 2 fixed-base gadget](https://zcash.github.io/halo2/design/gadgets/ecc/fixed-base-scalar-mul.html) gives a concrete starting point.

**Next loop:** Compare a reference method with one windowing strategy on a toy group, then identify the production call site and its exact correctness requirements.

## 5. Hash-based post-quantum signatures

**First question:** For a stated signing use and security target, what trade-off do current hash-based signature parameter sets make among signature bytes, verification work, signing cost, and limits on use? A wallet or protocol integration question comes only after these measurements. [NIST FIPS 205](https://csrc.nist.gov/pubs/fips/205/final) standardizes SLH-DSA; this is a reference point, not a claim that Zcash currently uses it.

**Next loop:** Create a comparison table from the standard and a maintained implementation; measure encoded size and verification time for a fixed workload.

## Working rule

Keep toy experiments, protocol facts, and performance proposals in separate sections of every result. A faster experiment is not yet a secure protocol change. Cite the exact version of any specification and implementation being evaluated.
