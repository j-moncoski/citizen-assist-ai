"""Fontes verificaveis usadas pelo assistente. Os codigos [R1]... aparecem nas respostas."""

REFERENCIAS = {
    "R1": "MCTI/SIRENE - Fatores de emissao de CO2 do SIN (media anual 2023 = 38,5 kgCO2/MWh; abr/2025 = 28,9). https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao",
    "R2": "ANEEL - Reajuste tarifario anual 2026 da Enel Distribuicao Sao Paulo, efeito medio 10,18%, vigencia 04/07/2026 (homologado em 30/06/2026). https://www.gov.br/aneel",
    "R3": "CRESESB/CEPEL - SunData e Atlas Brasileiro de Energia Solar (irradiacao no plano inclinado). http://www.cresesb.cepel.br/sundata/",
    "R4": "ANEEL - REN 1000/2021 (custo de disponibilidade: 30/50/100 kWh) e Lei 14.300/2022 (marco legal da geracao distribuida; cobranca gradual do Fio B).",
    "R5": "PROCEL/Eletrobras - Pesquisa de Posses e Habitos de Consumo (chuveiro entre os maiores consumos residenciais) e Selo PROCEL. https://www.gov.br/mme (conferir edicao vigente).",
    "R6": "EPE - Balanco Energetico Nacional (BEN) e Anuario Estatistico de Energia Eletrica (matriz eletrica brasileira com alta participacao renovavel). https://www.epe.gov.br",
    "R7": "IPCC AR5 WGIII Anexo III (2014) - emissoes de ciclo de vida de tecnologias de geracao (FV telhado ~41 gCO2e/kWh).",
}


def formatar(codigos):
    return "\n".join(f"  [{c}] {REFERENCIAS[c]}" for c in codigos)
