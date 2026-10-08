"""Compare classical and Strassen square matrix multiplication over integers."""
from __future__ import annotations

from dataclasses import dataclass
from random import Random
from time import perf_counter
from statistics import median

Matrix = tuple[tuple[int, ...], ...]


@dataclass
class Operations:
    multiplies: int = 0
    additions: int = 0


def validate(a: Matrix, b: Matrix) -> int:
    n = len(a)
    if n == 0 or n != len(b) or n & (n - 1) or any(len(row) != n for row in (*a, *b)):
        raise ValueError("Both matrices must be square with the same power-of-two size")
    return n


def add(a: Matrix, b: Matrix, stats: Operations, sign: int = 1) -> Matrix:
    n = len(a)
    stats.additions += n * n
    return tuple(tuple(a[i][j] + sign * b[i][j] for j in range(n)) for i in range(n))


def classical(a: Matrix, b: Matrix, stats: Operations | None = None) -> Matrix:
    n = validate(a, b)
    stats = stats if stats is not None else Operations()
    stats.multiplies += n**3
    stats.additions += n * n * (n - 1)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n)) for i in range(n))


def split(a: Matrix) -> tuple[Matrix, Matrix, Matrix, Matrix]:
    h = len(a) // 2
    return (tuple(row[:h] for row in a[:h]), tuple(row[h:] for row in a[:h]),
            tuple(row[:h] for row in a[h:]), tuple(row[h:] for row in a[h:]))


def join(a: Matrix, b: Matrix, c: Matrix, d: Matrix) -> Matrix:
    return tuple(a[i] + b[i] for i in range(len(a))) + tuple(c[i] + d[i] for i in range(len(c)))


def strassen(a: Matrix, b: Matrix, stats: Operations | None = None) -> Matrix:
    n = validate(a, b)
    stats = stats if stats is not None else Operations()
    if n == 1:
        stats.multiplies += 1
        return ((a[0][0] * b[0][0],),)
    a11, a12, a21, a22 = split(a)
    b11, b12, b21, b22 = split(b)
    m1 = strassen(add(a11, a22, stats), add(b11, b22, stats), stats)
    m2 = strassen(add(a21, a22, stats), b11, stats)
    m3 = strassen(a11, add(b12, b22, stats, -1), stats)
    m4 = strassen(a22, add(b21, b11, stats, -1), stats)
    m5 = strassen(add(a11, a12, stats), b22, stats)
    m6 = strassen(add(a21, a11, stats, -1), add(b11, b12, stats), stats)
    m7 = strassen(add(a12, a22, stats, -1), add(b21, b22, stats), stats)
    c11 = add(add(add(m1, m4, stats), m5, stats, -1), m7, stats)
    c12 = add(m3, m5, stats)
    c21 = add(m2, m4, stats)
    c22 = add(add(add(m1, m2, stats, -1), m3, stats), m6, stats)
    return join(c11, c12, c21, c22)


def sample(n: int, seed: int = 0) -> tuple[Matrix, Matrix]:
    rng = Random(seed)
    return tuple(tuple(rng.randrange(-9, 10) for _ in range(n)) for _ in range(n)), tuple(
        tuple(rng.randrange(-9, 10) for _ in range(n)) for _ in range(n))


if __name__ == "__main__":
    print("n  classical mul/add  Strassen mul/add  classical s  Strassen s")
    for n in (1, 2, 4, 8, 16):
        a, b = sample(n)
        counts = []
        times = []
        results = []
        for fn in (classical, strassen):
            stats = Operations()
            runs = []
            result = None
            for _ in range(5):
                start = perf_counter()
                result = fn(a, b, stats if not runs else Operations())
                runs.append(perf_counter() - start)
            counts.append(stats)
            times.append(median(runs))
            results.append(result)
        assert results[0] == results[1]
        print(f"{n:<2} {counts[0].multiplies:>7}/{counts[0].additions:<7} "
              f"{counts[1].multiplies:>7}/{counts[1].additions:<7} "
              f"{times[0]:>11.6f} {times[1]:>11.6f}")
