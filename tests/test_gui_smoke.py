"""
Teste gráfico de fumaça: abre widgets de verdade (sem janela visível) e confere o essencial da
nova interface. Precisa de PyQt5; sem ele os testes são pulados.

Executar na raiz do repositório (no Codespace não precisa de monitor):

    QT_QPA_PLATFORM=offscreen python3 -m unittest tests.test_gui_smoke -v
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["SPECTRUM_LAB_DATA_DIR"] = tempfile.mkdtemp(prefix="spectrum-test-")   # não mexe nas preferências reais
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from PyQt5.QtCore import QAbstractAnimation, QPoint, Qt
    from PyQt5.QtGui import QFontDatabase
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QVBoxLayout, QWidget
    HAVE_QT = True
except ImportError:   # pragma: no cover
    HAVE_QT = False

import analysis_messages as messages  # noqa: E402


def distinct_pixels(pixmap, step_x=23, step_y=7):
    image = pixmap.toImage()
    return {image.pixel(x, y) for x in range(0, image.width(), step_x) for y in range(0, image.height(), step_y)}


@unittest.skipUnless(HAVE_QT, "PyQt5 não instalado")
class GuiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv[:1])
        cls.app.setStyle("Fusion")
        from appearance import ensure_theme_manager
        cls.manager = ensure_theme_manager()

    def pump(self):
        self.app.processEvents()

    def test_embedded_fonts_are_registered(self):
        families = set(QFontDatabase().families())
        for family in ("IBM Plex Sans", "EB Garamond", "IBM Plex Mono"):
            self.assertIn(family, families)

    def test_font_styles_are_regular_and_bold_only(self):
        """Diagnóstico: cada família deve ter só os estilos Regular/Bold (e Italic na Garamond).

        Se aparecer outro estilo (Medium, SemiBold), o Windows pode registrá-lo como família separada
        e a pilha de fontes deixa de se comportar como esperado."""
        db = QFontDatabase()
        allowed = {"Regular", "Bold", "Italic", "Normal", "Bold Italic"}
        for family in ("IBM Plex Sans", "EB Garamond", "IBM Plex Mono"):
            styles = set(db.styles(family))
            self.assertTrue(styles, family)
            self.assertLessEqual(styles, allowed, f"{family}: estilos inesperados {sorted(styles - allowed)}")

    def test_cursor_images_load(self):
        import cursors
        for name in (cursors.ARROW, cursors.HAND):
            cursor = cursors.load_cursor(name)
            self.assertIsNotNone(cursor, name)
            self.assertEqual(cursor.shape(), Qt.BitmapCursor)

    def test_buttons_and_windows_get_the_cellulose_cursor(self):
        import cursors
        if not cursors.enabled():
            self.skipTest("SPECTRUM_SYSTEM_CURSOR=1")
        button = QPushButton("Teste")
        button.show()
        self.pump()
        self.assertEqual(button.cursor().shape(), Qt.BitmapCursor)
        button.close()

    def test_only_two_themes_exist(self):
        from appearance import PALETTES
        self.assertEqual(set(PALETTES), {"umber", "light"})
        with self.assertRaises(ValueError):
            self.manager.set_theme("dark", persist=False)

    def test_theme_switch_updates_the_application(self):
        for theme in ("light", "umber"):
            self.manager.set_theme(theme, persist=False)
            self.assertEqual(self.app.property("spectrum_theme"), theme)

    def test_canvas_root_paints_the_cellulose_texture(self):
        import scada_ui
        for theme in ("umber", "light"):
            self.manager.set_theme(theme, persist=False)
            root = scada_ui.CanvasRoot()
            root.resize(420, 300)
            pixmap = root.grab()
            self.assertGreater(len(distinct_pixels(pixmap, 5, 5)), 1, f"textura invisível no tema {theme}")

    def test_legacy_theme_names_migrate_to_umber(self):
        from appearance import LEGACY_THEMES
        self.assertEqual(LEGACY_THEMES.get("dark"), "umber")
        self.assertEqual(LEGACY_THEMES.get("gold"), "umber")

    def test_glass_panels_show_the_texture_through(self):
        """O cartão é translúcido: renderizado sobre a textura, não pode ser uma cor chapada."""
        import scada_ui
        self.manager.set_theme("umber", persist=False)
        root = scada_ui.CanvasRoot()
        layout = QVBoxLayout(root)
        box = scada_ui.panel()
        layout.addWidget(box)
        root._scada_style_factory = scada_ui.dashboard_style
        root.resize(420, 300)
        root.show()
        self.manager.apply_widget(root)
        self.pump()
        self.assertGreater(len(distinct_pixels(box.grab(), 5, 5)), 1, "painel opaco: a textura não aparece")
        root.close()

    def test_analysis_indicator_renders_every_state(self):
        from analysis_indicator import AnalysisIndicator
        for theme in ("umber", "light"):
            self.manager.set_theme(theme, persist=False)
            for state in messages.known_states():
                indicator = AnalysisIndicator(lambda s=state: s)
                indicator.resize(900, 92)
                indicator.show()
                indicator.refresh()
                pixmap = indicator.grab()
                self.assertFalse(pixmap.isNull(), state)
                self.assertGreater(len(distinct_pixels(pixmap, 37, 11)), 3, (theme, state))
                indicator.hide()

    def test_indicator_celebrates_after_a_finished_cycle(self):
        from analysis_indicator import AnalysisIndicator
        current = {"state": "AUTO_ABRINDO_GAVETA"}
        indicator = AnalysisIndicator(lambda: current["state"])
        indicator.resize(900, 92)
        indicator.show()
        indicator.refresh()
        current["state"] = "IDLE"
        indicator.refresh()
        self.assertTrue(indicator.celebrating)
        self.assertEqual(indicator.current_text()[0], "Análise concluída")

    def test_buttons_get_the_effect_layer_and_ripple(self):
        button = QPushButton("Teste")
        button.resize(160, 44)
        button.show()
        self.pump()
        overlay = getattr(button, "_fx_overlay", None)
        self.assertIsNotNone(overlay)
        QTest.mousePress(button, Qt.LeftButton, Qt.NoModifier, QPoint(30, 20))
        self.pump()
        self.assertEqual(overlay.ripple_anim.state(), QAbstractAnimation.Running)
        QTest.mouseRelease(button, Qt.LeftButton, Qt.NoModifier, QPoint(30, 20))
        self.assertFalse(button.grab().isNull())

    def test_busy_shimmer_runs_even_when_button_is_disabled(self):
        button = QPushButton("Realizar leitura")
        button.resize(200, 44)
        button.show()
        self.pump()
        button.setEnabled(False)
        button.setProperty("fxBusy", True)
        self.pump()
        self.assertTrue(button._fx_overlay.busy_timer.isActive())
        button.setProperty("fxBusy", False)
        self.pump()
        self.assertFalse(button._fx_overlay.busy_timer.isActive())

    def test_numeric_keyboard_types_an_ip_address(self):
        host = QWidget()
        layout = QVBoxLayout(host)
        field = QLineEdit()
        field.setProperty("touchKeyboard", "numeric")
        layout.addWidget(field)
        host.resize(400, 120)
        host.show()
        field.setFocus()
        self.pump()
        keyboard = self.manager.keyboard._window()
        keyboard.open_for(field)
        self.pump()
        self.assertTrue(keyboard.isVisible())

        def key(text):
            return next(b for b in keyboard.findChildren(QPushButton) if b.text() == text)

        for char in "192.168.4.1":
            key(char).click()
        self.assertEqual(field.text(), "192.168.4.1")
        key("Apagar").click()
        self.assertEqual(field.text(), "192.168.4.")
        key("Limpar").click()
        self.assertEqual(field.text(), "")
        keyboard.hide()
        host.close()

    def test_digits_keyboard_has_no_dot(self):
        host = QWidget()
        field = QLineEdit(host)
        field.setProperty("touchKeyboard", "digits")
        host.resize(300, 100)
        host.show()
        self.pump()
        keyboard = self.manager.keyboard._window()
        keyboard.open_for(field)
        self.pump()
        self.assertNotIn(".", [b.text() for b in keyboard.findChildren(QPushButton)])
        keyboard.hide()
        host.close()

    def test_keyboard_can_be_turned_off(self):
        self.manager.set_touch_keyboard(False)
        self.assertFalse(self.manager.keyboard.enabled)
        self.manager.set_touch_keyboard(True)
        self.assertTrue(self.manager.keyboard.enabled)


if __name__ == "__main__":
    unittest.main()
