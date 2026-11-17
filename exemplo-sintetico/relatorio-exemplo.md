# Relatório de rastreamento: exemplo sintético

> **Exemplo sintético.** As transações são reais na rede de teste Nile, sem valor financeiro, e foram encenadas para este exemplo (`encenar.py`). A vítima "V.", o "recuperador" "R.", a conversa e o Pix são fictícios (`evidencias/`). Os fatos on-chain abaixo saem das consultas guardadas em `execucoes/`, citadas pelo nome da pasta, e das consultas das três análises independentes, em `analises/`. O relatório foi redigido por quem montou a encenação e, portanto, conhecia os papéis pretendidos; o gabarito (`encenacao.json`) serve para conferi-lo (seção 8).

Horários em UTC, com o horário de Brasília (UTC−3) entre parênteses quando é preciso compará-los com a conversa.

## 1. Conclusão

- **O que aconteceu:** V. assinou, com a confirmação biométrica do celular, uma **autorização de gasto** de 10.000.000 USDT a um contrato. Seis segundos depois, o dono desse contrato retirou os 1.000 USDT. Não houve uso de senha: o relato dela é compatível com a blockchain.
- **Onde está o valor:** em cerca de dois minutos, o valor foi dividido em três lotes, passou por uma segunda camada de endereços e voltou a se juntar num único endereço, que guarda **997 USDT**. Os outros 3 USDT foram para um endereço que cobra 1 USDT por salto. **O endereço final pertence, ao que tudo indica, ao próprio operador do golpe, e não a uma corretora** (seção 3). Por isso o valor ainda não se misturou com o de terceiros.
- **Bloqueio:** **nenhum** endereço do caminho está bloqueado pela emissora.
- **O "recuperador":** as seis afirmações técnicas de R. conferidas contra a blockchain são **falsas** (seção 5). O "hash do bloqueio" é uma transferência comum do próprio caminho, anterior ao primeiro contato de V. com ele.
- **O que fazer primeiro:** não pagar mais nada a R. nem avisá-lo, pedir hoje o MED do Pix de R$ 560,00, abandonar a carteira, cuja autorização segue ativa, e procurar um advogado antes de ir à polícia (seção 6).

As três análises independentes (anexos em `analises/A`, `B` e `C`; a C com papel cético) chegaram às mesmas respostas para o mecanismo, o caminho e o bloqueio. As estimativas são juízo de cada análise, não medição.

| Pergunta | Análise A | Análise B | Análise C (cética) | Diagnóstico |
|---|---|---|---|---|
| R. cobra por uma recuperação que sabe ser falsa? | 97% | 97% | 94% | **94–97%.** A hipótese favorável a R. mais forte, intermediário enganado por terceiro, recebeu 3% da análise C |
| O relato de V. é compatível com a blockchain? | Sim | Sim | Sim | Sim: drenagem por autorização assinada por ela |
| Há valor bloqueado pela emissora? | Não | Não | Não | Não |
| O endereço final é de um serviço centralizado (corretora)? | Não: mesmo operador | Não: circuito fechado | Não: mesmo operador | Não. Ele pagou o TRX da segunda camada e foi abastecido pela mesma origem do operador |
| Recuperar parte relevante em 12 meses, por polícia e emissora | 6% (≥ 30% do valor) | 7% (≥ 50%) | ~10% | **6–10%, baixa.** O valor parado num só endereço é o fator a favor; a demora do pedido de congelamento, o contra |
| Idem, por ação cível | 2% | 3% | ~3% | 2–3% |
| Idem, pelo "recuperador" | < 1% | < 1% | < 1% | < 1% |
| Devolução do Pix pelo MED | 25% | 25% | ~25% | ~25%; cai a cada hora de atraso |

## 2. Como foi a perda (UTC)

| Quando | O que aconteceu | Prova |
|---|---|---|
| 23:24:21 | V. recebe 1.000 USDT de `TEhWiZ…mQ2RR` (a "compra") | `20261116-232818-transferencias`, hash `d23cbcdc…` |
| 23:24:33 | `TQ5CUe…1twE` envia **25 TRX** a V. ("aluguel de energia": paga a assinatura seguinte) | `20261116-234315-tx`, hash `0669f1e5…` |
| 23:24:39 (20:24:39) | **V. assina** `increaseApproval(TCdNNr…pof4, 10.000.000 USDT)` | `20261116-232819-tx`, hash `8d4bfd76…`, feita pela conta `TXXj87…Q8np` com a permissão de dono |
| 23:24:45 (20:24:45) | `TQ5CUe…1twE` chama `charge(V., 1.000)` no contrato `TCdNNr…pof4`, que transfere os 1.000 USDT de V. para `TQ5CUe…1twE` | `20261116-232816-tx`, hash `40d6399f…` |

