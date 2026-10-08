"""Bounded elliptic-curve discrete-log lab on tiny, public toy groups.

This deliberately cannot accept a production curve, wallet key, or address.
The experiments demonstrate generic attack scaling; they test no Zcash keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from statistics import median

Point = tuple[int, int] | None  # None is the identity.
MAX_TOY_PRIME = 1000


@dataclass(frozen=True)
class ToyCurve:
    p: int
    a: int = 0
    b: int = 7

    def __post_init__(self) -> None:
        if not (5 <= self.p <= MAX_TOY_PRIME and is_prime(self.p)):
            raise ValueError("Only small prime fields (5..1000) are permitted")
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise ValueError("Singular curve")

    def on_curve(self, point: Point) -> bool:
        return point is None or (
            0 <= point[0] < self.p and 0 <= point[1] < self.p and
            (point[1] ** 2 - point[0] ** 3 - self.a * point[0] - self.b) % self.p == 0
        )

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], (-point[1]) % self.p)

    def add(self, left: Point, right: Point) -> Point:
        if not self.on_curve(left) or not self.on_curve(right):
            raise ValueError("Point is not on the toy curve")
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            numerator = (3 * x1 * x1 + self.a) % self.p
            denominator = 2 * y1 % self.p
        else:
            numerator = (y2 - y1) % self.p
            denominator = (x2 - x1) % self.p
        slope = numerator * pow(denominator, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        return x3, y3

    def mul(self, factor: int, point: Point) -> Point:
        if factor < 0:
            return self.mul(-factor, self.neg(point))
        if not self.on_curve(point):
            raise ValueError("Point is not on the toy curve")
        result: Point = None
        while factor:
            if factor & 1:
                result = self.add(result, point)
            point = self.add(point, point)
            factor >>= 1
        return result


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for divisor in range(2, isqrt(n) + 1):
        if n % divisor == 0:
            return False
    return True


def prime_order_generator(curve: ToyCurve) -> tuple[Point, int]:
    """Find the largest prime-order subgroup seen on this tiny curve."""
    best: tuple[Point, int] = (None, 0)
    # Exhaustive enumeration is intentionally limited to small fields.
    for x in range(curve.p):
        rhs = (x**3 + curve.a * x + curve.b) % curve.p
        for y in range(curve.p):
            if y * y % curve.p != rhs:
                continue
            point: Point = (x, y)
            current: Point = None
            for order in range(1, 2 * curve.p + 2 * isqrt(curve.p) + 2):
                current = curve.add(current, point)
                if current is None:
                    if is_prime(order) and order > best[1]:
                        best = (point, order)
                    break
    if best[0] is None:
        raise ValueError("No prime-order point found")
    return best


def exhaustive(curve: ToyCurve, generator: Point, target: Point, order: int) -> tuple[int, int]:
    current: Point = None
    for guess in range(order):
        if current == target:
            return guess, guess
        current = curve.add(current, generator)
    raise ValueError("Target is not in the chosen subgroup")


def baby_step_giant_step(curve: ToyCurve, generator: Point, target: Point, order: int) -> tuple[int, int, int]:
    """Return the log, group-addition count, and stored baby-step count."""
    width = isqrt(order) + (isqrt(order) ** 2 != order)
    baby: dict[Point, int] = {}
    current: Point = None
    additions = 0
    for j in range(width):
        baby.setdefault(current, j)
        current = curve.add(current, generator)
        additions += 1
    stride = curve.mul(-width, generator)
    giant = target
    for i in range(width + 1):
        if giant in baby:
            candidate = (i * width + baby[giant]) % order
            if curve.mul(candidate, generator) == target:
                return candidate, additions, len(baby)
        giant = curve.add(giant, stride)
        additions += 1
    raise ValueError("Target is not in the chosen subgroup")


def pollard_rho(curve: ToyCurve, generator: Point, target: Point, order: int) -> tuple[int, int]:
    """Generic rho attack: expected square-root work, constant stored points.

    A collision may fail to determine the log; bounded deterministic restarts
    keep this toy demonstration reproducible. `additions` counts group additions.
    """
    additions = 0

    def advance(state: tuple[Point, int, int]) -> tuple[Point, int, int]:
        nonlocal additions
        point, a, b = state
        bucket = 0 if point is None else point[0] % 3
        if bucket == 0:
            point, a = curve.add(point, generator), (a + 1) % order
        elif bucket == 1:
            point, b = curve.add(point, target), (b + 1) % order
        else:
            point, a, b = curve.add(point, point), 2 * a % order, 2 * b % order
        additions += 1
        return point, a, b

    for attempt in range(1, 65):
        a, b = (attempt * 17 + 3) % order, (attempt * 29 + 7) % order
        start = (curve.add(curve.mul(a, generator), curve.mul(b, target)), a, b)
        additions += 1
        tortoise, hare = advance(start), advance(advance(start))
        for _ in range(5 * order):
            if tortoise[0] == hare[0]:
                denominator = (hare[2] - tortoise[2]) % order
                if denominator:
                    candidate = (tortoise[1] - hare[1]) * pow(denominator, -1, order) % order
                    if curve.mul(candidate, generator) == target:
                        return candidate, additions
                break
            tortoise = advance(tortoise)
            hare = advance(advance(hare))
    raise ValueError("Toy rho walk did not resolve this logarithm")


if __name__ == "__main__":
    print("toy p | subgroup q | exhaustive median adds | BSGS median adds/points | rho median/p95 adds")
    for p in (223, 307, 211):
        curve = ToyCurve(p)
        generator, order = prime_order_generator(curve)
        exhaustive_costs, bsgs_costs, rho_costs = [], [], []
        memory = None
        for secret in range(order):
            target = curve.mul(secret, generator)
            slow, slow_adds = exhaustive(curve, generator, target, order)
            fast, fast_adds, memory = baby_step_giant_step(curve, generator, target, order)
            rho, rho_adds = pollard_rho(curve, generator, target, order)
            assert slow == fast == rho == secret
            exhaustive_costs.append(slow_adds)
            bsgs_costs.append(fast_adds)
            rho_costs.append(rho_adds)
        rho_costs.sort()
        p95 = rho_costs[(95 * order + 99) // 100 - 1]
        print(f"{p:5d} | {order:10d} | {median(exhaustive_costs):22g} | "
              f"{median(bsgs_costs):16g}/{memory:<6d} | "
              f"{median(rho_costs):6g}/{p95:<6d}")
