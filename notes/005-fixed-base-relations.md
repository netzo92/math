# Fixed-base relations: a generic birthday baseline

## Question and scope

Does giving a simple generic relation finder more public elliptic-curve bases make it find a useful relation in fewer sampled combinations? This iteration tests that **specific algorithm**, not all multi-target attacks. The inputs are synthetic prime-order toy subgroups with `q=199` or `229`; no deployed point, key, wallet, or transaction is used.

The [Halo 2 Book](https://zcash.github.io/halo2/design/gadgets/ecc/fixed-base-scalar-mul.html) names six fixed bases used in Orchard's circuit. Their **roles and required security relations differ**; treating all six as freely interchangeable targets would be an unjustified protocol claim. [Orchard commitments](https://zcash.github.io/orchard/design/commitments.html) are binding under discrete-log assumptions. The [Ironwood security-model discussion](https://zcash.github.io/ironwood/formal-verification/security-models.html#fixed-bases-the-group-hash-and-the-reference-string) explains why a relation among the appropriate fixed bases matters, and why lifetime precomputation against deployed bases is a recognized limitation. It does not say that a toy relation breaks Orchard.

## Model and derivation

Let `G` generate a group of prime order `q`; let `B₁=G, B₂,…,Bₘ` be distinct public points in that group. For each trial, sample an independent uniform coefficient vector `a∈(Z/qZ)^m`, compute `P(a)=ΣaᵢBᵢ`, and store `(P(a),a)`. A collision `P(a)=P(b)` with `a≠b` yields the independently verifiable nonzero relation `Σ(aᵢ−bᵢ)Bᵢ=0`. For `m=2`, any nonzero relation has a nonzero coefficient on `B₂` and reveals its discrete log relative to `G`. For `m>2`, a valid relation is **not automatically an exploitable relation for every Orchard component**.

Because `B₁=G` and its coefficient is uniform, each sampled point is exactly uniform in the group, regardless of `m`. Independent draws give the exact point-collision probability

`Pr[no point collision in t draws] = ∏_{j=0}^{t−1}(1−j/q)` (for `t≤q`).

Thus this algorithm has a square-root birthday scale in `q` independent of the number of bases. A repeated *coefficient vector* gives a trivial relation; the code ignores it, so the formula describes point collisions rather than exact time to a **nontrivial** relation. This derivation does **not** rule out better multi-target algorithms, representation-specific attacks, or preprocessing trade-offs. In fact, [Corrigan-Gibbs and Kogan](https://eprint.iacr.org/2017/1113) study generic discrete logarithms with preprocessing, including multiple-log variants. Their results need their own cost model before application here.

## Reproduce and result

From the repo root run `python3 -m experiments.toy_fixed_bases` and `python3 -m unittest discover -s tests`. Python 3.11+; no dependencies. Each row below uses 64 deterministic trials. The script reports median sampled combinations and exact calls to the toy curve's group-addition method during search. It excludes base generation, verification, hash-table cost, memory allocation, and elapsed time. The independent tests verify every returned relation and recover `log_G(B₂)` for all two-base cases they run. The code stores one coefficient vector per distinct point, so memory grows with the samples.

| Toy subgroup order q | Bases m | Median samples | Median group additions |
| ---: | ---: | ---: | ---: |
| 229 | 2 | 17 | 377 |
| 229 | 6 | 20 | 1263.5 |
| 199 | 2 | 19 | 393.5 |
| 199 | 6 | 17 | 1049 |

Sampling medians vary between seeds, consistent with the derivation's lack of an `m` advantage for this algorithm. The six-base search uses more additions because it computes six scalar multiples per fresh random combination. This is a deliberately simple, memory-heavy baseline; these counts must **not** be compared directly with optimized Pollard rho costs or extrapolated to Pallas/Vesta. No production security weakness or novel attack was found.

## Comparable baselines and what is still missing

The table below uses `q` for subgroup order, `m` for number of bases, and counts group operations at the asymptotic level. It separates online work from stored group points; constants, field-operation cost, memory bandwidth, and parallelism are omitted.

| Problem / method | Online group work | Stored points | Prior work and applicability |
| --- | --- | --- | --- |
| One named two-base log, baby-step/giant-step | `Θ(√q)` | `Θ(√q)` | Textbook generic time/memory benchmark; no group-specific setup. |
| One named two-base log, Pollard rho | Expected `Θ(√q)` | `O(1)` for cycle detection | Generic attack benchmark; known Pasta automorphisms change the concrete constant ([previous lab](004-pasta-endomorphism.md)). |
| Any relation among `m` bases, this fresh-combination birthday search | `Θ(m log q √q)` with naive binary scalar multiplication | `Θ(√q)` | The exact uniform-sample collision law above; the measured implementation counts its actual additions. Precomputed multi-scalar tables could change the per-sample factor and must be charged. |
| Recover **all** `n` independent logs, published multiple-DL problem | `Θ(√(nq))` generic group work in the regime studied | Algorithm-dependent | [Yun, EUROCRYPT 2015](https://www.iacr.org/archive/eurocrypt2015/90560113/90560113.pdf) gives a tight generic bound for solving **all** logs. It is a different success condition from finding **any one** relation; it cannot be read as a `√n` discount on one Orchard relation. |
| Generic discrete log with group preprocessing | A trade-off between stored advice `S` and online time `T` | `S` **bits** of advice | [Corrigan-Gibbs–Kogan](https://eprint.iacr.org/2017/1113) prove `S·T² = Ω̃(εq)` for success probability `ε` in their model and discuss multiple-log variants. This is a bound in a **different experiment**, not an achieved cost for Orchard's fixed `V,R` relation. |

[Shoup's generic-group lower-bound work](https://www.shoup.net/papers/dlbounds1.pdf) supplies the context for square-root generic attacks. The essential missing comparison is **end-to-end, including offline operations**, for a candidate that actually benefits from multiple protocol bases or repeated targets. The table does not imply that six bases are as hard as two under every attack or that any theoretical relation is a valid transaction attack.

## Remaining uncertainty and next question

The important question is whether a **named, protocol-relevant relation** can be found more cheaply when the attacker's precomputation, stored advice, online work, target count, and elapsed protocol lifetime are all charged. Next, select one exact Orchard relation (for example, the value-commitment `V,R` pair), review published preprocessing and multi-target algorithms in their native cost models, and produce a side-by-side bound. Only then build a toy implementation of the most relevant candidate. Do not conflate a relation among arbitrary points with a valid commitment collision or transaction forgery.
