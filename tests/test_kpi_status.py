"""Estado dos indicadores, temperaturas e marcas dos gráficos (sem Qt).

python3 -I tests/test_kpi_status.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import kpi_status as ks  # noqa: E402

GOOD = [12000, 18000, 21000, 19000, 15000, 11000]
SNV = [0.12, 0.18, 0.21, 0.19, 0.15, 0.11]


class EvaluateTest(unittest.TestCase):
    def test_sem_leitura(self):
        for kind in ks.KINDS:
            self.assertEqual(ks.evaluate(kind, None).level, ks.NONE)
            self.assertEqual(ks.evaluate(kind, [1, 2, 3]).level, ks.NONE)

    def test_leitura_boa_e_normal(self):
        for kind, status in ks.evaluate_all(GOOD, SNV).items():
            self.assertEqual(status.level, ks.OK, kind)

    def test_saturacao_e_erro_e_aponta_o_canal(self):
        raw = [12000, 65500, 21000, 19000, 15000, 11000]
        for kind in ("energy", "peak"):
            status = ks.evaluate(kind, raw, SNV)
            self.assertEqual(status.level, ks.ERROR)
            self.assertEqual(status.channels, (1,))
            self.assertIn("680 nm", status.headline)

    def test_perto_da_saturacao_e_atencao(self):
        raw = [12000, 60000, 21000, 19000, 15000, 11000]
        self.assertEqual(ks.evaluate("energy", raw, SNV).level, ks.ATTENTION)

    def test_sinal_baixo_e_erro(self):
        self.assertEqual(ks.evaluate("energy", [10, 20, 30, 40, 50, 60], SNV).level, ks.ERROR)

    def test_espectro_plano_e_atencao_no_pico(self):
        flat = [10000, 10100, 10050, 10020, 10080, 10010]
        self.assertEqual(ks.evaluate("peak", flat, SNV).level, ks.ATTENTION)
        self.assertEqual(ks.evaluate("energy", flat, SNV).level, ks.OK)

    def test_pico_informa_o_comprimento_de_onda(self):
        self.assertEqual(ks.evaluate("peak", GOOD, SNV).headline, "Pico em 730 nm.")

    def test_razoes_fora_da_faixa_sao_atencao(self):
        snv = [0.02, 0.5, 0.05, 0.19, 0.15, 0.11]   # R680/R730 = 10
        self.assertEqual(ks.evaluate("ratio_cel", GOOD, snv).level, ks.ATTENTION)
        self.assertEqual(ks.evaluate("ratio_water", GOOD, SNV).level, ks.OK)

    def test_razao_indefinida_e_erro(self):
        snv = [0.12, 0.0, 0.21, 0.19, 0.15, 0.11]
        status = ks.evaluate("ratio_cel", GOOD, snv)
        self.assertEqual(status.level, ks.ERROR)
        self.assertEqual(ks.evaluate("ratio_cel", GOOD, None).level, ks.ERROR)
        self.assertIsNone(ks.ratio_value("ratio_cel", snv))

    def test_valor_da_razao(self):
        self.assertAlmostEqual(ks.ratio_value("ratio_cel", SNV), 0.18 / 0.21)
        self.assertAlmostEqual(ks.ratio_value("ratio_water", SNV), 0.11 / 0.19)

    def test_valor_invalido(self):
        self.assertEqual(ks.evaluate("energy", [1, 2, float("nan"), 4, 5, 6]).level, ks.ERROR)

    def test_indicador_desconhecido(self):
        with self.assertRaises(ValueError):
            ks.evaluate("outro", GOOD, SNV)

    def test_todo_nivel_tem_rotulo_e_cor(self):
        for level in (ks.NONE, ks.OK, ks.ATTENTION, ks.ERROR):
            self.assertIn(level, ks.LEVEL_LABEL)
            self.assertIn(level, ks.LEVEL_COLOR_KEY)


class TemperatureTest(unittest.TestCase):
    def test_faixas_do_esp32(self):
        self.assertEqual(ks.temperature_level("esp32", 5), ks.COLD)
        self.assertEqual(ks.temperature_level("esp32", 42), ks.OK)
        self.assertEqual(ks.temperature_level("esp32", 60), ks.OK)
        self.assertEqual(ks.temperature_level("esp32", 61), ks.ATTENTION)
        self.assertEqual(ks.temperature_level("esp32", 76), ks.ERROR)

    def test_faixas_do_sensor_sao_mais_estreitas(self):
        self.assertEqual(ks.temperature_level("sensor", 55), ks.ATTENTION)
        self.assertEqual(ks.temperature_level("esp32", 55), ks.OK)

    def test_valores_invalidos(self):
        for bad in (None, "x", float("nan"), float("inf")):
            self.assertEqual(ks.temperature_level("sensor", bad), ks.NONE)

    def test_todo_nivel_tem_cor_e_rotulo(self):
        for level in (ks.NONE, ks.COLD, ks.OK, ks.ATTENTION, ks.ERROR):
            self.assertIn(level, ks.THERMAL_COLOR_KEY)
            self.assertIn(level, ks.THERMAL_LABEL)


class TicksTest(unittest.TestCase):
    def test_marcas_redondas(self):
        self.assertEqual(ks.nice_ticks(0, 100, 5), [0, 20, 40, 60, 80, 100])
        self.assertEqual(ks.nice_ticks(0, 65500, 5), [0, 20000, 40000, 60000])
        self.assertEqual(ks.nice_ticks(0, 3, 6), [0, 0.5, 1, 1.5, 2, 2.5, 3])

    def test_intervalo_invalido(self):
        self.assertEqual(ks.nice_ticks(5, 5), [5.0])
        self.assertEqual(ks.nice_ticks(0, float("nan")), [0.0])


if __name__ == "__main__":
    unittest.main()
