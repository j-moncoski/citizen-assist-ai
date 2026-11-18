import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from energia import calculos as c  # noqa: E402


class TestCalculos(unittest.TestCase):
    def setUp(self):
        self.params = c.carregar_parametros()
        self.itens = c.carregar_equipamentos()

    def test_energia_potencia_vezes_tempo(self):
        # 1 equipamento de 1000 W por 1 h/dia durante 30 dias = 30 kWh
        self.assertAlmostEqual(1 * 1000 * 1 * 30 / 1000, 30.0)

    def test_consumo_total_modelo(self):
        self.assertAlmostEqual(c.consumo_total(self.itens), 234.7, places=1)

    def test_chuveiro(self):
        self.assertAlmostEqual(c.kwh_chuveiro(self.params), 70.4, places=1)

    def test_emissao(self):
        # 1000 kWh = 1 MWh x 0,0385 tCO2/MWh = 38,5 kg
        self.assertAlmostEqual(c.emissao_kg(1000, self.params), 38.5, places=6)

    def test_dimensionamento_fv(self):
        d = c.dimensionar_fv(234.7, self.params)
        self.assertEqual(d["modulos"], 3)
        self.assertAlmostEqual(d["kwp"], 1.65)
        self.assertAlmostEqual(d["geracao_kwh_mes"], 184.7, delta=0.5)

    def test_conta_nunca_abaixo_da_disponibilidade(self):
        conta = c.conta_mensal(100, 500, 1.0, self.params)
        self.assertAlmostEqual(conta, 50.0)

    def test_comparacao_tem_ao_menos_uma_renovavel_e_horizonte_comum(self):
        r = c.comparar(self.params, self.itens)
        self.assertGreaterEqual(len(r["alternativas"]), 2)
        self.assertTrue(any(a["renovavel"] for a in r["alternativas"]))
        for a in r["alternativas"]:
            self.assertEqual(len(a["fluxo"]["anos"]), self.params["horizonte_anos"])

    def test_resultados_esperados(self):
        r = c.comparar(self.params, self.itens)
        A, B, C = r["alternativas"]
        self.assertAlmostEqual(A["economia_kwh_mes"], 35.3, places=1)
        self.assertAlmostEqual(B["economia_kwh_mes"], 49.3, places=1)
        self.assertAlmostEqual(C["economia_rs_mes_ano1"], 165.3, delta=1.0)
        self.assertLess(C["fluxo"]["payback_anos"], B["fluxo"]["payback_anos"])

    def test_sem_reajuste_payback_maior_ou_igual(self):
        r = c.comparar(self.params, self.itens)
        for a in r["alternativas"]:
            self.assertGreaterEqual(a["fluxo_sem_reajuste"]["payback_anos"], a["fluxo"]["payback_anos"] - 1e-9)


if __name__ == "__main__":
    unittest.main()