Quem assinou a perda não foi V., e sim `TQ5CUe…1twE`, usando a autorização que V. tinha assinado 6 segundos antes. O mesmo endereço enviou o TRX a V., implantou o contrato e retirou o USDT. A partir daqui ele é chamado de **operador**.

## 3. O caminho dos valores

Consulta `20261116-232831-seguir`, com o endereço de taxa excluído. A primeira passada, sem exclusões (`20261116-232822-seguir`), mostra que `TUWTzm…Fi2y` recebe exatamente 1 USDT de cada intermediária e não repassa nada: é o padrão de cobrança por salto, e por isso foi excluído.

| Hora (UTC) | De | Para | Valor (USDT) | Hash | Observação |
|---|---|---|---|---|---|
| 23:24:45 | V. `TXXj87…Q8np` | operador `TQ5CUe…1twE` | 1.000 | `40d6399f…` | Perda |
| 23:25:09 | operador | `TUDB9j…3pHn` | 410 | `e313a2ce…` | Lote 1 |
| 23:25:15 | operador | `TG5Vrr…qjUTr` | 340 | `fe3a96b2…` | Lote 2 |
| 23:25:21 | operador | `TK7M7X…L1xfSp` | 250 | `78461df6…` | Lote 3; o operador fica com 0 |
| 23:25:45 / 26:03 / 26:21 | cada intermediária | `TUWTzm…Fi2y` | 1 cada | `006fb48a…` `5a71864d…` `b45e4ca7…` | Taxa fixa por salto (excluída) |
| 23:25:51 → 23:25:57 | `TUDB9j…3pHn` | `TQZ35N…sRSN7` | 5, depois 404 | `0ed9653a…` `d402f694…` | Envio de teste, depois o restante |
| 23:26:09 → 23:26:15 | `TG5Vrr…qjUTr` | `TSFLcR…Rnix` | 5, depois 334 | `637c01ff…` `767a2f87…` | Idem |
| 23:26:27 → 23:26:33 | `TK7M7X…L1xfSp` | `TAmsXH…hgiGn` | 5, depois 244 | `798bb149…` `863f0173…` | Idem |
| 23:26:39 | `TQZ35N…sRSN7` | `TEcWfh…B2f21X` | 409 | `73ac6075…` | Repasse integral em menos de um minuto |
| 23:26:45 | `TSFLcR…Rnix` | `TEcWfh…B2f21X` | 339 | `1ec3c4fc…` | Idem |
| 23:26:51 | `TAmsXH…hgiGn` | `TEcWfh…B2f21X` | 249 | `2f82638e…` | Idem |

Conferência das somas: 409 + 339 + 249 = 997 USDT no destino (`20261116-232840-transferencias`), mais 3 × 1 USDT de taxa = 1.000.

**Quem é o destino `TEcWfh…B2f21X`.** Pelo padrão da segunda camada (valor de teste, restante e repasse integral), a leitura só pelas transferências de USDT seria a de endereços de depósito de uma corretora, com `TEcWfh…B2f21X` como carteira operacional dela. As transações de TRX, consultadas pelas três análises, mostram que essa leitura não se sustenta:

- `TEcWfh…B2f21X` **enviou 30 TRX a cada endereço da segunda camada** entre 23:25:27 e 23:25:39, antes de eles lhe repassarem o USDT;
- ele próprio foi abastecido com 150 TRX por `TEhWiZ…mQ2RR`, a mesma origem que deu 500 TRX ao operador, às 23:24:15;
- só tem 3 entradas de USDT.

Fontes: `analises/A/execucoes/manual-historico`, `analises/B/execucoes/20261116-manual-api` (M06, M07) e `analises/C/execucoes/manual` (txs de `TEcWfh` e `TEhWiZ`). Depois das análises, o `rastreio.py` ganhou o comando `abastecimento`, que mostra as mesmas ligações (`20261117-003200-abastecimento`).

**Inferência:** toda a cadeia, do operador ao destino, é controlada pelo mesmo grupo. É uma lavagem em circuito fechado, e o valor ainda não passou por nenhum serviço com cadastro de clientes. Para um pedido de congelamento, esse é o melhor cenário: o saldo está inteiro num endereço só, ligado ao golpe de ponta a ponta.

