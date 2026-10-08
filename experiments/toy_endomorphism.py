"""Check the cube-root endomorphism on tiny y^2 = x^3 + 5 curves.

This is a structural toy experiment, not an attack on Pasta or Zcash keys.
The bound in ToyCurve deliberately excludes production-sized curves.
"""
from __future__ import annotations

from experiments.toy_ecdlp import Point, ToyCurve, prime_order_generator


def cube_root_of_unity(p: int) -> int:
    if p % 3 != 1:
        raise ValueError("A nontrivial cube root requires p = 1 mod 3")
    return next(z for z in range(2, p) if pow(z, 3, p) == 1)


def endomorphism(curve: ToyCurve, point: Point, zeta: int) -> Point:
    if curve.a != 0:
        raise ValueError("This endomorphism requires a = 0")
    if not curve.on_curve(point) or pow(zeta, 3, curve.p) != 1 or zeta % curve.p == 1:
        raise ValueError("Invalid point or nontrivial cube root")
    return None if point is None else (zeta * point[0] % curve.p, point[1])


def experiment(p: int) -> tuple[int, int, int, int, int]:
    curve = ToyCurve(p, a=0, b=5)
    generator, order = prime_order_generator(curve)
    if order <= 3:
        raise ValueError("Choose a subgroup of order greater than 3")
    zeta = cube_root_of_unity(p)
    image = endomorphism(curve, generator, zeta)
    eigenvalue = next((k for k in range(order) if curve.mul(k, generator) == image), None)
    if eigenvalue is None or eigenvalue == 1 or pow(eigenvalue, 3, order) != 1:
        raise ValueError("Chosen subgroup has no nontrivial cube-root action")

    nonzero_orbits: set[frozenset[Point]] = set()
    for k in range(order):
        point = curve.mul(k, generator)
        assert endomorphism(curve, point, zeta) == curve.mul(k * eigenvalue, generator)
        assert endomorphism(curve, endomorphism(curve, endomorphism(curve, point, zeta), zeta), zeta) == point
        if point is None:
            continue
        orbit = frozenset(curve.mul(k * sign * pow(eigenvalue, power, order), generator)
                          for sign in (1, -1) for power in range(3))
        assert len(orbit) == 6
        nonzero_orbits.add(orbit)
    assert len(nonzero_orbits) == (order - 1) // 6
    return order, zeta, eigenvalue, len(nonzero_orbits), 1 + len(nonzero_orbits)


if __name__ == "__main__":
    print("Toy curve: y^2 = x^3 + 5; identity counted separately")
    print("field p | subgroup q | zeta | lambda | nonzero six-point classes | total classes")
    for field in (223, 211, 307):
        q, zeta, eigenvalue, nonzero, total = experiment(field)
        print(f"{field:7d} | {q:10d} | {zeta:4d} | {eigenvalue:6d} | {nonzero:25d} | {total:13d}")
