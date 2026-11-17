# Comparação das três análises independentes

Três análises (A, B e C, esta com papel cético), conduzidas conforme os `BRIEFING.md` de cada pasta: cada uma recebeu `evidencias/`, o `rastreio.py` e as APIs públicas. Consultas feitas entre 23:51 e 23:56 UTC de 16/11/2026. Os pareceres estão em `A/`, `B/` e `C/`, junto com as consultas de cada análise (`execucoes/`, com manifesto SHA-256; o manifesto de `C/execucoes/manual/` usa caminhos relativos a `C/execucoes/` e confere a partir de lá).

## Números

| Pergunta | A | B | C (cética) |
|---|---|---|---|
| "Recuperador" cobra sabendo que é falso | 97% (93–99) | 97% (95–99) | 94% |
| Hipóteses favoráveis a ele (só C) | — | — | intermediário enganado 3%; honesto incompetente 2%; honesto competente ≤ 1% |
| R. do mesmo grupo do operador | aberta, sem número | inconclusiva | ~30%, inconclusiva |
| Polícia e emissora, 12 meses | 6% (≥ 30% do valor) | 7% (≥ 50%) | ~10% (5–20) |
| Ação cível | 2% | 3% | ~3% |
| "Recuperador" | < 1% | < 1% | < 1% |
| MED do Pix | 25% | 25% | ~25% |

As análises usaram definições diferentes de "parte relevante" (≥ 30%, ≥ 50% ou nenhuma), então os números de recuperação não são estritamente comparáveis.

## Onde as três concordaram

- mecanismo: autorização (`increaseApproval`) feita pela conta da vítima e `charge` → `transferFrom` pelo operador, 6 s depois;
- caminho: 3 lotes, 1 USDT por salto para um mesmo endereço, envio de teste de 5 USDT, segunda camada e reunião em `TEcWfh…B2f21X` (997 USDT), com 3 USDT em `TUWTzm…Fi2y`;
- nada bloqueado pela emissora; autorização ativa em 9.999.000 USDT;
- as provas do "recuperador" são falsas como prova de bloqueio. A e C classificaram todas as afirmações técnicas como falsas ou sem fundamento. B avaliou 8: 7 falsas e 1 verdadeira e trivial ("já localizei", porque o endereço do operador está no histórico público da vítima).

Os 28 hashes do gabarito aparecem nas consultas brutas de cada análise.

## Onde as análises divergem do gabarito

O gabarito define o destino como uma carteira que **simula** a carteira operacional de um serviço centralizado (`carteiras.json`). As três análises concluíram que ele **não** se comporta como serviço: pagou o TRX da segunda camada, foi abastecido pela mesma origem do operador e tem só 3 entradas. A leitura das análises é a que os dados sustentam. A encenação não conseguiu reproduzir uma carteira de serviço (ver os limites em `../PLANO.md`).

O relatório-exemplo, feito só com o `rastreio.py`, que na época listava apenas transferências de USDT, havia adotado a leitura de serviço. Contribuíram para a diferença dois fatores, que este exemplo não separa:

- **meios:** os briefings permitiam consultar a API diretamente, e foi assim que as análises viram as transações de TRX;
- **independência:** quem montou a encenação conhecia o papel pretendido do destino.

A ferramenta ganhou depois o comando `abastecimento`, que mostra essas ligações.

## Achados isolados

- **B** registrou um token TRC-10 recebido pela vítima às 23:24:39, sem relação com o golpe. A afirmação de B sobre o alcance desse envio não tem consulta guardada no repositório.
- **A e B** leram o recibo da autorização (23.728 de energia sem gastar TRX da vítima), o que explica os 25 TRX intactos.
- **B** diz "cinco minutos" entre o hash apresentado (20:26:45) e o contato (20:31); pelos horários, são 4 min 15 s.

## Limites desta comparação

- As três análises foram feitas pela mesma ferramenta de IA, com briefings iguais, salvo o papel cético de C. Execuções do mesmo modelo tendem a errar do mesmo jeito, então a concordância entre elas é corroboração fraca.
- O que cada sessão acessou de fato não está registrado no repositório. Os briefings mostram o que foi pedido.
- As três recomendam registrar ocorrência no mesmo dia. O relatório-exemplo recomenda consultar advogado antes, como o protocolo.
