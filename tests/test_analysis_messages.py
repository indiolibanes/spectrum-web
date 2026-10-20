"""Testes das fases e mensagens de análise (sem Qt). Executar: python3 -I tests/test_analysis_messages.py"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analysis_messages as am  # noqa: E402

# O ThemeManager remove estes intervalos de qualquer rótulo; as frases não podem depender deles.
EMOJI = re.compile(r"[\U0001F000-\U0001FAFF⌀-⏿▶☀-➿️‍]")


class PhaseTests(unittest.TestCase):
    def test_every_known_state_has_a_phase(self):
        for state in am.known_states():
            phase = am.phase_for(state)
            self.assertIn(phase.kind, am.MESSAGES, state)
            self.assertTrue(phase.title, state)
            self.assertIn(phase.mood, ("smile", "calm", "alert"), state)

    def test_steps_in_range(self):
        for state in am.known_states():
            phase = am.phase_for(state)
            if phase.step:
                self.assertEqual(phase.total, am.TOTAL_STEPS, state)
                self.assertTrue(1 <= phase.step <= am.TOTAL_STEPS, state)
            else:
                self.assertEqual(phase.total, 0, state)

    def test_auto_sequence_is_ordered(self):
        order = ["AUTO_FECHANDO_GAVETA", "AUTO_AVANCANDO_SENSOR", "AUTO_LENDO_ESPECTRO",
                 "AUTO_RECUANDO_SENSOR", "AUTO_ABRINDO_GAVETA"]
        self.assertEqual([am.phase_for(s).step for s in order], [1, 2, 3, 4, 5])

    def test_calibration_titles_distinguish_white_and_dark(self):
        self.assertIn("branco", am.phase_for("CALIB_ETAPA1_LENDO_ESPECTRO").title)
        self.assertIn("escura", am.phase_for("CALIB_ETAPA2_LENDO_ESPECTRO").title)

    def test_reading_is_busy_and_idle_is_not(self):
        self.assertTrue(am.phase_for("AUTO_LENDO_ESPECTRO").busy)
        self.assertFalse(am.phase_for("IDLE").busy)
        self.assertFalse(am.phase_for("AGUARDANDO_POPUP").busy)

    def test_alerts_are_serious(self):
        self.assertEqual(am.phase_for("EMERGENCIA").mood, "alert")
        self.assertEqual(am.phase_for("FALHA").mood, "alert")

    def test_unknown_and_empty_do_not_crash(self):
        self.assertEqual(am.phase_for(None).kind, "idle")
        self.assertEqual(am.phase_for("").kind, "idle")
        self.assertTrue(am.phase_for("ESTADO_NOVO").title)
        self.assertEqual(am.phase_for("auto_lendo_espectro").kind, "reading")


class MessageTests(unittest.TestCase):
    def test_no_emoji_and_not_empty(self):
        for kind, options in am.MESSAGES.items():
            self.assertTrue(options, kind)
            for text in options:
                self.assertTrue(text.strip(), kind)
                self.assertFalse(EMOJI.search(text), text)
                self.assertLessEqual(len(text), 110, text)

    def test_every_kind_has_a_mood(self):
        self.assertEqual(set(am.MESSAGES), set(am.KIND_MOOD))

    def test_rotation_wraps(self):
        phase = am.phase_for("AUTO_LENDO_ESPECTRO")
        n = len(phase.messages)
        self.assertEqual(am.message_for(phase, 0), am.message_for(phase, n))
        self.assertNotEqual(am.message_for(phase, 0), am.message_for(phase, 1))

    def test_happy_phases_smile(self):
        self.assertEqual(am.phase_for("IDLE").mood, "smile")
        self.assertTrue(any("Boa amostra" in t for t in am.MESSAGES["done"]))


class FinishedTests(unittest.TestCase):
    def test_finished_after_operation(self):
        self.assertTrue(am.finished("AUTO_ABRINDO_GAVETA", "IDLE"))
        self.assertTrue(am.finished("CONCLUSAO_FECHANDO_GAVETA", "IDLE"))

    def test_not_finished_for_idle_fault_cancel(self):
        self.assertFalse(am.finished("IDLE", "IDLE"))
        self.assertFalse(am.finished("FALHA", "IDLE"))
        self.assertFalse(am.finished("EMERGENCIA", "IDLE"))
        self.assertFalse(am.finished("CANCELANDO_FECHANDO_GAVETA", "IDLE"))
        self.assertFalse(am.finished("CALIB_CANCELANDO_FECHANDO_GAVETA", "IDLE"))
        self.assertFalse(am.finished("AUTO_LENDO_ESPECTRO", "AUTO_RECUANDO_SENSOR"))


if __name__ == "__main__":
    unittest.main()
