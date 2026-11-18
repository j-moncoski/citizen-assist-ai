"""Assistente de energia (regras com nivel de confianca). Integra-se ao Citizen Assist AI via responder().

Nao e canal oficial de nenhuma concessionaria ou orgao. Todas as respostas usam os numeros de calculos.py,
portanto sempre coerentes com a analise em docs/ e resultados/.
"""
from . import calculos as c
from .referencias import REFERENCIAS
from .validacao import normalizar, validar_pergunta

AVISO_GERAL = ("Estimativas (nao garantias). Valores dependem da sua conta, tarifa, local e orcamento real. "
               "Este assistente nao e canal oficial da distribuidora nem da ANEEL.")

# intencao -> palavras-chave (ja sem acento)
INTENCOES = {
    "aquecedor": ["aquecedor", "banho", "chuveiro", "agua quente"],
    "eficiencia": ["led", "lampada", "standby", "stand-by", "regua", "habito", "desperdicio", "eficiencia", "sem gastar", "dica"],
    "comparar": ["comparar", "alternativa", "melhor", "vale a pena", "economizar", "economia", "compensa", "qual escolher", " ou ", "baixar a conta"],
    "emissao": ["co2", "emissao", "carbono", "ambiental", "ambiente", "polui", "sustentavel"],
    "solar": ["solar", "fotovoltaic", "painel", "placa", "energia renovavel", "gerar energia", "microgeracao", "zerar"],
    "consumo": ["consumo", "kwh", "gasta", "gastando", "equipamento", "aparelho", "conta de luz", "quanto custa", "maior consumo", "vilao"],
    "limites": ["garantia", "garantido", "certeza", "limitacao", "erro", "confiavel", "confiar", "posso confiar", "vou economizar"],
    "fontes": ["fonte", "referencia", "de onde", "dados"],
    "ajuda": ["ajuda", "menu", "o que voce faz", "como funciona"],
}


def classificar(pergunta):
    """Retorna (intencao, confianca 0..1). Confianca = acertos de palavra-chave / 2 (max 1)."""
    t = normalizar(pergunta)
    melhor, acertos = None, 0
    for nome, palavras in INTENCOES.items():
        n = sum(1 for w in palavras if w in t)
        if n > acertos:
            melhor, acertos = nome, n
    if melhor is None:
        return None, 0.0
    return melhor, min(1.0, acertos / 2)


