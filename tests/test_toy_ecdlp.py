import unittest
from experiments.toy_ecdlp import ToyCurve, baby_step_giant_step, exhaustive, pollard_rho, prime_order_generator


class ToyDiscreteLogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curve = ToyCurve(211)
        cls.generator, cls.order = prime_order_generator(cls.curve)

    def test_every_log_in_the_chosen_subgroup(self):
        for secret in range(self.order):
            target = self.curve.mul(secret, self.generator)
            self.assertEqual(exhaustive(self.curve, self.generator, target, self.order)[0], secret)
            self.assertEqual(baby_step_giant_step(self.curve, self.generator, target, self.order)[0], secret)
            self.assertEqual(pollard_rho(self.curve, self.generator, target, self.order)[0], secret)

    def test_group_edges(self):
        self.assertIsNone(self.curve.mul(self.order, self.generator))
        self.assertEqual(self.curve.add(self.generator, self.curve.neg(self.generator)), None)
        self.assertTrue(self.curve.on_curve(self.generator))

    def test_bounded_toy_domain(self):
        with self.assertRaises(ValueError):
            ToyCurve(1009)
        with self.assertRaises(ValueError):
            ToyCurve(211, 0, 0)
        with self.assertRaises(ValueError):
            self.curve.add(self.generator, (0, 0))


if __name__ == "__main__":
    unittest.main()
