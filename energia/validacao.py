"""Validacao de entradas e protecao de dados pessoais (LGPD: nao coletar dados desnecessarios)."""
import re
import unicodedata

MAX_TEXTO = 300
_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_TEL = re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b")


def normalizar(texto):
    """minusculas e sem acentos, para comparar palavras-chave."""
    t = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def validar_pergunta(texto):
    """Retorna (ok, mensagem_de_erro). Rejeita vazio, muito longo, caracteres de controle e dados pessoais."""
    if texto is None or not isinstance(texto, str) or not texto.strip():
        return False, "Digite uma pergunta (ex.: 'vale a pena painel solar?')."
    if len(texto) > MAX_TEXTO:
        return False, f"Pergunta muito longa (maximo {MAX_TEXTO} caracteres)."
    if any(unicodedata.category(c) == "Cc" and c not in "\t\n" for c in texto):
        return False, "A pergunta contem caracteres invalidos."
    if _CPF.search(texto) or _EMAIL.search(texto) or _TEL.search(texto):
        return False, ("Parece haver dado pessoal (CPF, e-mail ou telefone). "
                       "Nao precisamos disso: reescreva a pergunta sem dados pessoais.")
    return True, ""


def ler_numero(texto, minimo, maximo):
    """Converte '250' ou '1,05' em float dentro do intervalo; retorna (valor, erro)."""
    try:
        v = float(str(texto).strip().replace(",", "."))
    except (ValueError, TypeError):
        return None, "Digite apenas um numero (ex.: 250 ou 1,05)."
    if v != v or v in (float("inf"), float("-inf")):
        return None, "Numero invalido."
    if not (minimo <= v <= maximo):
        return None, f"Valor fora do intervalo aceito ({minimo} a {maximo})."
    return v, ""