def _reais(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _num(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",")


def _anos(v):
    if v is None:
        return "mais que o horizonte de 15 anos"
    if v < 1:
        return f"{max(1, round(v * 12))} meses"
    return f"{_num(v)} anos"


def _txt_consumo(r, itens):
    ordenados = sorted(itens, key=lambda i: i["kwh_mes"], reverse=True)[:3]
    top = "; ".join(f"{i['equipamento'].split('(')[0].strip()}: {_num(i['kwh_mes'])} kWh/mes" for i in ordenados)
    return (f"Na residencia-modelo (4 pessoas, dados ESTIMADOS) o consumo e ~{_num(r['consumo_base_kwh_mes'])} kWh/mes "
            f"(~{_reais(r['conta_base_rs_mes'])}/mes a {_reais(c.p(PARAMS, 'tarifa_kwh_rs'))}/kWh). "
            f"Maiores consumos: {top}. Energia = potencia x tempo (kWh = kW x h).")


def _linha_alt(a):
    f = a["fluxo"]
    return (f"{a['nome']}: investimento {_reais(a['investimento'])}, economia ~{_reais(a['economia_rs_mes_ano1'])}/mes no ano 1, "
            f"retorno em {_anos(f['payback_anos'])} (ou {_anos(a['fluxo_sem_reajuste']['payback_anos'])} sem reajuste de tarifa), "
            f"CO2 evitado ~{_num(a['co2_evitado_kg_ano1'])} kg/ano.")


PARAMS = c.carregar_parametros()
ITENS = c.carregar_equipamentos()
RESULT = c.comparar(PARAMS, ITENS)


def _montar(intencao):
    r, A, B, C = RESULT, *RESULT["alternativas"]
    if intencao == "consumo":
        return _txt_consumo(r, ITENS), ["R5"]
    if intencao == "comparar":
        txt = ("Para a mesma necessidade (reduzir a conta de luz), horizonte de 15 anos:\n- " +
               "\n- ".join(_linha_alt(a) for a in (A, B, C)) +
               "\nSugestao do modelo: comece pela A (barata e rapida) e depois dimensione o solar com o consumo ja reduzido.")
        return txt, ["R2", "R3", "R4", "R1"]
    if intencao == "solar":
        d = C["detalhe"]
        return (f"Solar fotovoltaico on-grid (modelo): {d['modulos']} modulos = {_num(d['kwp'], 2)} kWp, gera ~{_num(d['geracao_kwh_mes'], 0)} kWh/mes. "
                f"{_linha_alt(C)} Mesmo com muito credito, a conta nunca zera: ha o custo de disponibilidade "
                f"({c.p(PARAMS, 'custo_disponibilidade_kwh'):.0f} kWh/mes em ligacao bifasica)."), ["R3", "R4", "R2"]
    if intencao == "eficiencia":
        d = A["detalhe"]
        return (f"Eficiencia e habitos (A): trocar 10 lampadas fluorescentes por LED economiza ~{_num(d['led'])} kWh/mes; "
                f"banho de 8 para 6 min, ~{_num(d['banho'])}; regua anti-standby, ~{_num(d['standby'])}. "
                f"Total ~{_num(A['economia_kwh_mes'])} kWh/mes ({_reais(A['economia_rs_mes_ano1'])}/mes) com investimento de ~{_reais(A['investimento'])}."), ["R5"]
    if intencao == "aquecedor":
        return (f"Chuveiro eletrico e o maior consumo da casa-modelo (~{_num(c.kwh_chuveiro(PARAMS))} kWh/mes). "
                f"Aquecedor solar de agua (B) cobre ~{int(PARAMS['alternativa_B']['fracao_solar'] * 100)}% desse uso. "
                f"{_linha_alt(B)} Em dias nublados continua sendo necessario o apoio eletrico."), ["R5", "R3"]
    if intencao == "emissao":
        fe = c.p(PARAMS, "fator_emissao_tco2_mwh") * 1000
        return (f"A matriz eletrica brasileira ja e majoritariamente renovavel: fator medio do SIN em 2023 = {_num(fe)} kgCO2/MWh. "
                f"Por isso o CO2 evitado em casa e pequeno (ex.: solar FV ~{_num(C['co2_evitado_kg_ano1'])} kg/ano) e o principal ganho e financeiro. "
                f"O fator varia (28,9 kg/MWh em abr/2025; 126,4 em 2021). Nao inclui emissoes de fabricacao dos equipamentos."), ["R1", "R6", "R7"]
    if intencao == "limites":
        return ("Os numeros sao estimativas: tarifa, irradiacao, custos, habitos e regras (Lei 14.300) mudam. "
                "Nao ha garantia de economia. Confira sua conta real, peca orcamentos e consulte um profissional habilitado antes de investir."), ["R4"]
    if intencao == "fontes":
        return "Fontes usadas (verificaveis) listadas abaixo. Dados ESTIMADOS estao marcados em dados/parametros.json.", list(REFERENCIAS)
    return ("Posso ajudar com: consumo dos equipamentos, comparar alternativas de economia/solar, "
            "energia solar fotovoltaica, aquecedor solar, emissoes e limitacoes. Ex.: 'vale a pena painel solar?'"), []


def responder(pergunta):
    """Retorna dict: ok, intencao, confianca, nivel, texto, referencias(list), aviso."""
    ok, erro = validar_pergunta(pergunta)
    if not ok:
        return {"ok": False, "intencao": None, "confianca": 0.0, "nivel": "invalida", "texto": erro, "referencias": [], "aviso": AVISO_GERAL}
    intencao, conf = classificar(pergunta)
    if intencao is None:
        return {"ok": True, "intencao": None, "confianca": 0.0, "nivel": "nao sei",
                "texto": ("Nao sei responder isso com seguranca. Tente perguntar sobre: consumo, comparar alternativas, "
                          "solar fotovoltaico, aquecedor solar, emissoes ou limitacoes."),
                "referencias": [], "aviso": AVISO_GERAL}
    texto, refs = _montar(intencao)
    nivel = "alta" if conf >= 1.0 else "media"
    if conf < 1.0:
        texto = "(Confianca media - se nao era isso, reformule.) " + texto
    return {"ok": True, "intencao": intencao, "confianca": conf, "nivel": nivel, "texto": texto, "referencias": refs, "aviso": AVISO_GERAL}


def simular(consumo_kwh_mes, tarifa):
    """Resposta para a simulacao com a conta do proprio usuario (somente FV)."""
    s = c.simular_conta(consumo_kwh_mes, tarifa, PARAMS)
    a, f = s["alt"], s["fluxo"]
    d = a["detalhe"]
    return (f"Com {_num(consumo_kwh_mes, 0)} kWh/mes e {_reais(tarifa)}/kWh: sistema de ~{d['modulos']} modulos ({_num(d['kwp'], 2)} kWp), "
            f"investimento estimado {_reais(a['investimento'])}. Conta de {_reais(s['conta_atual'])} para ~{_reais(s['conta_com_fv'])}/mes (ano 1). "
            f"Retorno ~{_anos(f['payback_anos'])} ({_anos(s['fluxo_sem_reajuste']['payback_anos'])} sem reajuste). "
            f"ESTIMATIVA com premissas de dados/parametros.json - nao e orcamento.")
