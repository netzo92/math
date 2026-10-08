import unittest

from experiments.toy_ecdlp import ToyCurve
from experiments.toy_endomorphism import cube_root_of_unity, endomorphism, experiment


class ToyEndomorphismTests(unittest.TestCase):
    def test_every_subgroup_element_on_three_toy_curves(self):
        for p in (223, 211, 307):
            with self.subTest(p=p):
                q, zeta, eigenvalue, nonzero, total = experiment(p)
                self.assertEqual(pow(zeta, 3, p), 1)
                self.assertNotEqual(zeta, 1)
                self.assertEqual(pow(eigenvalue, 3, q), 1)
                self.assertNotEqual(eigenvalue, 1)
                self.assertEqual(nonzero, (q - 1) // 6)
                self.assertEqual(total, 1 + nonzero)

    def test_rejects_inapplicable_curve_or_root(self):
        with self.assertRaises(ValueError):
            cube_root_of_unity(227)
        with self.assertRaises(ValueError):
            endomorphism(ToyCurve(223, a=1, b=5), None, 39)
        with self.assertRaises(ValueError):
            endomorphism(ToyCurve(223, a=0, b=5), None, 1)


if __name__ == "__main__":
    unittest.main()
