"""Toy finite-field polynomial evaluation, motivated by Halo 2 circuits.

The small field is for learning only. This is not a Zcash protocol primitive.
"""
from __future__ import annotations
from dataclasses import dataclass

P = 97


@dataclass
class Operations:
    multiplies: int = 0
    additions: int = 0


def naive(coefficients: tuple[int, ...], x: int, stats: Operations | None = None) -> int:
    stats = stats if stats is not None else Operations()
    total = 0
    for degree, coefficient in enumerate(coefficients):
        power = 1
        for _ in range(degree):
            power = power * x % P
            stats.multiplies += 1
        total = (total + coefficient * power) % P
        stats.multiplies += 1
        stats.additions += 1
    return total


def horner(coefficients: tuple[int, ...], x: int, stats: Operations | None = None) -> int:
    stats = stats if stats is not None else Operations()
    total = 0
    for coefficient in reversed(coefficients):
        total = (total * x + coefficient) % P
        stats.multiplies += 1
        stats.additions += 1
    return total


if __name__ == "__main__":
    for degree in (0, 1, 2, 4, 8, 16, 32):
        coefficients = tuple(range(degree + 1))
        slow, fast = Operations(), Operations()
        assert naive(coefficients, 7, slow) == horner(coefficients, 7, fast)
        print(f"degree={degree:2d} naive multiplications={slow.multiplies:3d} "
              f"Horner multiplications={fast.multiplies:3d}")
