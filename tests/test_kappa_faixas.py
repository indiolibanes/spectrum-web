"""Faixas demonstrativas do Kappa (modelo experimental): fronteiras e valores inválidos."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chemometrics import classify_experimental_kappa  # noqa: E402


class KappaFaixasTest(unittest.TestCase):
    def test_fronteiras_pertencem_a_faixa_inferior(self):
        self.assertEqual(classify_experimental_kappa(2)[0], "Faixa 1 — até 2")
        self.assertEqual(classify_experimental_kappa(6)[0], "Faixa 2 — acima de 2 até 6")
        self.assertEqual(classify_experimental_kappa(12)[0], "Faixa 3 — acima de 6 até 12")
        self.assertEqual(classify_experimental_kappa(22)[0], "Faixa 4 — acima de 12 até 22")
        self.assertEqual(classify_experimental_kappa(55)[0], "Faixa 5 — acima de 22 até 55")

    def test_acima_de_55_e_faixa_6(self):
        self.assertEqual(classify_experimental_kappa(55.01)[0], "Faixa 6 — acima de 55")

    def test_valores_invalidos_nao_recebem_faixa(self):
        self.assertEqual(classify_experimental_kappa(-1)[0], "Faixa não disponível")
        self.assertEqual(classify_experimental_kappa(float("nan"))[0], "Faixa não disponível")

    def test_cada_faixa_tem_cor_hexadecimal(self):
        for valor in (1, 4, 9, 20, 40, 80):
            cor = classify_experimental_kappa(valor)[1]
            self.assertRegex(cor, r"^#[0-9A-Fa-f]{6}$")


if __name__ == "__main__":
    unittest.main()
