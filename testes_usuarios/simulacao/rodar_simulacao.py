"""Roda os cenarios SIMULADOS (personas ficticias) no assistente real e mede acerto de intencao.
ATENCAO: simulacao, nao teste com pessoas reais. Saida: simulacao/resultado_simulacao.csv"""
import csv
import json
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(AQUI)))
from energia.assistente import responder  # noqa: E402


def main():
    cenarios = json.load(open(os.path.join(AQUI, "cenarios.json"), encoding="utf-8"))
    linhas, ok = [], 0
    for c in cenarios:
        for q in c["perguntas"]:
            t0 = time.perf_counter()
            r = responder(q["texto"])
            ms = (time.perf_counter() - t0) * 1000
            obtido = r["intencao"] if r["ok"] else "invalida"
            acertou = obtido == q["esperado"]
            ok += acertou
            linhas.append([c["id"], q["texto"], q["esperado"], obtido, r["nivel"], "sim" if r["referencias"] else "nao",
                           "sim" if acertou else "nao", f"{ms:.1f}"])
    with open(os.path.join(AQUI, "resultado_simulacao.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cenario", "pergunta", "intencao_esperada", "intencao_obtida", "nivel_confianca", "tem_referencia", "acertou", "tempo_resposta_ms"])
        w.writerows(linhas)
    print(f"Acerto: {ok}/{len(linhas)} = {100 * ok / len(linhas):.0f}%")
    for l in linhas:
        if l[6] == "nao":
            print("FALHOU:", l[1], "| esperado", l[2], "| obtido", l[3], "|", l[4])


if __name__ == "__main__":
    main()
