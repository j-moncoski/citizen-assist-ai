# Testes SIMULADOS (personas fictícias) — NÃO são testes com pessoas reais

**Status:** simulação feita a pedido do grupo, que informou ter autorização do professor para usar testes simulados no lugar de testes com pessoas reais. **Guardem essa autorização por escrito** (e-mail, print do Teams/portal) e mencionem no vídeo e no README que os testes foram simulados.

**O que é real e o que é fictício**
- **Fictício:** as 5 personas (SIM-1 a SIM-5) e as perguntas que elas "fariam".
- **Real:** as respostas, as classificações de intenção, o nível de confiança e o tempo de resposta — foram obtidos executando o assistente (`python testes_usuarios/simulacao/rodar_simulacao.py`). Não há comentários de pessoas reais, notas de facilidade nem tempos de uso humano.

## Resultados
| Execução | Acerto de intenção | Arquivo |
|---|---|---|
| 1ª (antes dos ajustes) | 12/16 = 75% | `resultado_simulacao_antes_dos_ajustes.csv` |
| 2ª (depois dos ajustes) | 16/16 = 100% | `resultado_simulacao.csv` |

**Ressalva:** os 100% foram obtidos ajustando o assistente com as mesmas 16 perguntas; isso mostra que as falhas foram corrigidas, mas **não** mede desempenho em perguntas novas. Com usuários reais o acerto tende a ser menor.

## Situações testadas e ajustes realizados (reais, no código)
| # | Pergunta (persona) | Problema observado na execução | Ajuste | Onde |
|---|---|---|---|---|
| 1 | "como economizar sem gastar dinheiro" (SIM-1) | classificada como *consumo* (palavra "gastar") | adicionadas palavras "sem gastar" e "dica" à intenção *eficiência* | `energia/assistente.py` |
| 2 | "tem como zerar minha conta de luz?" (SIM-2) | classificada como *consumo* | adicionada "zerar" à intenção *solar* | idem |
| 3 | "solar polui menos mesmo?" (SIM-4) | caía em *solar*, não em *emissão* ("poluicao" não casava com "polui") | palavra-chave trocada para "polui"; *emissão* passou a ter prioridade sobre *solar* em empate | idem |
| 4 | "aquecedor solar ou painel, qual compensa mais" (SIM-5) | caía em *solar* | adicionadas " ou " e "baixar a conta" à intenção *comparar*, que passou a ter prioridade sobre *solar* em empate | idem |
| 5 | "posso confiar que vou economizar isso tudo?" (SIM-5) | caía em *comparar* | adicionadas "posso confiar" e "vou economizar" à intenção *limites* | idem |

Cada caso corrigido virou teste de regressão (`TestRegressaoSimulacao` em `tests/test_assistente.py`).

Também foram verificados: pergunta com CPF (SIM-5) é bloqueada com aviso de privacidade; pedido de ajuda e pergunta fora do escopo recebem resposta segura.
