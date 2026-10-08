import unittest
from random import Random
from experiments.matrix_multiply import Operations as MatrixOperations, classical, sample, strassen
from experiments.polynomial_eval import Operations as FieldOperations, P, horner, naive


class MatrixTests(unittest.TestCase):
    def test_against_classical_for_signed_random_matrices(self):
        for n in (1, 2, 4, 8):
            for seed in range(12):
                a, b = sample(n, seed)
                self.assertEqual(strassen(a, b), classical(a, b))

    def test_two_by_two_operation_counts(self):
        a, b = sample(2)
        classical_count, strassen_count = MatrixOperations(), MatrixOperations()
        classical(a, b, classical_count)
        strassen(a, b, strassen_count)
        self.assertEqual((classical_count.multiplies, strassen_count.multiplies), (8, 7))
        self.assertGreater(strassen_count.additions, classical_count.additions)

    def test_bad_dimensions_rejected(self):
        with self.assertRaises(ValueError):
            strassen(((1, 2),), ((1,),))


class PolynomialTests(unittest.TestCase):
    def test_naive_equals_horner_in_toy_field(self):
        rng = Random(0)
        for degree in range(30):
            coefficients = tuple(rng.randrange(P) for _ in range(degree + 1))
            for x in (0, 1, 7, P - 1):
                self.assertEqual(naive(coefficients, x), horner(coefficients, x))

    def test_operation_growth(self):
        coefficients = tuple(range(17))
        slow, fast = FieldOperations(), FieldOperations()
        naive(coefficients, 7, slow)
        horner(coefficients, 7, fast)
        self.assertGreater(slow.multiplies, fast.multiplies)


if __name__ == "__main__":
    unittest.main()
