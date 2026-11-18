"""Calculos de consumo e comparacao de alternativas (A: eficiencia, B: aquecedor solar, C: fotovoltaico).

Todas as formulas estao documentadas em docs/comparacao_alternativas.md.
Unidades: potencia em W, energia em kWh, dinheiro em R$, emissoes em kgCO2.
"""
import csv
import json
import math
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIAS_MES = 365 / 12  # dias medios por mes


def carregar_parametros(caminho=None):
    caminho = caminho or os.path.join(RAIZ, "dados", "parametros.json")
    with open(caminho, encoding="utf-8") as f:
        bruto = json.load(f)
    return bruto


def p(params, chave):
    """Atalho: retorna o campo 'valor' de um parametro."""
    return params[chave]["valor"]


def carregar_equipamentos(caminho=None):
    caminho = caminho or os.path.join(RAIZ, "dados", "consumo_residencia_modelo.csv")
    itens = []
    with open(caminho, encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            qtd = float(linha["qtd"])
            pot = float(linha["potencia_w"])
            horas = float(linha["horas_dia"])
            dias = float(linha["dias_mes"])
            kwh = qtd * pot * horas * dias / 1000.0  # E = P x t
            itens.append({"equipamento": linha["equipamento"], "kwh_mes": kwh, "origem": linha["origem"]})
    return itens


def consumo_total(itens):
    return sum(i["kwh_mes"] for i in itens)


def kwh_chuveiro(params):
    c = params["chuveiro"]
    horas = c["pessoas"] * c["minutos_por_pessoa"] / 60.0
    return c["potencia_media_w"] * horas * 30 / 1000.0


def emissao_kg(kwh, params):
    """Emissao operacional evitada (metodo do fator medio do SIN, MCTI)."""
    return kwh * p(params, "fator_emissao_tco2_mwh")  # kWh x (tCO2/MWh) = kgCO2


# ---------------- Alternativa A: eficiencia / habitos ----------------
def alternativa_a(params, consumo_base):
    a = params["alternativa_A"]
    led = a["led_qtd"] * (a["w_antes"] - a["w_depois"]) * a["horas_dia"] * 30 / 1000.0
    banho = kwh_chuveiro(params) * (1 - a["banho_min_depois"] / params["chuveiro"]["minutos_por_pessoa"])
    standby = (a["standby_w_antes"] - a["standby_w_depois"]) * 24 * 30 / 1000.0
    economia = led + banho + standby
    return {
        "nome": "A - Eficiencia e habitos (LED + banho 6 min + regua anti-standby)",
        "renovavel": False,
        "investimento": a["custo_rs"],
        "economia_kwh_mes": economia,
        "detalhe": {"led": led, "banho": banho, "standby": standby},
        "custos_extras": {a["reposicao_led_ano"]: a["reposicao_led_rs"]},
        "manutencao_ano": 0.0,
        "geracao_kwh_mes": 0.0,
    }


# ---------------- Alternativa B: aquecedor solar de agua ----------------
def alternativa_b(params, consumo_base):
    b = params["alternativa_B"]
    economia = kwh_chuveiro(params) * b["fracao_solar"]
    return {
        "nome": "B - Aquecedor solar de agua (renovavel termica)",
        "renovavel": True,
        "investimento": b["custo_rs"],
        "economia_kwh_mes": economia,
        "detalhe": {"chuveiro_evitado": economia},
        "custos_extras": {},
        "manutencao_ano": b["manutencao_rs_ano"],
        "geracao_kwh_mes": 0.0,
    }


# ---------------- Alternativa C: fotovoltaico on-grid ----------------
def dimensionar_fv(consumo_kwh_mes, params):
    """kWp = (consumo - disponibilidade) / (HSP x dias x PR); arredonda ao modulo inteiro mais proximo."""
    alvo = max(consumo_kwh_mes - p(params, "custo_disponibilidade_kwh"), 0)
    kwh_por_kwp_mes = p(params, "hsp_kwh_m2_dia") * DIAS_MES * p(params, "performance_ratio")
    kwp_ideal = alvo / kwh_por_kwp_mes if kwh_por_kwp_mes else 0
    wp_modulo = p(params, "potencia_modulo_wp")
    modulos = max(1, round(kwp_ideal * 1000 / wp_modulo)) if alvo > 0 else 0
    kwp = modulos * wp_modulo / 1000.0
    return {"kwp_ideal": kwp_ideal, "modulos": modulos, "kwp": kwp, "geracao_kwh_mes": kwp * kwh_por_kwp_mes}


def valor_geracao_kwh(geracao, params):
    """kWh-equivalentes creditados: autoconsumo vale 100%; injecao vale fator_compensacao (Fio B)."""
    auto = p(params, "autoconsumo_instantaneo")
    return geracao * (auto + (1 - auto) * p(params, "fator_compensacao_injetada"))


def conta_mensal(consumo, creditos_kwh, tarifa, params):
    faturavel = max(consumo - creditos_kwh, p(params, "custo_disponibilidade_kwh"))
    return faturavel * tarifa


def alternativa_c(params, consumo_base):
    dim = dimensionar_fv(consumo_base, params)
    ti = params["troca_inversor"]
    return {
        "nome": "C - Fotovoltaico on-grid (renovavel eletrica)",
        "renovavel": True,
        "investimento": dim["kwp"] * p(params, "custo_fv_rs_por_kwp"),
        "economia_kwh_mes": None,  # depende de tarifa/creditos: calculado no fluxo
        "detalhe": dim,
        "custos_extras": {ti["ano"]: ti["custo_rs"]},
        "manutencao_ano": 0.0,
        "geracao_kwh_mes": dim["geracao_kwh_mes"],
    }


# ---------------- Fluxo de caixa em horizonte comum ----------------
def fluxo(alt, consumo_base, params, reajuste=None):
    """Retorna economia anual por ano (1..H), economia acumulada liquida, payback, VPL e CO2."""
    h = params["horizonte_anos"]
    tarifa0 = p(params, "tarifa_kwh_rs")
    reaj = p(params, "reajuste_tarifa_anual") if reajuste is None else reajuste
    taxa = params["taxa_desconto"]
    deg = p(params, "degradacao_fv_anual")
    anos, acum, vpl = [], -alt["investimento"], -alt["investimento"]
    payback = None
    saldo_ant = acum
    kwh_evitados_total = 0.0
    for ano in range(1, h + 1):
        tarifa = tarifa0 * (1 + reaj) ** (ano - 1)
        if alt["geracao_kwh_mes"] > 0:  # FV
            ger = alt["geracao_kwh_mes"] * (1 - deg) ** (ano - 1)
            cred = valor_geracao_kwh(ger, params)
            antes = consumo_base * tarifa
            depois = conta_mensal(consumo_base, cred, tarifa, params)
            econ_mes = antes - depois
            kwh_ev_mes = min(cred, max(consumo_base - p(params, "custo_disponibilidade_kwh"), 0))
        else:
            econ_mes = alt["economia_kwh_mes"] * tarifa
            kwh_ev_mes = alt["economia_kwh_mes"]
        liquido = econ_mes * 12 - alt["manutencao_ano"] - alt["custos_extras"].get(ano, 0.0)
        acum += liquido
        vpl += liquido / (1 + taxa) ** ano
        kwh_evitados_total += kwh_ev_mes * 12
        anos.append({"ano": ano, "economia_liquida": liquido, "acumulado": acum})
        if payback is None and acum >= 0:
            # interpolacao linear dentro do ano
            frac = -saldo_ant / liquido if liquido else 0
            payback = (ano - 1) + frac
        saldo_ant = acum
    return {
        "anos": anos,
        "acumulado_final": acum,
        "payback_anos": payback,
        "vpl": vpl,
        "kwh_evitados_ano1": (alt["economia_kwh_mes"] if alt["geracao_kwh_mes"] == 0 else
                              min(valor_geracao_kwh(alt["geracao_kwh_mes"], params),
                                  max(consumo_base - p(params, "custo_disponibilidade_kwh"), 0))) * 12,
        "kwh_evitados_total": kwh_evitados_total,
    }


def comparar(params=None, itens=None):
    params = params or carregar_parametros()
    itens = itens or carregar_equipamentos()
    base = consumo_total(itens)
    tarifa = p(params, "tarifa_kwh_rs")
    resultado = {"consumo_base_kwh_mes": base, "conta_base_rs_mes": base * tarifa, "alternativas": []}
    for fn in (alternativa_a, alternativa_b, alternativa_c):
        alt = fn(params, base)
        f = fluxo(alt, base, params)
        f0 = fluxo(alt, base, params, reajuste=0.0)
        alt["fluxo"] = f
        alt["fluxo_sem_reajuste"] = f0
        alt["economia_rs_mes_ano1"] = f["anos"][0]["economia_liquida"] / 12
        alt["co2_evitado_kg_ano1"] = emissao_kg(f["kwh_evitados_ano1"], params)
        resultado["alternativas"].append(alt)
    return resultado


def simular_conta(consumo_kwh_mes, tarifa, params=None):
    """Simulacao simplificada para o cidadao: dimensiona FV e estima payback com a propria conta."""
    params = dict(params or carregar_parametros())
    params["tarifa_kwh_rs"] = dict(params["tarifa_kwh_rs"], valor=tarifa)
    alt = alternativa_c(params, consumo_kwh_mes)
    f = fluxo(alt, consumo_kwh_mes, params)
    f0 = fluxo(alt, consumo_kwh_mes, params, reajuste=0.0)
    return {"alt": alt, "fluxo": f, "fluxo_sem_reajuste": f0,
            "conta_atual": consumo_kwh_mes * tarifa,
            "conta_com_fv": conta_mensal(consumo_kwh_mes, valor_geracao_kwh(alt["geracao_kwh_mes"], params), tarifa, params)}
