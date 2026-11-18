# Citizen Assist AI — Módulo de Energia e Sustentabilidade

**Global Solution 2026.2 · FIAP · 1º ano de Ciência da Computação · Disciplina: Soluções em Energias Renováveis e Sustentáveis**

## Integrantes

| Nome | RM |
|---|---|
| Julian Nayde Moncoski | 572603 |
| Gustavo Bonamico Piccoli | 569984 |
| Victor Hugo Ferreira Freire | 571099 |

> Se este repositório for compartilhado com outras disciplinas, a contribuição de Energias Renováveis está **toda** na pasta `energia/` (código), `dados/`, `calculos/`, `resultados/`, `docs/` e `testes_usuarios/`.

## Público e problema

- **Público:** moradores de residências urbanas de São Paulo (SP), em família de ~4 pessoas, atendidos pela Enel SP, que querem **reduzir a conta de luz** mas não sabem por onde começar nem se solar "compensa".
- **Necessidade energética:** reduzir o consumo e o custo mensal de eletricidade de uma residência-modelo (~235 kWh/mês). O chuveiro elétrico sozinho responde por ~30% desse consumo.
- **Como o assistente ajuda:** responde em linguagem simples, com números calculados, **fontes** e **avisos de limitação**; compara 3 alternativas na mesma necessidade e no mesmo período (15 anos); permite simular com a conta do próprio usuário, sem pedir dados pessoais.

## Funcionalidades de energia

1. Consumo por equipamento (E = P × t) e ranking dos maiores consumos.
2. Comparação de 3 alternativas: **A** eficiência e hábitos (LED + banho de 6 min + régua anti-standby), **B** aquecedor solar de água (renovável térmica), **C** solar fotovoltaico on-grid (renovável elétrica) — com custo, retorno (payback), VPL, economia acumulada e CO₂ evitado.
3. Simulação com a conta do usuário (kWh/mês + tarifa) dimensionando o sistema fotovoltaico.
4. Respostas por regras com **nível de confiança** (alta/média/"não sei"), referências `[R1]…` e avisos.
5. Tratamento de entradas inválidas e bloqueio de dados pessoais (CPF, e-mail, telefone).

## Como executar

```bash
python main.py                          # assistente (menu interativo)
python calculos/gerar_relatorio.py      # regenera tabelas e gráfico em resultados/
python -m unittest discover -s tests -v # testes automatizados
```

Integração com o restante do Citizen Assist AI: `from energia.assistente import responder` → retorna `texto`, `referencias`, `nivel`, `aviso`.

## Estrutura

```
main.py                  menu do assistente
energia/                 calculos.py · assistente.py · validacao.py · referencias.py
dados/                   parametros.json (cada premissa com status ESTIMADO/PÚBLICO) · consumo_residencia_modelo.csv
calculos/                gerar_relatorio.py
resultados/              CSVs, comparação (md) e gráfico gerados
tests/                   testes automatizados
docs/                    contexto, análise de consumo, comparação, justificativas, referências, uso de IA
testes_usuarios/         roteiro, registro e ajustes dos testes com usuários
entrega/                 modelo do arquivo .txt da entrega
```

## Testes com usuários
Os testes foram **simulados com personas fictícias**, conforme autorização do professor; as respostas do assistente foram executadas de verdade e os ajustes feitos estão em `testes_usuarios/simulacao/LEIA-ME_SIMULACAO.md`. O roteiro para testes com pessoas reais continua disponível em `testes_usuarios/roteiro_de_teste.md`.

## Resultados-chave (estimativas — veja limitações)

| Alternativa | Investimento | Economia/mês (ano 1) | Retorno | CO₂ evitado/ano |
|---|---|---|---|---|
| A — Eficiência e hábitos | R$ 140 | R$ 35,30 | ~4 meses | ~16 kg |
| B — Aquecedor solar | R$ 4.000 | R$ 40,95 | ~7,0 anos | ~23 kg |
| C — Solar FV (1,65 kWp) | R$ 7.425 | R$ 165,30 | ~3,6 anos | ~76 kg |

Detalhes: `docs/comparacao_alternativas.md` e `docs/justificativas.md`.

## Limitações (resumo)

Valores marcados ESTIMADO em `dados/parametros.json` (tarifa, irradiação, custos, hábitos) precisam ser trocados pelos dados reais do usuário. Não são garantias de economia nem orçamento. O assistente **não é canal oficial** da distribuidora, da ANEEL ou de qualquer órgão. Lista completa em `docs/justificativas.md`.
