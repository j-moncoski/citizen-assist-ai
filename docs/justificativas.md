# 3. Justificativas, viabilidade, impactos e limitações

## Custos
A tem o menor custo e o retorno mais rápido (R$ 140 → ~4 meses). C tem o maior ganho absoluto (R$ 165/mês), mas exige R$ 7.425 de entrada. B tem retorno longo (7 anos) nas premissas atuais (VPL positivo, porém pequeno: R$ 846).

## Viabilidade
- **A:** sem obras, imediata. Depende de mudança de hábito (banho de 6 min).
- **B:** exige espaço no telhado, reservatório térmico e instalação; no inverno/dias nublados precisa de apoio elétrico (por isso fração solar de 70%, não 100%).
- **C:** exige telhado adequado (orientação/sombreamento), projeto e homologação na distribuidora; regras da Lei 14.300 reduzem a compensação da energia injetada de forma gradual [R4]; com ligação bifásica sempre se paga o custo de disponibilidade (50 kWh).

## Impactos ambientais
A matriz elétrica brasileira já é majoritariamente renovável: fator médio do SIN de 38,5 kgCO₂/MWh em 2023 [R1]. Por isso, **o CO₂ evitado em casa é pequeno** (16–76 kg/ano) e o argumento principal de A e C é financeiro. O fator varia bastante entre anos (126,4 kg/MWh em 2021). **Limitação:** consideramos só emissão operacional evitada (método do fator médio); não descontamos a fabricação dos painéis/aquecedor (ciclo de vida do FV de telhado ≈ 41 gCO₂e/kWh segundo [R7]) nem usamos fator marginal. Comparar diretamente o ciclo de vida do painel com um fator operacional da rede não é equivalente; por isso o assistente avisa que o ganho ambiental é modesto e depende do método.

## Por que estas recomendações são coerentes com o assistente
As respostas do assistente (`energia/assistente.py`) são geradas chamando as mesmas funções de `energia/calculos.py` que produzem os resultados deste repositório; há teste automatizado verificando essa coerência (`test_coerencia_com_analise`).

## Limitações e condições
1. Consumo, hábitos, potência do chuveiro, custos, HSP, PR e fator de compensação são **estimados**; trocar pelos dados reais (conta de luz, SunData, orçamentos).
2. Tarifa de R$ 1,00/kWh e reajuste de 4%/ano são premissas; a tarifa real da Enel SP deve ser conferida na conta [R2].
3. Não incluímos bandeiras tarifárias, COSIP, impostos sobre créditos de geração, financiamento nem valor residual dos equipamentos.
4. Aquecedor solar e FV dependem de local, telhado e clima; resultados reais podem ser melhores ou piores.
5. Estimativas **não são garantias** nem orçamento; consulte profissional habilitado. O assistente **não é canal oficial** de nenhum órgão ou concessionária.
