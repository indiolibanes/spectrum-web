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

    def test_night_theme_is_dark_and_purple(self):
        p = self.palettes["noturno"]
        self.assertTrue(glass.is_dark(p))
        self.assertFalse(glass.is_dark(self.palettes["light"]))
        r, g, b = glass._channels(p["canvas"])
        self.assertTrue(b >= r > g, "o fundo do noturno é roxo-escuro")
        r, g, b = glass._channels(p["secondary"])
        self.assertTrue(b > g and r > g, "a secundária do noturno é roxa")

    def test_night_accent_is_gold(self):
        p = self.palettes["noturno"]
        r, g, b = glass._channels(p["accent"])
        self.assertTrue(r > g > b and r > 200, "o destaque do noturno é dourado")

    def test_light_theme_uses_distinct_greens(self):
        p = self.palettes["light"]
        greens = {p["accent"], p["positive"], p["secondary"]}
        self.assertEqual(len(greens), 3)
        for color in greens:
            r, g, b = glass._channels(color)
            self.assertRegex(color, r"^#[0-9A-Fa-f]{6}$")

    def test_alarm_colors_are_not_used_as_button_or_identity_colors(self):
        """ISA-101: vermelho e laranja são de alarme. Tons de função não podem ter esse matiz.
        O ouro (accent) é a cor de foco e identidade do noturno, não de alarme; fica de fora do teste."""
        import colorsys
        for name, p in self.palettes.items():
            for tone in ("secondary", "sky", "violet", "rose", "slate", "sand"):
                r, g, b = (c / 255 for c in glass._channels(p[tone]))
                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                if s > 0.30:
                    self.assertFalse(h * 360 < 40 or h * 360 > 335, (name, tone, round(h * 360)))

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


class TranslucencyAndNeutralButtonTests(unittest.TestCase):
    """Fundo e painéis translúcidos; botões neutros (sem cor por função, sem fio de luz)."""

    def setUp(self):
        self.palettes = load_palettes()

    def test_rgba_format_and_clamp(self):
        self.assertEqual(glass.rgba("#FF8000", 0.5), "rgba(255, 128, 0, 50%)")
        self.assertEqual(glass.rgba("#000000", 2), "rgba(0, 0, 0, 100%)")
        self.assertEqual(glass.rgba("#000000", -1), "rgba(0, 0, 0, 0%)")

    def test_every_fill_is_a_valid_qss_color(self):
        for p in self.palettes.values():
            values = [glass.panel_fill(p), glass.result_fill(p), glass.field_fill(p), glass.rim(p), glass.rim(p, 1.5)]
            values += [glass.primary_fill(p, s) for s in ("rest", "hover", "hot")]
            values += [glass.button_fill(p, s) for s in ("rest", "hover", "disabled")]
            for value in values:
                self.assertTrue(value.startswith("rgba(") or re.match(r"^#[0-9A-Fa-f]{6}$", value), value)

    def test_panels_are_translucent_in_both_themes(self):
        for name, p in self.palettes.items():
            alpha = float(re.search(r", (\d+)%\)", glass.panel_fill(p)).group(1))
            self.assertLess(alpha, 75, name)
            self.assertGreater(alpha, 30, name)

    def test_background_has_glows_for_the_translucency_to_show(self):
        for p in self.palettes.values():
            spec = glass.glow_spec(p)
            self.assertGreaterEqual(len(spec), 2)
            for x, y, radius, color, alpha in spec:
                self.assertTrue(0 <= x <= 1 and 0 <= y <= 1)
                self.assertTrue(0 < radius <= 1.2)
                self.assertTrue(0 < alpha < 0.35)
                self.assertRegex(color, r"^#[0-9A-Fa-f]{6}$")

    def test_no_gradient_helper_and_no_edge_light(self):
        self.assertFalse(hasattr(glass, "vgrad"))
        for p in self.palettes.values():
            self.assertEqual(glass.edge_highlight(p)[1], 0)

    def test_no_texture_in_any_theme(self):
        source = (ROOT / "appearance.py").read_text(encoding="utf-8")
        self.assertIn("TEXTURE_FILES={}", source)

    def test_buttons_are_neutral_for_every_function(self):
        """Cada função tem a mesma cor de botão: a cor fica nos gráficos, não nos botões."""
        for p in self.palettes.values():
            for tone in glass.TONES:
                self.assertEqual(glass.tone_fill(p, tone), glass.button_fill(p))
                self.assertEqual(glass.tone_text(p, tone), p["text"])

    def test_primary_button_is_neutral_and_readable(self):
        for p in self.palettes.values():
            self.assertEqual(glass.primary_fill(p), p["text"])
            self.assertGreater(contrast(p["on_strong"], p["text"]), 4.5)

    def test_secondary_buttons_are_visible(self):
        for p in self.palettes.values():
            self.assertTrue(glass.button_fill(p).startswith("rgba("))


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
