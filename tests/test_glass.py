"""Testes do módulo de vidro e da paleta (sem Qt): python3 -I tests/test_glass.py"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import glass  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def load_palettes():
    """Lê PALETTES de appearance.py sem importar o PyQt5."""
    source = (ROOT / "appearance.py").read_text(encoding="utf-8")
    start = source.index("PALETTES={")
    end = source.index("DEFAULT_THEME")
    namespace = {}
    exec(source[start:end], namespace)
    return namespace["PALETTES"]


def contrast(a, b):
    la, lb = glass.luminance(a), glass.luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


class PaletteTests(unittest.TestCase):
    def setUp(self):
        self.palettes = load_palettes()

    def test_two_themes_with_the_same_tokens(self):
        self.assertEqual(set(self.palettes), {"umber", "light"})
        self.assertEqual(set(self.palettes["umber"]), set(self.palettes["light"]))

    def test_every_token_is_a_hex_color(self):
        for name, palette in self.palettes.items():
            for key, value in palette.items():
                self.assertRegex(value, r"^#[0-9A-Fa-f]{6}$", (name, key))

    def test_dark_theme_is_near_amoled(self):
        self.assertLess(glass.luminance(self.palettes["umber"]["canvas"]), 0.01)
        self.assertTrue(glass.is_dark(self.palettes["umber"]))
        self.assertFalse(glass.is_dark(self.palettes["light"]))

    def test_dark_theme_inherits_the_identity_colors(self):
        p = self.palettes["umber"]
        self.assertEqual(p["accent"].upper(), "#E2C35C")
        self.assertEqual(p["heading"].upper(), "#FFF1B4")
        self.assertEqual(p["surface"].upper(), "#14120D")

    def test_text_contrast_is_comfortable(self):
        for name, p in self.palettes.items():
            self.assertGreater(contrast(p["text"], p["canvas"]), 12, name)
            self.assertGreater(contrast(p["muted"], p["surface"]), 6, name)
            self.assertGreater(contrast(p["accent"], p["canvas"]), 4.5, name)
            self.assertGreater(contrast(p["on_strong"], p["accent_strong"]), 4.5, name)
            self.assertGreater(contrast(p["on_strong"], p["danger_strong"]), 4.5, name)
            self.assertGreater(contrast(p["disabled"], p["canvas"]), 3.0, name)


class GlassTests(unittest.TestCase):
    def setUp(self):
        self.palettes = load_palettes()

    def test_rgba_format_and_clamp(self):
        self.assertEqual(glass.rgba("#FF8000", 0.5), "rgba(255, 128, 0, 50%)")
        self.assertEqual(glass.rgba("#000000", 2), "rgba(0, 0, 0, 100%)")
        self.assertEqual(glass.rgba("#000000", -1), "rgba(0, 0, 0, 0%)")

    def test_every_fill_is_a_valid_qss_value(self):
        grad = re.compile(r"^qlineargradient\(x1:0,y1:0,x2:0,y2:1,stop:0 [^,]+(?:\([^)]*\))?,stop:1 .+\)$")
        for p in self.palettes.values():
            fills = [glass.panel_fill(p), glass.result_fill(p), glass.primary_fill(p), glass.primary_fill(p, "hover"),
                     glass.primary_fill(p, "hot")] + [glass.button_fill(p, s) for s in ("rest", "hover", "disabled")]
            for value in fills:
                self.assertRegex(value, grad)
                self.assertEqual(value.count("("), value.count(")"))
            self.assertTrue(glass.field_fill(p))
            self.assertTrue(glass.rim(p).startswith("rgba("))

    def test_panels_are_translucent(self):
        for p in self.palettes.values():
            self.assertIn("%", glass.panel_fill(p))
            self.assertNotIn("100%", glass.panel_fill(p))

    def test_glow_specs_are_in_range(self):
        for p in self.palettes.values():
            spec = glass.glow_spec(p)
            self.assertGreaterEqual(len(spec), 2)
            for x, y, radius, color, alpha in spec:
                self.assertTrue(0 <= x <= 1 and 0 <= y <= 1)
                self.assertTrue(0 < radius <= 1.2)
                self.assertTrue(0 < alpha < 0.2)
                self.assertRegex(color, r"^#[0-9A-Fa-f]{6}$")

    def test_edge_highlight_alpha(self):
        for p in self.palettes.values():
            color, alpha = glass.edge_highlight(p)
            self.assertRegex(color, r"^#[0-9A-Fa-f]{6}$")
            self.assertTrue(0 < alpha <= 1)


class AssetTests(unittest.TestCase):
    def test_generated_assets_exist(self):
        for rel in ("assets/textures/madeira-escura.png", "assets/textures/celulose-claro.png",
                    "assets/cursors/fibra-seta.png", "assets/cursors/fibra-seta@2x.png",
                    "assets/cursors/fibra-mao.png", "assets/cursors/fibra-mao@2x.png"):
            path = ROOT / rel
            self.assertTrue(path.exists(), rel)
            self.assertEqual(path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n", rel)

    def test_font_files_declared_in_typography_exist(self):
        source = (ROOT / "typography.py").read_text(encoding="utf-8")
        for name in re.findall(r'"((?:IBMPlex|EBGaramond)[A-Za-z-]*\.ttf)"', source):
            self.assertTrue((ROOT / "assets" / "fonts" / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