## 4. Situação atual

Consulta `20261116-234319-estado`, às 23:43:19 UTC (20:43:19 em Brasília), depois da última afirmação técnica de R. (20:40). As três análises repetiram a consulta entre 23:52 e 23:56 UTC, com o mesmo resultado.

| Endereço | Bloqueado pela emissora | Saldo (USDT) |
|---|---|---|
| V. `TXXj87…Q8np` | não | 0 |
| operador `TQ5CUe…1twE` | não | 0 |
| 3 intermediárias e 3 endereços da segunda camada | não | 0 |
| destino `TEcWfh…B2f21X` | não | 997 |
| taxa `TUWTzm…Fi2y` | não | 3 |

**A autorização ainda está ativa na carteira de V.:** 9.999.000 USDT para o contrato `TCdNNr…pof4` (consulta `20261116-234408-allowance`, às 23:44:08 UTC). Qualquer USDT que entrar nessa carteira pode ser retirado de novo, sem nova assinatura.

## 5. Afirmações de terceiros × dados

| O que foi dito ou mostrado (16/11, Brasília) | O que os dados mostram | Prova |
|---|---|---|
| 20:33: "sua carteira foi hackeada, sua senha vazou" | A perda foi uma `transferFrom` executada pelo operador com base numa autorização **assinada pela própria carteira de V.** às 20:24:39. O mecanismo não exige senha nem frase de recuperação, o que é compatível com o relato. As permissões da conta de V. continuam com a chave dela, e os 25 TRX continuam lá: quem tivesse a chave teria levado também o TRX. | `20261116-232819-tx`, `20261116-232816-tx`; contas: `analises/B/execucoes/20261116-manual-api` (M03) |
| 20:34: "os 1.000 USDT continuam parados na carteira do golpista" | O operador repassou tudo entre 20:25:09 e 20:25:21, **antes** do primeiro contato de V. com R. (20:31). Saldo 0 às 20:43:19. | `20261116-232831-seguir`, `20261116-234319-estado` |
| 20:36: "fiz o bloqueio agora", com o hash `1ec3c4fc…` | O hash é uma `transfer` de 339 USDT, assinada por `TSFLcR…Rnix` para o destino, às **20:26:45**: cerca de quatro minutos antes do primeiro contato, e não "agora". Não é `addBlackList` nem nenhuma ação da emissora. É um salto comum do caminho, visível a qualquer um. | `20261116-234317-tx` |
| 20:37: imagem de "painel" com 1.000,00 USDT "retidos" em `TQ5CUe…1twE` | Às 20:37, esse endereço já estava com saldo 0 desde 20:25:21 e não está bloqueado. O painel não corresponde à blockchain. Não há na rede um "status retido" fora do bloqueio pela emissora, que dá "não". | `20261116-232831-seguir`, `20261116-234319-estado` |
| 20:38: "cancelei a permissão que o golpista tinha; pode voltar a usar a carteira" | Às 20:44:08 a autorização seguia ativa, em 9.999.000 USDT. Revogá-la exigiria uma transação feita pela própria conta de V., e não há nenhuma até 23:51:47 UTC. Seguir o conselho exporia V. a nova perda. | `20261116-234408-allowance`; `analises/B/execucoes/20261116-235147-transferencias` |
| 20:40: "está tudo congelado pela Tether" | Nenhum dos 10 endereços do caminho está bloqueado pela emissora. | `20261116-234319-estado` |
| 20:40: "a plataforma cobra 10%, R$ 560,00 por Pix, é o único custo" | Não é verificável na blockchain. Bate com os sinais 2 e 6 de `modelos/sinais-golpe-recuperacao.md` (cobrança antecipada e "taxa da plataforma"). Uma liberação pela emissora não seria paga por Pix a um particular. | conversa, 20:40 |
| 20:41: "não precisa de polícia nem de advogado" | Sinal 11. O congelamento pela emissora costuma depender de pedido de autoridade. | conversa, 20:41 |

## 6. Recomendações (em ordem)

