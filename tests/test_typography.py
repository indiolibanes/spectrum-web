"""Testes das regras de tipografia (sem Qt). Executar: python -I -m unittest tests.test_typography"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import typography as ty  # noqa: E402


class SnapTests(unittest.TestCase):
    def test_sizes_land_on_scale(self):
        for raw in (7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 22, 24, 27, 30, 34, 36, 48):
            self.assertIn(ty.snap_size(raw), ty.SCALE, raw)

    def test_minimum_is_11(self):
        self.assertEqual(ty.snap_size(8), 11)
        self.assertEqual(ty.snap_size(10), 11)

    def test_scale_values_are_fixed_points(self):
        for step in ty.SCALE:
            self.assertEqual(ty.snap_size(step), step)

    def test_weights(self):
        self.assertEqual(ty.snap_weight("bold"), 600)
        self.assertEqual(ty.snap_weight("900"), 700)
        self.assertEqual(ty.snap_weight("800"), 700)
        self.assertEqual(ty.snap_weight("normal"), 400)
        self.assertEqual(ty.snap_weight("300"), 400)
        self.assertEqual(ty.snap_weight("500"), 500)


class QssTests(unittest.TestCase):
    REAL = [
        "font-size: 10px; color: #9CA3AF; font-weight: bold;",
        "color: #F3F4F6; font-size: 12px; line-height: 1.5;",
        "color: #38BDF8; font-size: 14px;",
        "font-size: 27px; color: #FFFFFF;",
        "font-size: 36px; color: #FFFFFF;",
        "color: #FFFFFF; font-size: 22px; font-weight: 600;",
        "font-size: 15px; font-weight: 800; color: #38BDF8; letter-spacing: 0.8px;",
        "QLabel { color: #E5E7EB; font-family: 'Segoe UI', Arial, sans-serif; }",
        "QTextEdit {background:#000;color:#999;border:0;font-family:Consolas;font-size:11px;}",
        "QPushButton {background:#111;border-radius:7px;padding:8px 12px;font-size:11px;font-weight:400;}",
        "QWidget#centralWidget {background:#000;font-family:Segoe UI;}",
    ]

    def test_idempotent(self):
        for text in self.REAL:
            once = ty.normalize_qss(text)
            self.assertEqual(once, ty.normalize_qss(once), text)

    def test_all_sizes_on_scale(self):
        for text in self.REAL:
            for size in re.findall(r"font-size:\s*(\d+)px", ty.normalize_qss(text)):
                self.assertIn(int(size), ty.SCALE, text)

    def test_line_height_and_letter_spacing_removed(self):
        out = ty.normalize_qss("color: #fff; font-size: 12px; line-height: 1.5; letter-spacing: 0.8px;")
        self.assertNotIn("line-height", out)
        self.assertNotIn("letter-spacing", out)

    def test_families_are_mapped(self):
        self.assertIn(ty.FAMILY_UI, ty.normalize_qss("QLabel { font-family: 'Segoe UI', Arial; }"))
        self.assertIn(ty.FAMILY_DATA, ty.normalize_qss("QTextEdit { font-family: Consolas; font-size: 11px; }"))
        self.assertIn(ty.FAMILY_DISPLAY, ty.normalize_qss("QLabel { font-family: Bahnschrift; font-size: 19px; }"))

    def test_big_sizes_get_default_family(self):
        self.assertIn(ty.FAMILY_DISPLAY, ty.normalize_qss("font-size: 22px; color: #fff;"))   # título
        self.assertIn(ty.FAMILY_DATA, ty.normalize_qss("font-size: 27px; color: #fff;"))      # número
        self.assertIn(ty.FAMILY_DATA, ty.normalize_qss("font-size: 36px; color: #fff;"))      # destaque

    def test_small_sizes_keep_app_font(self):
        self.assertNotIn("font-family", ty.normalize_qss("font-size: 11px; color: #fff;"))

    def test_explicit_family_is_respected(self):
        out = ty.normalize_qss(f"font-family: {ty.STACK_DATA}; font-size: 28px;")
        self.assertEqual(out.count("font-family"), 1)
        self.assertIn(ty.FAMILY_DATA, out)

    def test_untouched_when_no_font_properties(self):
        text = "QFrame { background: #000; border: 1px solid #333; }"
        self.assertEqual(ty.normalize_qss(text), text)

    def test_role_qss(self):
        self.assertIn("font-size: 28px", ty.qss("kpi"))
        self.assertIn(ty.FAMILY_DATA, ty.qss("kpi"))
        self.assertIn("font-weight: 600", ty.qss("title"))
        self.assertEqual(ty.normalize_qss(ty.qss("section")), ty.qss("section"))

    def test_braces_stay_balanced(self):
        for text in self.REAL:
            out = ty.normalize_qss(text)
            self.assertEqual(out.count("{"), out.count("}"))


class AssetsTests(unittest.TestCase):
    def test_font_files_exist(self):
        for name in ty.FONT_FILES:
            self.assertTrue((ty.fonts_directory() / name).exists(), name)

    def test_license_ships_with_fonts(self):
        self.assertTrue((ty.fonts_directory() / "LICENSE-IBM-Plex-OFL.txt").exists())


if __name__ == "__main__":
    unittest.main()
