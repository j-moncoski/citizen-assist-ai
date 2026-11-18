# 1. Contexto e análise de consumo

## Contexto
Público: famílias de ~4 pessoas em residência urbana de São Paulo (Enel SP). Necessidade: reduzir a conta de luz. Tarifas reajustadas: a ANEEL aprovou em 30/06/2026 reajuste médio de 10,18% para a Enel SP, em vigor desde 04/07/2026 [R2], o que torna o tema relevante.

## Dados de consumo
Arquivo: `dados/consumo_residencia_modelo.csv`. **Todos os dados são ESTIMADOS** (residência-modelo), não medidos. Unidade: potência em W, tempo em h/dia, período: mês de 30 dias. Cada linha vem de **E (kWh) = qtd × P (W) × h/dia × dias ÷ 1000**.

| Equipamento | kWh/mês | % |
|---|---|---|
| Chuveiro elétrico (4 pessoas × 8 min/dia, 4,4 kW médio) | 70,4 | 30,0 |
| Geladeira (potência média equivalente 55 W) | 39,6 | 16,9 |
| Ventiladores (2 × 80 W × 6 h) | 28,8 | 12,3 |
| Iluminação fluorescente compacta (10 × 15 W × 5 h) | 22,5 | 9,6 |
| TV LED | 15,0 | 6,4 |
| Computador/notebook | 10,8 | 4,6 |
| Standby (carregadores/decoder) | 10,8 | 4,6 |
| Micro-ondas | 9,0 | 3,8 |
| Secador de cabelo | 8,1 | 3,5 |
| Roteador/modem | 7,2 | 3,1 |
| Máquina de lavar | 6,0 | 2,6 |
| Ferro de passar | 4,0 | 1,7 |
| Aspirador/outros | 2,5 | 1,1 |
| **Total** | **234,7** | 100 |

Conta-base: 234,7 kWh × R$ 1,00/kWh (tarifa com tributos, **ESTIMADA** — conferir na conta real) = **R$ 234,70/mês**. Não inclui COSIP/iluminação pública nem bandeiras tarifárias.

## Premissas
- Chuveiro: potência média de 4,4 kW já considera mistura inverno/verão; ver `dados/parametros.json`.
- 365/12 dias por mês nos cálculos de geração solar; 30 dias nos de consumo.
- O chuveiro ser o maior consumo é coerente com pesquisas do PROCEL [R5], mas o percentual exato aqui é do modelo.