1. **Não pagar mais nada a R. e não avisá-lo** de que o golpe foi percebido, antes de pedir a devolução do Pix.
2. **Pedir hoje o MED do Pix** de R$ 560,00, pelo aplicativo do banco de V., na conta que fez o Pix. As três análises apontam este como o passo mais sensível ao tempo.
3. **Abandonar a carteira:** a autorização de 9.999.000 USDT segue ativa. Não depositar mais nada nela. Se V. quiser revogar a autorização, que seja só pelo aplicativo oficial da carteira, nunca por link recebido.
4. **Consultar advogado de confiança**, levando este relatório.
5. **Com o advogado, registrar a ocorrência** na autoridade policial, pelos dois fatos (o desvio e o estelionato de R.), com o pedido de que a autoridade solicite à emissora o congelamento de `TEcWfh…B2f21X`, onde os 997 USDT seguem parados.
6. **Preservar as evidências:** a conversa exportada com mídia, o comprovante do Pix (nome, banco e chave do recebedor, a melhor pista de identificação de R.) e as consultas deste relatório.

## 7. Perguntas em aberto

1. De quem V. comprou os 1.000 USDT? O endereço que os enviou (`TEhWiZ…mQ2RR`) abasteceu também o operador e o destino minutos antes. Num caso real, isso apontaria para um vendedor ligado ao grupo. Neste exemplo, é efeito da montagem (seção 8).
2. Por onde chegou o link do "bônus", e o domínio ainda está no ar? Conferir só por RDAP, sem abrir o site.
3. R. é ligado ao operador ou é um segundo golpista que aproveitou a perda? Os dados on-chain não respondem. As análises deixaram a questão inconclusiva (a C estimou ~30% para "mesmo grupo").

## 8. Método e limites

- **Fontes:** API pública da rede de teste Nile (`nile.trongrid.io`), pelo `rastreio.py --rede nile` (13 consultas em `execucoes/`) e pelas consultas próprias de cada análise (em `analises/*/execucoes/`). Todas guardam as respostas brutas com manifesto SHA-256.
- **Análises independentes:** três sessões separadas, conduzidas conforme os briefings (`analises/*/BRIEFING.md`), que entregam `evidencias/`, o `rastreio.py` e as APIs públicas, e não este relatório, o gabarito nem as outras análises. O acesso efetivo de cada sessão não está registrado no repositório. O parecer de B tem uma nota editorial entre colchetes. Comparação em `analises/COMPARACAO.md`.
- **Leitura do destino:** feito só com transferências de USDT, o rastreio sugeria carteira de corretora no destino. As análises, que consultaram também as transações de TRX, mostraram que o destino é do mesmo operador (seção 3). O `rastreio.py` ganhou o comando `abastecimento`, que mostra essas ligações, e o PROTOCOLO, o passo correspondente (consulta `20261117-003200-abastecimento`). Este exemplo não separa o efeito da independência das análises do efeito de elas terem consultado mais dados.
- **Conferência automática** (`conferir.py`): valores e pontas de cada linha da seção 3 contra as transferências registradas, saldo e bloqueio da seção 4 contra a consulta `estado`, abreviações e pastas citadas. Os 28 passos do gabarito aparecem nas consultas. O `conferir.py` não confere o texto corrido, as afirmações da seção 5 nem os papéis atribuídos, que são inferência.
- **Limites da encenação:** as três análises perceberam que se trata de uma montagem. Uma única carteira abasteceu vítima, operador e destino; o contrato se chama "DrenadorTeste"; a origem dos fundos é a torneira da rede de teste. Uma carteira de serviço de verdade, com milhares de movimentos, não pode ser simulada numa rede de teste com poucas carteiras. O "recuperador" fictício só faz afirmações verificavelmente falsas; o exemplo não cobre afirmações ambíguas.
- **Correlação entre as análises:** as três foram feitas pela mesma ferramenta de IA, com briefings iguais, salvo o papel cético de C. A concordância entre elas é corroboração fraca.
- **O que não foi identificado:** a origem do link e a identidade de R.
- **Limites:** não substitui exame oficial nem orientação jurídica. Titular de carteira sem rótulo verificável é inferência. A chance de recuperar cripto desviada é baixa.
- **Uso de IA.** Todos os dados deste relatório saem de consultas a fontes públicas, com a saída de cada consulta guardada. Uma ferramenta de IA generativa (Claude, da Anthropic) foi usada sob supervisão humana para encenar o exemplo na rede de teste, fazer as consultas, rastrear os valores, conduzir as três análises independentes e redigir versões do texto. As análises (anexos A, B e C) foram feitas em sessões separadas, conforme briefings que não incluíam este relatório nem as outras análises. Cada uma refez as consultas à blockchain, e a análise C teve o papel explícito de buscar a explicação mais favorável ao "recuperador". Nenhum dado vem do modelo. O texto passou por revisão humana.
