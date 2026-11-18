# 2. Comparação de alternativas

Mesma necessidade (reduzir a conta de luz da residência-modelo, 234,7 kWh/mês), **mesmo período de referência: 15 anos**, mesma tarifa inicial (R$ 1,00/kWh, ESTIMADA) e reajuste de 4%/ano (ESTIMADO; também mostrado sem reajuste). Desconto para VPL: 10% a.a. (ESTIMADO). Código: `energia/calculos.py`.

## Fórmulas
- Energia: `E = P × t`.
- **A:** LED `10 × (15−8) W × 5 h × 30 / 1000 = 10,5 kWh`; banho 8→6 min `70,4 × (1−6/8) = 17,6 kWh`; standby `(15−5) W × 24 × 30 / 1000 = 7,2 kWh`. Total **35,3 kWh/mês**.
- **B:** `70,4 kWh × 70% (fração solar) = 49,3 kWh/mês`; manutenção R$ 100/ano.
- **C:** `kWp = (consumo − disponibilidade) / (HSP × 30,42 × PR)`; `(234,7 − 50) / (4,6 × 30,42 × 0,80) = 1,65 kWp` → 3 módulos de 550 Wp. Geração ≈ **184,7 kWh/mês**. Créditos = geração × [autoconsumo 30% + injeção 70% × 0,85 (efeito do Fio B, Lei 14.300) ] = 165,3 kWh-equivalentes. Fatura mínima = custo de disponibilidade de 50 kWh (bifásico) [R4]. Troca do inversor no ano 12 (R$ 1.800).
- **CO₂ evitado:** `kWh evitados × 0,0385 tCO₂/MWh` (fator médio SIN 2023, MCTI [R1]) — apenas emissão **operacional** evitada.
- **Payback:** primeiro ano em que a economia acumulada líquida ≥ 0 (interpolado). **VPL:** fluxo líquido descontado a 10%.

## Resultados

| | A Eficiência | B Aquec. solar | C Solar FV |
|---|---|---|---|
| Fonte renovável? | não | sim (térmica) | sim (elétrica) |
| Investimento (R$) | 140 | 4.000 | 7.425 |
| Economia ano 1 (kWh/mês) | 35,3 | 49,3 | ~165 (kWh-equiv.) |
| Economia líquida ano 1 (R$/mês) | 35,30 | 40,95 | 165,30 |
| Payback com reajuste 4% | ~4 meses | 7,0 anos | 3,6 anos |
| Payback sem reajuste | ~4 meses | 8,1 anos | 3,8 anos |
| Economia acumulada 15 anos (R$) | 8.242 | 6.341 | 28.993 |
| VPL a 10% (R$) | 3.838 | 846 | 10.258 |
| CO₂ evitado ano 1 (kg) | 16,3 | 22,8 | 76,4 |

Gráfico: `resultados/grafico_economia_acumulada.png`. Tabelas: `resultados/*.csv`.

## Sensibilidades
- **Tarifa** (`resultados/sensibilidade_tarifa.csv`, sem reajuste): com R$ 0,70/kWh o payback do FV vai a 5,4 anos e o do aquecedor a 12,7; com R$ 1,30, FV 2,9 e aquecedor 6,0.
- **Fator de emissão** (`resultados/sensibilidade_emissao.csv`): para o FV, 57 kg/ano (28,9 kg/MWh) a 251 kg/ano (126,4 kg/MWh, ano 2021).

## Combinação recomendada pelo modelo
Começar por **A** (retorno em meses) e só depois dimensionar o **C** sobre o consumo já reduzido (evita sistema superdimensionado). **B** é a menos atrativa financeiramente nestas premissas, mas atua direto no maior consumo e pode fazer sentido para quem já vai reformar o banheiro/telhado.
