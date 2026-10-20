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
        self.assertEqual(set(self.palettes), {"noturno", "light"})
        self.assertEqual(set(self.palettes["noturno"]), set(self.palettes["light"]))

    def test_every_token_is_a_hex_color(self):
        for name, palette in self.palettes.items():
            for key, value in palette.items():
                self.assertRegex(value, r"^#[0-9A-Fa-f]{6}$", (name, key))

    def test_night_theme_is_dark_and_neutral_enough(self):
        p = self.palettes["noturno"]
        self.assertTrue(glass.is_dark(p))
        self.assertFalse(glass.is_dark(self.palettes["light"]))
        self.assertLess(glass.luminance(p["canvas"]), 0.01, "fundo quase preto")

    def test_night_theme_is_purple_with_a_teal_secondary(self):
        p = self.palettes["noturno"]
        r, g, b = glass._channels(p["accent"])
        self.assertTrue(b > r > g, "o destaque do noturno é roxo")
        r, g, b = glass._channels(p["secondary"])
        self.assertTrue(g >= b > r, "a secundária é turquesa")

    def test_alarm_colors_are_not_used_as_identity_colors(self):
        """ISA-101: vermelho/laranja/amarelo são de alarme. Nenhum tom de botão pode ter esse matiz."""
        import colorsys
        for name, p in self.palettes.items():
            for tone in glass.TONES:
                r, g, b = (c / 255 for c in glass._channels(glass.tone_color(p, tone)))
                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                hue = h * 360
                if s > 0.30:   # tons neutros (slate, sand) ficam de fora
                    self.assertFalse(hue < 70 or hue > 335, (name, tone, round(hue)))

    def test_every_button_tone_is_distinct(self):
        for name, p in self.palettes.items():
            colors = [glass.tone_color(p, t) for t in glass.TONES]
            self.assertEqual(len(set(colors)), len(colors), name)

    def test_text_contrast_is_comfortable(self):
        for name, p in self.palettes.items():
            self.assertGreater(contrast(p["text"], p["canvas"]), 14, name)
            self.assertGreater(contrast(p["text"], p["surface"]), 13, name)
            self.assertGreater(contrast(p["muted"], p["surface"]), 7, name)
            self.assertGreater(contrast(p["heading"], p["surface"]), 12, name)
            self.assertGreater(contrast(p["accent"], p["canvas"]), 4.5, name)
            self.assertGreater(contrast(p["on_strong"], p["accent_strong"]), 4.5, name)
            self.assertGreater(contrast(p["on_strong"], p["danger_strong"]), 4.5, name)
            self.assertGreater(contrast(p["disabled"], p["canvas"]), 3.0, name)
            for tone in ("sky", "violet", "rose", "positive", "warning", "danger", "secondary", "slate", "sand"):
                self.assertGreater(contrast(p[tone], p["surface"]), 4.5, (name, tone))

    def test_series_palettes_have_six_distinct_colors(self):
        source = (ROOT / "appearance.py").read_text(encoding="utf-8")
        start, end = source.index("SERIES={"), source.index("DEFAULT_THEME")
        ns = {}
        exec(source[start:end], ns)
        for name, colors in ns["SERIES"].items():
            self.assertEqual(len(colors), 6, name)
            self.assertEqual(len(set(colors)), 6, name)
            surface = self.palettes[name]["surface"]
            for color in colors:
                self.assertRegex(color, r"^#[0-9A-Fa-f]{6}$")
                self.assertGreater(contrast(color, surface), 2.0, (name, color))


class FlatSurfaceTests(unittest.TestCase):
    """ISA-101: superfícies lisas, sem degradê, translucidez, brilho ou textura."""

    def setUp(self):
        self.palettes = load_palettes()

    def test_rgba_format_and_clamp(self):
        self.assertEqual(glass.rgba("#FF8000", 0.5), "rgba(255, 128, 0, 50%)")
        self.assertEqual(glass.rgba("#000000", 2), "rgba(0, 0, 0, 100%)")
        self.assertEqual(glass.rgba("#000000", -1), "rgba(0, 0, 0, 0%)")

    def test_every_fill_is_a_solid_hex_color(self):
        for p in self.palettes.values():
            fills = [glass.panel_fill(p), glass.result_fill(p), glass.field_fill(p), glass.rim(p), glass.rim(p, .6), glass.rim(p, 1.5)]
            fills += [glass.primary_fill(p, s) for s in ("rest", "hover", "hot")]
            fills += [glass.button_fill(p, s) for s in ("rest", "hover", "disabled")]
            for tone in glass.TONES:
                fills += [glass.tone_fill(p, tone, s) for s in ("rest", "hover")]
                fills += [glass.tone_border(p, tone, s) for s in ("rest", "hover")] + [glass.tone_hot(p, tone)]
            for value in fills:
                self.assertRegex(value, r"^#[0-9A-Fa-f]{6}$", value)

    def test_no_gradient_helper_is_left(self):
        self.assertFalse(hasattr(glass, "vgrad"))

    def test_no_ambient_glow_and_no_edge_light(self):
        for p in self.palettes.values():
            self.assertEqual(glass.glow_spec(p), [])
            self.assertEqual(glass.edge_highlight(p)[1], 0)

    def test_no_texture_in_any_theme(self):
        source = (ROOT / "appearance.py").read_text(encoding="utf-8")
        self.assertIn("TEXTURE_FILES={}", source)

    def test_tone_recipes(self):
        for p in self.palettes.values():
            for tone in glass.TONES:
                self.assertRegex(glass.tone_text(p, tone), r"^#[0-9A-Fa-f]{6}$")
                # texto do botão em tom sobre o preenchimento do próprio botão (legibilidade)
                for state in ("rest", "hover"):
                    self.assertGreater(contrast(glass.tone_text(p, tone), glass.tone_fill(p, tone, state)), 4.5, (tone, state, glass.is_dark(p)))
                self.assertGreater(contrast(glass.on_tone(p), glass.tone_color(p, tone)), 4.5, tone)

    def test_secondary_buttons_are_visible_on_dark(self):
        p = self.palettes["noturno"]
        self.assertGreater(contrast(glass.button_fill(p), p["surface"]), 1.15)
        self.assertGreater(contrast(glass.rim(p, 1.5), p["surface"]), 2.5)


class AssetTests(unittest.TestCase):
    def test_generated_assets_exist(self):
        for rel in ("assets/cursors/fibra-seta.png", "assets/cursors/fibra-seta@2x.png",
                    "assets/cursors/fibra-mao.png", "assets/cursors/fibra-mao@2x.png"):
            path = ROOT / rel
            self.assertTrue(path.exists(), rel)
            self.assertEqual(path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n", rel)

    def test_font_files_declared_in_typography_exist(self):
        source = (ROOT / "typography.py").read_text(encoding="utf-8")
        for name in re.findall(r'"((?:IBMPlex|Dropline|Arena)[A-Za-z-]*\.(?:ttf|otf))"', source):
            self.assertTrue((ROOT / "assets" / "fonts" / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
