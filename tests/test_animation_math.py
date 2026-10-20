"""Testes das funções puras de animação. Executar: python3 -I tests/test_animation_math.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import animation_math as am  # noqa: E402


class RippleTests(unittest.TestCase):
    def test_radius_grows_to_farthest_corner(self):
        self.assertEqual(am.ripple_radius(0, 0, 30, 40, 0), 0)
        self.assertAlmostEqual(am.ripple_radius(0, 0, 30, 40, 1), 50.0)
        self.assertAlmostEqual(am.ripple_radius(15, 20, 30, 40, 1), (15 ** 2 + 20 ** 2) ** 0.5)

    def test_radius_is_clamped(self):
        self.assertEqual(am.ripple_radius(0, 0, 30, 40, 5), am.ripple_radius(0, 0, 30, 40, 1))
        self.assertEqual(am.ripple_radius(0, 0, 30, 40, -1), 0)

    def test_alpha_fades_out(self):
        self.assertAlmostEqual(am.ripple_alpha(0), 0.34)
        self.assertEqual(am.ripple_alpha(1), 0)
        self.assertGreater(am.ripple_alpha(0.2), am.ripple_alpha(0.6))


class SweepTests(unittest.TestCase):
    def test_enters_and_leaves_outside(self):
        self.assertEqual(am.busy_sweep_x(0, 100, 40), -40)
        self.assertAlmostEqual(am.busy_sweep_x(0.999999, 100, 40), 140, places=3)

    def test_phase_wraps(self):
        self.assertAlmostEqual(am.busy_sweep_x(1.25, 100, 40), am.busy_sweep_x(0.25, 100, 40))


class FaceTests(unittest.TestCase):
    def test_blink_range_and_rest(self):
        samples = [am.blink_amount(i / 100) for i in range(0, 1000)]
        self.assertTrue(all(0.0 <= v <= 1.0 for v in samples))
        self.assertEqual(am.blink_amount(1.0), 0.0)
        self.assertGreater(max(samples), 0.9)

    def test_bounce_and_pulse_bounds(self):
        for i in range(200):
            t = i / 37
            self.assertTrue(0.0 <= am.bounce(t, height=6) <= 6.0 + 1e-9)
            self.assertTrue(0.35 - 1e-9 <= am.pulse(t) <= 1.0 + 1e-9)

    def test_mouth_shapes(self):
        smile, _ = am.mouth_params("smile")
        calm, _ = am.mouth_params("calm")
        alert, _ = am.mouth_params("alert")
        self.assertGreater(smile, calm)
        self.assertGreater(calm, 0)
        self.assertLess(alert, calm)
        self.assertEqual(am.mouth_params("desconhecido"), am.mouth_params("calm"))


class SpectrumTests(unittest.TestCase):
    def test_points_in_unit_range_and_move(self):
        a = am.spectrum_points(40, 0.0)
        b = am.spectrum_points(40, 0.5)
        self.assertEqual(len(a), 40)
        self.assertTrue(all(0.0 <= v <= 1.0 for v in a + b))
        self.assertNotEqual(a, b)

    def test_single_point(self):
        self.assertEqual(len(am.spectrum_points(1, 0.0)), 1)


if __name__ == "__main__":
    unittest.main()
