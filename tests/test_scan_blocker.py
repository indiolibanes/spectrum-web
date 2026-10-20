"""Motivo exibido quando 'Realizar leitura' não pode começar (função pura, sem Qt).

python3 -I tests/test_scan_blocker.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis_messages import scan_blocker  # noqa: E402

READY = dict(connected=True, protocol_ready=True, sensor_ready=True, equipment_ready=True,
             equipment_known=True, busy=False, calibration_valid=True)


class ScanBlockerTest(unittest.TestCase):
    def test_pronto_quando_tudo_confirmado(self):
        self.assertIsNone(scan_blocker(**READY))

    def test_sem_conexao_orienta_a_conectar_e_o_simulador(self):
        text = scan_blocker(**{**READY, "connected": False})
        self.assertIn("Conecte", text)
        self.assertIn("127.0.0.1", text)

    def test_firmware_sem_protocolo_de_porta_e_carrinho_pede_atualizacao(self):
        self.assertIn("firmware", scan_blocker(**{**READY, "equipment_ready": False}).lower())

    def test_calibracao_ausente_pede_calibrar(self):
        text = scan_blocker(**{**READY, "calibration_valid": False})
        self.assertIn("Calibrar", text)

    def test_erro_de_calibracao_tem_prioridade_sobre_o_texto_padrao(self):
        text = scan_blocker(**{**READY, "calibration_valid": False, "calibration_error": "Branco expirado"})
        self.assertEqual(text, "Branco expirado")

    def test_ordem_dos_motivos(self):
        # Sem conexão, o motivo é a conexão, mesmo que a calibração também esteja faltando.
        text = scan_blocker(**{**READY, "connected": False, "calibration_valid": False})
        self.assertIn("Conecte", text)

    def test_equipamento_em_movimento_bloqueia(self):
        self.assertIn("movimento", scan_blocker(**{**READY, "busy": True}))


if __name__ == "__main__":
    unittest.main()
