"""Gera resultados/: tabela de consumo, comparacao (CSV + MD), sensibilidade e grafico. Execute: python calculos/gerar_relatorio.py"""
import csv
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from energia import calculos as c  # noqa: E402

SAIDA = os.path.join(RAIZ, "resultados")
os.makedirs(SAIDA, exist_ok=True)


def fmt(v, n=2):
    return f"{v:.{n}f}"


def main():
    params = c.carregar_parametros()
    itens = c.carregar_equipamentos()
    r = c.comparar(params, itens)

    with open(os.path.join(SAIDA, "consumo_por_equipamento.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["equipamento", "kwh_mes", "percentual"])
        for i in sorted(itens, key=lambda i: -i["kwh_mes"]):
            w.writerow([i["equipamento"], fmt(i["kwh_mes"]), fmt(100 * i["kwh_mes"] / r["consumo_base_kwh_mes"], 1)])
        w.writerow(["TOTAL", fmt(r["consumo_base_kwh_mes"]), "100.0"])

    cab = ["alternativa", "renovavel", "investimento_rs", "economia_rs_mes_ano1", "payback_anos_com_reajuste",
           "payback_anos_sem_reajuste", "economia_acumulada_15a_rs", "vpl_10pct_rs", "co2_evitado_kg_ano1"]
    linhas = []
    for a in r["alternativas"]:
        f, f0 = a["fluxo"], a["fluxo_sem_reajuste"]
        linhas.append([a["nome"], "sim" if a["renovavel"] else "nao", fmt(a["investimento"]), fmt(a["economia_rs_mes_ano1"]),
                       fmt(f["payback_anos"], 1) if f["payback_anos"] is not None else ">15",
                       fmt(f0["payback_anos"], 1) if f0["payback_anos"] is not None else ">15",
                       fmt(f["acumulado_final"], 0), fmt(f["vpl"], 0), fmt(a["co2_evitado_kg_ano1"], 1)])
    with open(os.path.join(SAIDA, "comparacao_alternativas.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cab)
        w.writerows(linhas)

    # sensibilidade ao fator de emissao
    with open(os.path.join(SAIDA, "sensibilidade_emissao.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["fator_tco2_mwh", "origem", "A_kg_ano", "B_kg_ano", "C_kg_ano"])
        for fe, o in ((0.0289, "abr/2025 (MCTI)"), (0.0385, "media 2023 (MCTI) - usado"), (0.0426, "media 2022"), (0.1264, "media 2021")):
            w.writerow([fe, o] + [fmt(a["fluxo"]["kwh_evitados_ano1"] * fe, 1) for a in r["alternativas"]])

    # sensibilidade da tarifa (payback do FV e do aquecedor)
    with open(os.path.join(SAIDA, "sensibilidade_tarifa.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tarifa_rs_kwh", "payback_A_anos", "payback_B_anos", "payback_C_anos"])
        for t in (0.70, 0.85, 1.00, 1.15, 1.30):
            p2 = dict(params)
            p2["tarifa_kwh_rs"] = dict(params["tarifa_kwh_rs"], valor=t)
            rr = c.comparar(p2, itens)
            w.writerow([t] + [fmt(a["fluxo_sem_reajuste"]["payback_anos"], 1) if a["fluxo_sem_reajuste"]["payback_anos"] is not None else ">15"
                              for a in rr["alternativas"]])

    # Markdown
    md = ["# Resultados (gerado por calculos/gerar_relatorio.py)\n",
          f"Consumo-base: **{fmt(r['consumo_base_kwh_mes'], 1)} kWh/mes** | conta-base: **R$ {fmt(r['conta_base_rs_mes'])}/mes** "
          f"(tarifa estimada R$ {fmt(c.p(params, 'tarifa_kwh_rs'))}/kWh). Dados ESTIMADOS - ver dados/parametros.json.\n",
          "| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    md += ["| " + " | ".join(l) + " |" for l in linhas]
    with open(os.path.join(SAIDA, "comparacao_alternativas.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    # Grafico
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for a, rot in zip(r["alternativas"], ("A - Eficiencia", "B - Aquecedor solar", "C - Fotovoltaico")):
            xs = [0] + [x["ano"] for x in a["fluxo"]["anos"]]
            ys = [-a["investimento"]] + [x["acumulado"] for x in a["fluxo"]["anos"]]
            ax.plot(xs, ys, marker="o", markersize=3, label=rot)
        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_xlabel("Ano")
        ax.set_ylabel("Economia acumulada liquida (R$)")
        ax.set_title("Economia acumulada em 15 anos (estimativa, tarifa +4%/ano)")
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(SAIDA, "grafico_economia_acumulada.png"), dpi=130)
    except ImportError:
        print("matplotlib ausente: grafico nao gerado (pip install matplotlib).")
    print("Resultados gerados em", SAIDA)


if __name__ == "__main__":
    main()
