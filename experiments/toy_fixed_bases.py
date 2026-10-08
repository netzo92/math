"""Generic relation finding among tiny public fixed elliptic-curve bases.

Only ToyCurve fields <= 1000 are accepted. No deployed points or keys are used.
This implements a simple random-combination birthday search, not an optimized
multi-target discrete-log attack or a Zcash protocol break.
"""
from __future__ import annotations

from random import Random
from statistics import median

from experiments.toy_ecdlp import Point, ToyCurve, prime_order_generator


def counted_mul(curve: ToyCurve, scalar: int, point: Point) -> tuple[Point, int]:
    """Binary scalar multiplication; count calls to group addition."""
    if scalar < 0:
        raise ValueError("Expected a nonnegative scalar")
    result: Point = None
    additions = 0
    while scalar:
        if scalar & 1:
            result = curve.add(result, point)
            additions += 1
        scalar >>= 1
        if scalar:
            point = curve.add(point, point)
            additions += 1
    return result, additions


def combination(curve: ToyCurve, bases: tuple[Point, ...], coefficients: tuple[int, ...]) -> tuple[Point, int]:
    if len(bases) != len(coefficients):
        raise ValueError("Each base needs a coefficient")
    total: Point = None
    additions = 0
    for base, coefficient in zip(bases, coefficients):
        term, cost = counted_mul(curve, coefficient, base)
        total = curve.add(total, term)
        additions += cost + 1
    return total, additions


def find_relation(curve: ToyCurve, bases: tuple[Point, ...], order: int, seed: int) -> tuple[tuple[int, ...], int, int]:
    """Return a verified nonzero relation, sampled combinations, group additions.

    Setup, hash-table lookups, and independent verification are excluded from
    the addition count. Memory is one stored entry per distinct sample.
    """
    if len(bases) < 2 or order <= 2 or not all(curve.on_curve(base) for base in bases):
        raise ValueError("Need at least two valid bases in a prime-order subgroup")
    if any(curve.mul(order, base) is not None for base in bases):
        raise ValueError("A base lies outside the stated subgroup")
    rng = Random(seed)
    seen: dict[Point, tuple[int, ...]] = {}
    additions = 0
    for sample in range(1, 10 * order + 1):
        coefficients = tuple(rng.randrange(order) for _ in bases)
        point, cost = combination(curve, bases, coefficients)
        additions += cost
        previous = seen.get(point)
        if previous is not None:
            relation = tuple((left - right) % order for left, right in zip(coefficients, previous))
            if any(relation) and combination(curve, bases, relation)[0] is None:
                return relation, sample, additions
        else:
            seen[point] = coefficients
    raise RuntimeError("No nontrivial toy relation found within the bound")


def sample_bases(curve: ToyCurve, generator: Point, order: int, count: int, seed: int) -> tuple[Point, ...]:
    if count < 2 or count >= order:
        raise ValueError("Choose 2 <= count < order")
    rng = Random(seed)
    # Distinct public toy bases; the search receives points, not these scalars.
    scalars = (1, *rng.sample(range(2, order), count - 1))
    return tuple(curve.mul(scalar, generator) for scalar in scalars)


def sweep(curve: ToyCurve, counts: tuple[int, ...] = (2, 6), trials: int = 64) -> list[tuple[int, int, float, float]]:
    generator, order = prime_order_generator(curve)
    rows = []
    for count in counts:
        samples, additions = [], []
        for trial in range(trials):
            bases = sample_bases(curve, generator, order, count, seed=1000 + trial)
            relation, sampled, cost = find_relation(curve, bases, order, seed=2000 + trial)
            assert any(relation)
            samples.append(sampled)
            additions.append(cost)
        rows.append((order, count, median(samples), median(additions)))
    return rows


if __name__ == "__main__":
    print("Toy random-combination birthday search; 64 fixed-seed trials per row")
    print("group q | base count | median sampled combinations | median group additions")
    for field, b in ((223, 5), (211, 7)):
        for q, count, samples, adds in sweep(ToyCurve(field, b=b)):
            print(f"{q:7d} | {count:10d} | {samples:27g} | {adds:22g}")
