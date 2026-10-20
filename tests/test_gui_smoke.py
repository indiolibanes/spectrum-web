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
    from PyQt5.QtGui import QFontDatabase, QFontInfo
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QVBoxLayout, QWidget
    HAVE_QT = True
except ImportError:   # pragma: no cover
    HAVE_QT = False

import analysis_messages as messages  # noqa: E402
import responsive_math  # noqa: E402,F401


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

    def test_canvas_root_paints_the_cellulose_texture_only_in_light(self):
        import scada_ui
        from appearance import TEXTURE_FILES
        self.assertNotIn("umber", TEXTURE_FILES, "o Escuro é preto liso, sem textura")
        self.manager.set_theme("light", persist=False)
        root = scada_ui.CanvasRoot()
        root.resize(420, 300)
        self.assertGreater(len(distinct_pixels(root.grab(), 5, 5)), 1, "textura invisível no tema claro")
        self.manager.set_theme("umber", persist=False)
        root = scada_ui.CanvasRoot()
        root.resize(420, 300)
        self.assertEqual(len(distinct_pixels(root.grab(), 5, 5)), 1, "fundo do Escuro deve ser preto liso")

    def test_legacy_theme_names_migrate_to_umber(self):
        from appearance import LEGACY_THEMES
        self.assertEqual(LEGACY_THEMES.get("dark"), "umber")
        self.assertEqual(LEGACY_THEMES.get("gold"), "umber")

    def test_glass_panels_show_the_texture_through(self):
        """O cartão é translúcido: renderizado sobre a textura, não pode ser uma cor chapada."""
        import scada_ui
        self.manager.set_theme("light", persist=False)
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
        self.manager.set_theme("umber", persist=False)

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


    # ---- Configurações: aparência e acessibilidade em seções separadas
    def _dialog(self):
        from appearance import AppearanceDialog
        dialog = AppearanceDialog(self.manager)
        dialog.show()
        self.pump()
        return dialog

    def test_settings_separates_appearance_from_accessibility(self):
        from PyQt5.QtWidgets import QComboBox, QFrame
        dialog = self._dialog()
        sections = [f for f in dialog.findChildren(QFrame) if f.objectName() == "settingsSection"]
        self.assertEqual(len(sections), 2)
        appearance_section, access_section = sections
        # o tema fica só na primeira seção; teclado e animações só na segunda
        for button in dialog.theme_buttons.values():
            self.assertTrue(appearance_section.isAncestorOf(button))
            self.assertFalse(access_section.isAncestorOf(button))
        for combo in (dialog.keyboard_selector, dialog.motion_selector):
            self.assertIsInstance(combo, QComboBox)
            self.assertTrue(access_section.isAncestorOf(combo))
            self.assertFalse(appearance_section.isAncestorOf(combo))
        dialog.close()

    def test_settings_theme_buttons_switch_theme(self):
        dialog = self._dialog()
        dialog.theme_buttons["light"].click()
        self.assertEqual(self.manager.theme, "light")
        self.assertTrue(dialog.theme_buttons["light"].isChecked())
        self.assertFalse(dialog.theme_buttons["umber"].isChecked())
        dialog.theme_buttons["umber"].click()
        self.assertEqual(self.manager.theme, "umber")
        dialog.close()

    def test_reduce_motion_option(self):
        import motion
        dialog = self._dialog()
        dialog.motion_selector.setCurrentIndex(1)
        self.assertTrue(self.manager.reduce_motion)
        self.assertTrue(motion.reduced())
        dialog.motion_selector.setCurrentIndex(0)
        self.assertFalse(self.manager.reduce_motion)
        self.assertFalse(motion.reduced())
        dialog.close()

    def test_theme_switch_with_crossfade_leaves_no_overlay_behind(self):
        from PyQt5.QtWidgets import QWidget
        host = QWidget()
        host.resize(300, 200)
        host.show()
        self.pump()
        before = len(host.findChildren(QWidget))
        self.manager.set_theme("light", persist=False)
        self.manager.set_theme("umber", persist=False)
        QTest.qWait(700)
        self.assertEqual(len(host.findChildren(QWidget)), before)
        host.close()

    def test_press_effect_honors_reduced_motion(self):
        import motion
        motion.set_reduced(True)
        try:
            button = QPushButton("Teste")
            button.resize(160, 44)
            button.show()
            self.pump()
            QTest.mousePress(button, Qt.LeftButton, Qt.NoModifier, QPoint(30, 20))
            self.pump()
            self.assertEqual(button._fx_overlay.spring_anim.state(), QAbstractAnimation.Stopped)
            QTest.mouseRelease(button, Qt.LeftButton, Qt.NoModifier, QPoint(30, 20))
        finally:
            motion.set_reduced(False)

    # ---- Legibilidade e vetores coloridos
    def test_colored_faces_and_glyphs_paint_in_both_themes(self):
        import emoji_icons
        for theme in ("umber", "light"):
            self.manager.set_theme(theme, persist=False)
            for kind in ("bolt", "trend", "leaf", "drop"):
                icon = emoji_icons.GlyphIcon(kind, 28)
                icon.show()
                self.assertGreater(len(distinct_pixels(icon.grab(), 3, 3)), 3, (theme, kind))
        self.manager.set_theme("umber", persist=False)

    def test_calibration_card_has_no_compressed_text(self):
        try:
            from main import CardKpiCalibracao
        except Exception as error:   # importar o main exige as dependências do equipamento
            self.skipTest(f"main não importável aqui: {error}")
        for theme in ("umber", "light"):
            self.manager.set_theme(theme, persist=False)
            card = CardKpiCalibracao()
            card.resize(330, 220)
            card.show()
            self.manager.apply_widget(card)
            self.pump()
            for label in (card.lbl_r2, card.lbl_rmse, card.lbl_n):
                self.assertGreaterEqual(QFontInfo(label.font()).pixelSize(), 12, (theme, label.text()))
                self.assertLessEqual(label.sizeHint().width(), label.width() + 1, (theme, label.text()))
            card.close()
        self.manager.set_theme("umber", persist=False)

    def test_credits_link_to_the_authors_github(self):
        import version
        html = version.credits_html("#D4A84B")
        self.assertIn("github.com/indiolibanes", html)
        self.assertIn("github.com/yosemate", html)
        self.assertIn("Kauê Carvalho", html)
        self.assertIn("Mateus Ferreira", html)

    def test_chart_bars_get_one_color_per_band(self):
        from animated_chart import SingleBarWidget
        from appearance import series_colors
        colors = []
        for index in range(len(series_colors())):
            bar = SingleBarWidget("450nm", "#087D7B", "Azul")
            bar.series_index = index
            colors.append(bar.band_color())
        self.assertEqual(len(set(colors)), len(colors))

    def test_adaptive_canvas_never_clips_the_layout_minimum(self):
        from responsive_layout import ScaledCanvasView
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.addWidget(QPushButton("Ação"))
        content.setMinimumSize(900, 520)
        for size in ((800, 1280), (1024, 600), (1366, 768), (1920, 1080)):
            view = ScaledCanvasView(content, parent=None, adaptive=True)
            view.resize(*size)
            view.show()
            self.pump()
            self.assertGreaterEqual(content.width(), 900)
            self.assertGreaterEqual(content.height(), 520)
            view.close()


if __name__ == "__main__":
    unittest.main()
