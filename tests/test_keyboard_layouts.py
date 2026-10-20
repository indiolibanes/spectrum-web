"""Testes do teclado na tela (sem Qt). Executar: python3 -I tests/test_keyboard_layouts.py"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import keyboard_layouts as kl  # noqa: E402

EMOJI = re.compile(r"[\U0001F000-\U0001FAFF⌀-⏿▶☀-➿️‍]")


def flat(rows):
    return [key for row in rows for key in row]


def all_layouts():
    for kind in kl.KINDS:
        if kind == "full":
            for layer in kl.LAYERS:
                for shift in (False, True):
                    yield kind, layer, shift
        else:
            yield kind, "letters", False


class LayoutTests(unittest.TestCase):
    def test_every_layout_has_enter_and_backspace(self):
        for kind, layer, shift in all_layouts():
            kinds = {k.kind for k in flat(kl.layout_for(kind, layer, shift))}
            self.assertIn("enter", kinds, (kind, layer))
            self.assertTrue({"backspace"} <= kinds, (kind, layer))

    def test_valid_key_kinds_and_text(self):
        for kind, layer, shift in all_layouts():
            for key in flat(kl.layout_for(kind, layer, shift)):
                self.assertIn(key.kind, kl.KEY_KINDS)
                self.assertGreater(key.weight, 0)
                if key.kind == "char":
                    self.assertEqual(len(key.value), 1, key)
                    self.assertEqual(key.label, key.value)
                if key.kind != "spacer":
                    self.assertTrue(key.label.strip(), key)
                self.assertFalse(EMOJI.search(key.label), key)

    def test_numeric_has_each_digit_once_and_dot(self):
        values = [k.value for k in flat(kl.layout_for("numeric")) if k.kind == "char"]
        for digit in "0123456789":
            self.assertEqual(values.count(digit), 1, digit)
        self.assertIn(".", values)

    def test_digits_has_no_dot(self):
        values = [k.value for k in flat(kl.layout_for("digits")) if k.kind == "char"]
        self.assertNotIn(".", values)
        self.assertEqual(sorted(values), list("0123456789"))

    def test_numeric_can_type_an_ip_and_move_cursor(self):
        kinds = {k.kind for k in flat(kl.layout_for("numeric"))}
        self.assertTrue({"left", "right", "clear"} <= kinds)

    def test_letters_cover_alphabet_and_cedilla(self):
        values = {k.value for k in flat(kl.layout_for("full", "letters"))}
        for c in "abcdefghijklmnopqrstuvwxyzç0123456789":
            self.assertIn(c, values)

    def test_shift_uppercases_letters_only(self):
        values = {k.value for k in flat(kl.layout_for("full", "letters", True))}
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZÇ0123456789":
            self.assertIn(c, values)
        self.assertNotIn("a", values)

    def test_symbols_cover_common_password_characters(self):
        values = {k.value for k in flat(kl.layout_for("full", "symbols"))}
        for c in "!@#$%&*()-_+=.,:;/?'\"":
            if c in ".,":
                continue   # ponto e vírgula ficam na camada de letras
            self.assertIn(c, values, c)
        letters = {k.value for k in flat(kl.layout_for("full", "letters"))}
        self.assertTrue({".", ","} <= letters)

    def test_accents_layer_has_portuguese_vowels(self):
        values = {k.value for k in flat(kl.layout_for("full", "accents"))}
        for c in "áàâãéêíóôõúç":
            self.assertIn(c, values, c)

    def test_layers_are_reachable_both_ways(self):
        targets = {k.value for k in flat(kl.layout_for("full", "letters")) if k.kind == "layer"}
        self.assertEqual(targets, {"symbols", "accents"})
        for layer in ("symbols", "accents"):
            back = {k.value for k in flat(kl.layout_for("full", layer)) if k.kind == "layer"}
            self.assertIn("letters", back)

    def test_space_is_the_widest_key(self):
        row = kl.layout_for("full", "letters")[-1]
        space = next(k for k in row if k.kind == "space")
        self.assertEqual(max(k.weight for k in row), space.weight)


class ResolveTests(unittest.TestCase):
    def test_property_wins(self):
        self.assertEqual(kl.resolve_kind("numeric"), "numeric")
        self.assertEqual(kl.resolve_kind("digits", inside_spin_box=False), "digits")

    def test_spin_box_defaults_to_numeric(self):
        self.assertEqual(kl.resolve_kind(None, inside_spin_box=True), "numeric")
        self.assertEqual(kl.resolve_kind(None), "full")
        self.assertEqual(kl.resolve_kind("qualquer"), "full")


class PlacementTests(unittest.TestCase):
    SCREEN = (0, 0, 1920, 1080)

    def test_prefers_the_top_left_corner(self):
        x, y = kl.compute_position((900, 400, 150, 36), self.SCREEN, (300, 248))
        self.assertEqual((x, y), (14, 14))

    def test_steps_below_the_field_when_the_corner_would_cover_it(self):
        field = (100, 40, 200, 40)
        x, y = kl.compute_position(field, self.SCREEN, (300, 248))
        self.assertEqual(x, 14)
        self.assertEqual(y, 40 + 40 + 14)

    def test_never_covers_the_field(self):
        for fy in range(0, 1040, 40):
            for fx in (20, 300, 900):
                field = (fx, fy, 160, 40)
                x, y = kl.compute_position(field, self.SCREEN, (300, 248))
                overlap_y = not (y + 248 <= fy or fy + 40 <= y)
                overlap_x = not (x + 300 <= fx or fx + 160 <= x)
                self.assertFalse(overlap_x and overlap_y, (fx, fy, x, y))

    def test_stays_inside_the_screen(self):
        for fy in range(0, 1040, 80):
            for size in ((300, 248), (660, 292)):
                x, y = kl.compute_position((900, fy, 160, 40), self.SCREEN, size)
                self.assertTrue(0 <= x and x + size[0] <= 1920 and 0 <= y and y + size[1] <= 1080, (fy, size, x, y))

    def test_size_is_compact_and_fits_small_screens(self):
        w, h = kl.keyboard_size("full", 1024, 600)
        self.assertLessEqual(w, 1024)
        self.assertLessEqual(h, 300)
        self.assertEqual(kl.keyboard_size("numeric", 1920, 1080), (300, 248))
        self.assertLessEqual(kl.keyboard_size("full", 1920, 1080)[0], 700)


if __name__ == "__main__":
    unittest.main()
