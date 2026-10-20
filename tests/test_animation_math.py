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


class SpringTests(unittest.TestCase):
    def test_starts_at_zero_and_settles_at_one(self):
        self.assertEqual(am.spring(0.0), 0.0)
        self.assertEqual(am.spring(-1.0), 0.0)
        self.assertAlmostEqual(am.spring(3.0), 1.0, places=3)

    def test_underdamped_spring_overshoots(self):
        peak = max(am.spring(i / 200.0, 0.5, 0.4) for i in range(0, 400))
        self.assertGreater(peak, 1.05)
        self.assertLess(peak, 1.5)

    def test_critically_damped_does_not_overshoot(self):
        peak = max(am.spring(i / 200.0, 0.5, 1.0) for i in range(0, 400))
        self.assertLessEqual(peak, 1.0 + 1e-9)

    def test_more_damping_overshoots_less(self):
        def peak(damping):
            return max(am.spring(i / 200.0, 0.5, damping) for i in range(0, 400))
        self.assertGreater(peak(0.3), peak(0.6))
        self.assertGreater(peak(0.6), peak(0.9))

    def test_never_nan(self):
        for t in (0.0, 1e-9, 0.01, 1.0, 100.0):
            for damping in (0.0, 0.5, 0.999, 1.0, 2.0):
                value = am.spring(t, 0.4, damping)
                self.assertEqual(value, value)


class EntranceTests(unittest.TestCase):
    def test_ease_out_expo_endpoints_and_monotonic(self):
        self.assertEqual(am.ease_out_expo(0.0), 0.0)
        self.assertEqual(am.ease_out_expo(1.0), 1.0)
        values = [am.ease_out_expo(i / 20.0) for i in range(21)]
        self.assertEqual(values, sorted(values))
        self.assertGreater(am.ease_out_expo(0.3), 0.8)   # sobe depressa no começo

    def test_stagger_delays_each_item(self):
        self.assertEqual(am.staggered(0.0, 0), 0.0)
        self.assertGreater(am.staggered(0.2, 0), am.staggered(0.2, 3))
        self.assertEqual(am.staggered(0.1, 5, 0.06, 0.5), 0.0)
        self.assertEqual(am.staggered(5.0, 5), 1.0)


if __name__ == "__main__":
    unittest.main()
