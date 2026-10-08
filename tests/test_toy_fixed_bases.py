import unittest

from experiments.toy_ecdlp import ToyCurve, prime_order_generator
from experiments.toy_fixed_bases import combination, find_relation, sample_bases


class ToyFixedBasesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curve = ToyCurve(223, b=5)
        cls.generator, cls.order = prime_order_generator(cls.curve)

    def test_relations_verify_for_multiple_seeds_and_base_counts(self):
        for count in (2, 6):
            for trial in range(20):
                with self.subTest(count=count, trial=trial):
                    bases = sample_bases(self.curve, self.generator, self.order, count, trial)
                    relation, samples, adds = find_relation(self.curve, bases, self.order, 100 + trial)
                    self.assertTrue(any(relation))
                    self.assertIsNone(combination(self.curve, bases, relation)[0])
                    self.assertGreater(samples, 1)
                    self.assertGreater(adds, 0)
                    if count == 2:
                        # With bases G and Q, a*G + b*Q = 0 reveals log_G(Q).
                        a, b = relation
                        self.assertNotEqual(b, 0)
                        log = -a * pow(b, -1, self.order) % self.order
                        self.assertEqual(self.curve.mul(log, bases[0]), bases[1])

    def test_rejects_bad_inputs(self):
        with self.assertRaises(ValueError):
            sample_bases(self.curve, self.generator, self.order, 1, 0)
        with self.assertRaises(ValueError):
            combination(self.curve, (self.generator,), ())
        with self.assertRaises(ValueError):
            find_relation(self.curve, (self.generator,), self.order, 0)


if __name__ == "__main__":
    unittest.main()
