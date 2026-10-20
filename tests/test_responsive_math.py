"""Testes das regras de responsividade (sem Qt): python3 -I tests/test_responsive_math.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import responsive_math as rm  # noqa: E402


class FitTests(unittest.TestCase):
    def test_reference_size_is_one_to_one(self):
        scale, w, h = rm.fit(1600, 1000, 1000, 800)
        self.assertAlmostEqual(scale, 1.0)
        self.assertEqual((w, h), (1600, 1000))

    def test_full_hd_grows_the_text_a_little(self):
        scale, w, h = rm.fit(1920, 1080, 1000, 800)
        self.assertAlmostEqual(scale, 1.2)
        self.assertGreaterEqual(w * scale, 1920 - 1e-6)
        self.assertGreaterEqual(h * scale, 1080 - 1e-6)

    def test_small_laptop_keeps_the_text_readable(self):
        """1366x768: antes a escala era 0,77 (14 px viravam 10,8 px); agora fica em 0,90."""
        scale, _, _ = rm.fit(1366, 768, 1000, 700)
        self.assertAlmostEqual(scale, 0.90)

    def test_scale_shrinks_only_as_much_as_the_content_needs(self):
        scale, w, h = rm.fit(1000, 700, 1000, 900)
        self.assertAlmostEqual(scale, 700 / 900)
        self.assertGreaterEqual(w, 1000 / scale - 1)
        scale2, _, _ = rm.fit(800, 900, 1200, 600)
        self.assertAlmostEqual(scale2, 800 / 1200)

    def test_logical_size_always_covers_the_window(self):
        for vw, vh in ((320, 480), (800, 1280), (1024, 600), (1280, 720), (1366, 768), (1920, 1080), (2560, 1440), (3440, 1440)):
            scale, w, h = rm.fit(vw, vh, 960, 760)
            self.assertGreaterEqual(w * scale, vw - 1e-6, (vw, vh))
            self.assertGreaterEqual(h * scale, vh - 1e-6, (vw, vh))
            self.assertLessEqual(scale, rm.MAX_SCALE)
            self.assertGreaterEqual(w, 960 - 1, (vw, vh))   # nunca menor que o mínimo do layout
            self.assertGreaterEqual(h, 760 - 1, (vw, vh))

    def test_never_exceeds_max_scale(self):
        scale, _, _ = rm.fit(5120, 2880, 900, 700)
        self.assertAlmostEqual(scale, rm.MAX_SCALE)

    def test_degenerate_inputs_do_not_crash(self):
        for args in ((0, 0, 0, 0), (-5, 10, 10, 10), (100, 100, 0, 0)):
            scale, w, h = rm.fit(*args)
            self.assertGreater(scale, 0)
            self.assertGreaterEqual(w, 1)
            self.assertGreaterEqual(h, 1)


class LayoutModeTests(unittest.TestCase):
    def test_wide_landscape_is_the_full_layout(self):
        mode = rm.layout_mode(1700, 1000)
        self.assertEqual(mode, {"topbar_two_rows": False, "kpi_columns": 4, "stack_main": False})

    def test_laptop_gets_a_two_row_header_only(self):
        mode = rm.layout_mode(1366 / 0.9, 768 / 0.9)
        self.assertTrue(mode["topbar_two_rows"])
        self.assertEqual(mode["kpi_columns"], 4)
        self.assertFalse(mode["stack_main"])

    def test_tablet_portrait_stacks(self):
        mode = rm.layout_mode(800 / 0.9, 1280 / 0.9)
        self.assertTrue(mode["stack_main"])
        self.assertEqual(mode["kpi_columns"], 2)
        self.assertTrue(mode["topbar_two_rows"])

    def test_breakpoints_are_ordered(self):
        self.assertGreater(rm.TOPBAR_TWO_ROWS_BELOW, rm.KPI_TWO_COLUMNS_BELOW)
        self.assertGreater(rm.KPI_TWO_COLUMNS_BELOW, rm.STACK_BELOW)


if __name__ == "__main__":
    unittest.main()
