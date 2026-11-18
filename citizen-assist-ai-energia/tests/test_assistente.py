import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from energia.assistente import responder, simular  # noqa: E402
from energia.validacao import ler_numero, validar_pergunta  # noqa: E402


class TestAssistente(unittest.TestCase):
    def test_pergunta_solar(self):
        r = responder("Vale a pena instalar painel solar?")
        self.assertTrue(r["ok"])
        self.assertEqual(r["intencao"], "solar")
        self.assertIn("R3", r["referencias"])
        self.assertIn("nao e canal oficial", r["aviso"].lower())

    def test_sem_acento_e_maiuscula(self):
        self.assertEqual(responder("EMISSÃO de CO2")["intencao"], "emissao")

    def test_nao_sei(self):
        r = responder("qual a capital da Franca")
        self.assertEqual(r["nivel"], "nao sei")
        self.assertEqual(r["referencias"], [])

    def test_entradas_invalidas(self):
        for texto in ("", "   ", None, "x" * 301, "oi\x00"):
            self.assertFalse(responder(texto)["ok"], repr(texto))

    def test_dados_pessoais_bloqueados(self):
        for texto in ("meu cpf 123.456.789-09", "email fulano@site.com solar", "ligue (11) 91234-5678 solar"):
            self.assertFalse(responder(texto)["ok"], texto)

    def test_numero_valido_e_invalido(self):
        self.assertEqual(ler_numero("1,05", 0.3, 3)[0], 1.05)
        self.assertIsNone(ler_numero("abc", 0, 10)[0])
        self.assertIsNone(ler_numero("nan", 0, 10)[0])
        self.assertIsNone(ler_numero("5000", 50, 2000)[0])
        self.assertIsNone(ler_numero("-3", 50, 2000)[0])

    def test_validar_pergunta_ok(self):
        self.assertTrue(validar_pergunta("quanto gasta o chuveiro?")[0])

    def test_simular_coerente(self):
        txt = simular(234.7, 1.0)
        self.assertIn("3 modulos", txt)
        self.assertIn("ESTIMATIVA", txt)

    def test_coerencia_com_analise(self):
        # a resposta do assistente usa os mesmos numeros de calculos.comparar()
        self.assertIn("165,30", responder("comparar alternativas")["texto"])

    def test_toda_resposta_com_conteudo_tem_aviso(self):
        for q in ("solar", "consumo", "co2", "limitacoes e garantia", "fontes"):
            self.assertTrue(responder(q)["aviso"])


if __name__ == "__main__":
    unittest.main()


class TestRegressaoSimulacao(unittest.TestCase):
    """Casos que falharam na simulacao (testes_usuarios/simulacao) e foram corrigidos."""

    def test_frases_coloquiais(self):
        casos = {
            "como economizar sem gastar dinheiro": "eficiencia",
            "tem como zerar minha conta de luz?": "solar",
            "solar polui menos mesmo?": "emissao",
            "aquecedor solar ou painel, qual compensa mais": "comparar",
            "posso confiar que vou economizar isso tudo?": "limites",
        }
        for pergunta, esperado in casos.items():
            self.assertEqual(responder(pergunta)["intencao"], esperado, pergunta)
