"""Citizen Assist AI - modulo de Energia (CLI). Execute: python main.py"""
from energia.assistente import responder, simular, AVISO_GERAL, RESULT, ITENS
from energia.referencias import formatar, REFERENCIAS
from energia.validacao import ler_numero

MENU = """
=== Citizen Assist AI | Energia e Sustentabilidade ===
1) Perguntar ao assistente
2) Ver consumo da residencia-modelo
3) Comparar alternativas (A, B, C)
4) Simular com a minha conta (kWh/mes e tarifa)
5) Fontes e limitacoes
0) Sair
"""


def mostrar(r):
    print("\n" + r["texto"])
    if r["referencias"]:
        print("\nReferencias:\n" + formatar(r["referencias"]))
    if r["ok"] and r["nivel"] != "invalida":
        print(f"\n[confianca: {r['nivel']}] Aviso: {r['aviso']}")


def main():
    print("Nao informe dados pessoais. " + AVISO_GERAL)
    while True:
        print(MENU)
        op = input("Escolha uma opcao: ").strip()
        if op == "0":
            print("Ate logo!")
            break
        elif op == "1":
            mostrar(responder(input("Sua pergunta: ")))
        elif op == "2":
            mostrar(responder("qual o maior consumo da casa"))
            for i in sorted(ITENS, key=lambda i: -i["kwh_mes"]):
                print(f"  {i['equipamento']:<45} {i['kwh_mes']:7.1f} kWh/mes")
        elif op == "3":
            mostrar(responder("comparar alternativas"))
        elif op == "4":
            kwh, e1 = ler_numero(input("Consumo mensal (kWh, ver na conta): "), 50, 2000)
            if e1:
                print(e1)
                continue
            tar, e2 = ler_numero(input("Tarifa com tributos (R$/kWh, ver na conta): "), 0.3, 3.0)
            if e2:
                print(e2)
                continue
            print("\n" + simular(kwh, tar))
            print("Referencias:\n" + formatar(["R3", "R4"]) + "\nAviso: " + AVISO_GERAL)
        elif op == "5":
            mostrar(responder("quais as fontes"))
            mostrar(responder("limitacoes e garantia"))
        else:
            print("Opcao invalida. Digite um numero de 0 a 5.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nEncerrado.")
