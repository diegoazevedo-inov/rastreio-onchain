# Parecer: análise C (caso sintético, TRON Nile)

Consultas feitas em 16/11/2026, entre 23:51 e 23:53 UTC (20:51 a 20:53 em Brasília), na rede de teste **Nile**. Usei `rastreio.py --rede nile` e chamadas diretas a `https://nile.trongrid.io`. As respostas brutas estão em `execucoes/`: uma pasta por execução do `rastreio.py`, com `saida.txt` e `MANIFEST.sha256`, e as chamadas diretas em `execucoes/manual/`, com seu próprio `MANIFEST.sha256`.

Horários: a blockchain registra em UTC. Brasília é UTC−3, então 23:24 UTC corresponde a 20:24 em Brasília. Nas tabelas, **BRT** indica horário de Brasília. Endereços longos aparecem abreviados pelos 4 primeiros caracteres depois da primeira citação.

---

## Tabela-resumo

| Pergunta | Estimativa | Base principal |
|---|---|---|
| P1. O "recuperador" cobra por uma recuperação que **sabe** ser falsa | **94%** | O "hash do bloqueio" é um salto da lavagem que ele mesmo escolheu. Ele afirma ter revogado uma autorização que só a vítima pode revogar, e ela continua ativa. |
| Hipótese: golpista consciente (golpe da recuperação) | 94% | ver seção "Papel cético" |
| Hipótese: intermediário enganado por terceiro | 3% | |
| Hipótese: honesto porém incompetente | 2% | |
| Hipótese: honesto e competente | ≤1% | refutada pela blockchain |
| Subhipótese: R. pertence ao mesmo grupo do dreno | inconclusivo (~30%) | indícios fracos, sem prova de vínculo |
| P2. Hash `1ec3c4fc…` como prova de bloqueio | **Falsa**: a transação existe, mas é uma transferência comum de 339 USDT feita antes da conversa | consulta `tx` |
| P2. Imagem "PAINEL DE RECUPERAÇÃO" | **Falsa** no conteúdo: TQ5C tem saldo 0 e não está bloqueado | consulta `estado` |
| P4. O relato é compatível com a blockchain | **Sim**. Mecanismo: autorização (`increaseApproval`) assinada pela vítima, seguida de `charge` → `transferFrom` por um contrato drenador | consultas `tx`, `transferencias` |
| P5. Onde está o valor | 997 USDT em `TEcWfhn3h7X8UYR5REz4s2w9PMA1B2f21X` e 3 USDT em `TUWTzm2dnqKuBrkkM4s3JNoecD8H1UFi2y`. **Nada bloqueado pela emissora** | consultas `seguir`, `estado` |
| P6. Recuperar parte relevante em 12 meses: polícia + emissora | **~10%** (faixa 5–20%) | |
| P6. Ação judicial cível | **~3%** | |
| P6. "Recuperador" | **<1%** | |
| P6. Devolução do Pix pelo MED | **~25%** (faixa 15–40%) | depende da rapidez da contestação |
| P7. Risco que continua ativo | **Sim**: autorização de 9.999.000 USDT ao contrato drenador, além de nova cobrança ou novo golpe por R. | consulta `allowance` |

---

## 1. Fatos verificados na blockchain (linha do tempo)

Toda linha abaixo vem de uma consulta minha. As fontes estão na última coluna.

| BRT (16/11) | Evento | Hash | Fonte |
|---|---|---|---|
| 20:19:51 | Conta `TEhWiZDs4aYvvG5bRQBfqjKPyzwepmQ2RR` criada; recebe 1.000 TRX de `TVF2Mp9QY7FEGTnr3DBpFLobA6jguHyMvi` (20:19:54) | `c04632be971be811b30a1690bfdc5046e27e4eba7dd36595304dfa0ca220b621` | `manual/txs-TEhW…json`, getaccount |
| 20:24:06 | Conta `TQ5CUe1QqQmRvd7Vx8gTCdCnu5nAFH1twE` (o golpista; daqui em diante TQ5C) criada | — | `manual/getaccount-TQ5C…json` |
| 20:24:09 | TEhW → TQ5C: 500 TRX | `b19f6cc90119ca2b8c84b821431c40e9962d13177f1410a715cfd9c583dcd145` | `manual/txs-TEhW…json` |
| 20:24:15 | TEhW → TEcW: 150 TRX | `b577e853606766b932f2023f159f183b5e6ab313f4842b6e4df5e8ecdf465304` | idem |
| 20:24:21 | TEhW → vítima `TXXj87UjQReAAvu49t1N3Gs9NuXFSgQ8np`: **1.000 USDT** | `d23cbcdce5a553695dd80996b807d55e14fc015b4686c72f60420c984ab39867` | `rastreio tx`, `transferencias` |
| 20:24:27 | TQ5C implanta o contrato `TCdNNrHkXBaxxSaD1beacDwmjMjEzDpof4`, de nome **"DrenadorTeste"**. Funções: `charge(usuario, valor)`, `dono()`, `token()`. `dono()` = TQ5C; `token()` = USDT de teste | `74ef2aa2991d613276895a01afad4fec5b1f0f748ff93a64fc86496e1ed0a950` | `manual/getcontract-TCdNN.json`, `const-dono.json`, `const-token.json` |
| 20:24:33 | TQ5C → vítima: 25 TRX | `0669f1e5044599de8807ce4b71b2b73c8400199fde73da2134afcbb1f7f11755` | `manual/txs-TXXj…json` |
| 20:24:39 | **A vítima assina** `increaseApproval(TCdNN…, 10.000.000 USDT)` | `8d4bfd76c85e94f8db9ce61746dfa1eddc15725aa653e240f30700a9c0a77a9a` | `rastreio tx` |
| 20:24:45 | **TQ5C assina** `charge(vítima, 1.000)` no contrato TCdNN. Evento `Transfer` de 1.000 USDT, da vítima para TQ5C | `40d6399f352f717154d7caf9c5364d2720bf41aee5d453e71fabf0df16f8a1b5` | `rastreio tx` |
| 20:24:51–20:25:03 | TQ5C envia 40 TRX (para pagar taxas) a cada um dos 3 endereços do 1º salto | `d7a567ef…`, `5a6a1193…`, `a73987fc…` | `manual/txs-TQ5C…json` |
| 20:25:09–20:25:21 | TQ5C divide o valor: 410 → `TUDB9jNJfoZ7J5PmgswXuL4pMYMCDg3pHn`, 340 → `TG5VrrxsrLccFNBQMs8KAxyzhkkpyqjUTr`, 250 → `TK7M7XeizZENZZvvBRtqDQAwtyezL1xfSp` | `e313a2ce…`, `fe3a96b2…`, `78461df6…` | `rastreio seguir` |
| 20:25:27–20:25:39 | **TEcW** (destino final) envia 30 TRX (para pagar taxas) a cada um dos 3 endereços do 2º salto | `66198476…`, `12b220ca…`, `2e4d7751…` | `manual/txs-TEcW…json` |
| 20:25:45–20:26:33 | Cada endereço do 1º salto paga 1 USDT a TUWTz, faz um envio de teste de 5 USDT e manda o resto ao 2º salto: TUDB → `TQZ35NhWNu2E9fKmNNvcbjLkUKzinsRSN7` (409), TG5V → `TSFLcR7iE9Bvw35JBhX4E9aQFAZmccRnix` (339), TK7M → `TAmsXHxvLG2XaAMn1JKMjtkjSWUWkhgiGn` (249) | ver a seção 5 | `rastreio seguir` |
| 20:26:39–20:26:51 | 2º salto → TEcW: 409 (`73ac6075…`), **339 (`1ec3c4fc…`)**, 249 (`2f82638e…`) | | `rastreio transferencias TEcW` |
| 20:31 | A vítima procura R. (conversa) | — | conversa |
| 20:36 | R. apresenta `1ec3c4fc…` como "hash do bloqueio" | — | conversa |
| 20:42 | Pix de R$ 560,00 para R. | — | relato e conversa (não verificável por mim) |

Situação no momento da consulta (23:52:36 UTC, 20:52 BRT), comando `estado`:

- vítima: 0 USDT, **não** bloqueada; 25 TRX (getaccount);
- TQ5C, todos os endereços intermediários e o contrato TCdNN: 0 USDT, **não** bloqueados;
- **TEcW: 997 USDT, não bloqueado**;
- TUWTz: 3 USDT, não bloqueado. A conta nunca foi ativada: zero transações próprias (`manual/txs-TUWT…json`).

Autorização vigente (comando `allowance`, 23:52:06 UTC): **vítima → TCdNN: 9.999.000 USDT**, ou seja, os 10.000.000 autorizados menos os 1.000 já gastos. Vítima → TQ5C: 0. A vítima não assinou nenhuma transação depois das 20:24:39 BRT; a lista completa tem 3 transações (`manual/txs-TXXj…json`).

O contrato USDT de teste (`TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf`, nome "TetherToken", dono `TKGRE6oiU3rEzasue4MsB6sCXXSTx9BAe3`) tem as funções `addBlackList`, `isBlackListed` e `destroyBlackFunds` (`manual/getcontract-USDT.json`). Um bloqueio pela emissora seria, portanto, uma chamada `addBlackList` assinada pelo dono do contrato, e apareceria como `isBlackListed = true`.

---

## 2. P1: Probabilidade de o "recuperador" saber que a recuperação é falsa: **94%**

**Fatos:**

1. O hash que R. chama de "bloqueio" (`1ec3c4fc…`) é uma **transferência comum** (`transfer`) de 339 USDT. Foi assinada pela chave de TSFL e enviada a TEcW, às 20:26:45 BRT. Ou seja, aconteceu **4 minutos antes** de a vítima procurar R. (20:31) e quase 10 minutos antes de ele dizer "fiz o bloqueio **agora**" (20:36).
2. Essa transação não é aleatória: é **um dos três saltos finais da lavagem** do valor da vítima.
3. Às 20:34 R. afirma que os 1.000 USDT "continuam parados na carteira do golpista". TQ5C já estava zerada desde 20:25:21 BRT.
4. R. diz que "cancelou a permissão". A autorização continua em 9.999.000 USDT. Além disso, só a dona da conta pode reduzir a própria autorização: `approve` e `decreaseApproval` exigem a assinatura dela.
5. Nenhum endereço do caminho está bloqueado (`isBlackListed = não` em todos).

**Inferência:** para escolher o hash `1ec3c4fc…`, alguém acompanhou o dinheiro por pelo menos três saltos até TEcW. Quem fez isso **viu** que o valor não estava "parado" em TQ5C, e mesmo assim afirmou o contrário e cobrou por um "desbloqueio". Isso é incompatível com engano de boa-fé por parte de quem escolheu o hash. Há três explicações possíveis: R. escolheu o hash pessoalmente, alguém o forneceu a ele, ou ele tem ligação com quem fez a lavagem. As duas primeiras levam ao golpe consciente; só a segunda abre espaço para "R. enganado", e por isso essa hipótese recebe uma fatia pequena. Somam-se os sinais clássicos de golpe de taxa antecipada: "100% de êxito", taxa de 10% por Pix, "não precisa de polícia" e prazo de 24 horas.

---

## 3. Papel cético: hipóteses favoráveis a R.

| Hipótese | Prob. | O que a sustentaria | O que a derruba |
|---|---|---|---|
| **H4. Honesto e competente** | ≤1% | Nada na evidência | Bloqueio inexistente (`estado`); autorização intacta (`allowance`); hash anterior à conversa |
| **H2. Honesto porém incompetente** (não sabe ler a blockchain e acredita que fez algo) | 2% | O jargão confuso ("senha vazou") combina com incompetência | Alguém incompetente não acharia por acaso, entre milhões de transações, justamente um salto da lavagem. E não diria que a Tether "devolve pro golpista" se houver polícia: isso não é incompetência, é desestimular a denúncia |
| **H3. Intermediário enganado por terceiro** (repassa o "painel" e o hash de alguém que o enganou, e recebe o Pix para essa pessoa) | 3% | Explicaria um hash escolhido por quem conhece o caminho sem que R. saiba o que significa | R. fala em primeira pessoa ("fiz o bloqueio", "cancelei a permissão") e promete resultado ("100%"). Mesmo enganado, estaria cobrando por algo cujo funcionamento não conhece. Continua sendo uma hipótese possível para o caso de R. ser uma conta "laranja" |
| **H1. Golpista consciente** (golpe da recuperação) | 94% | Tudo o que está nas seções 2, 4 e 5 | — |

Subhipótese dentro de H1, **R. é do mesmo grupo que drenou a carteira**: inconclusiva, ~30%. A favor: conhecimento rápido do caminho exato da lavagem, 5 minutos depois do primeiro contato. Contra: o caminho é público e fácil de seguir com um explorador, e golpistas de recuperação costumam ser operações separadas que monitoram vítimas em redes sociais. Não há na blockchain nenhuma ligação entre R. e os endereços (R. não tem endereço conhecido; recebeu por Pix).

---

## 4. P2: Provas apresentadas por R.

| Prova | Classificação | Motivo técnico | Consulta |
|---|---|---|---|
| Hash `1ec3c4fc066243fc806eb504170d512b52795bf40f7964edc6be285038bdf77e` ("hash do bloqueio") | **Falsa como prova de bloqueio** (a transação é real, mas tem outro significado) | Tipo `TriggerSmartContract`, chamada `transfer(TEcW…, 339 USDT)`, assinada por TSFL, bloco 72776828, 23:26:45 UTC (20:26:45 BRT). Não é `addBlackList` e não foi assinada pelo dono do contrato USDT (`TKGRE6…`). É anterior à conversa e faz parte da lavagem | `rastreio tx 1ec3c4fc…`; `rastreio transferencias TEcW…` |
| Imagem "PAINEL DE RECUPERAÇÃO": "Carteira TQ5CUe1… · 1.000,00 USDT · STATUS: RETIDO", selo "bloqueio ativo" | **Falsa** (o conteúdo contradiz a blockchain) | TQ5C tem saldo 0 USDT e `isBlackListed = não`, e não tem USDT desde 20:25:21 BRT. Um bloqueio real apareceria no próprio contrato, não num "painel" privado, e mostraria 997 em TEcW, não 1.000 em TQ5C. Observação: analisei a **descrição** da imagem, não o arquivo; isso não muda a conclusão, porque o conteúdo descrito é verificável e é falso | `rastreio estado`; `rastreio transferencias TQ5C…` |

O comprovante de Pix é prova da vítima, não de R., e não tenho como verificá-lo.

---

## 5. P3: Afirmações técnicas de R.

| # | Afirmação | Veredito | Por quê (com consulta) |
|---|---|---|---|
| 1 | "Sua carteira foi hackeada, sua senha vazou" | **Falsa** | A única transação de saída assinada pela vítima é a autorização `8d4bfd76…`. A retirada `40d6399f…` foi assinada por TQ5C, usando essa autorização (`charge` → `Transfer` vítima→TQ5C; a autorização caiu de 10.000.000 para 9.999.000). Quem tivesse a chave da vítima simplesmente faria um `transfer` assinado por ela, sem precisar de autorização nem de contrato. As permissões de dono e ativa da conta continuam com a chave da própria vítima (`manual/getaccount-TXXj…json`) |
| 2 | "Tenho 100% de êxito" | **Falsa** na prática / não verificável | Não existe mecanismo que garanta recuperação: congelamento depende da emissora e de ordem de autoridade |
| 3 | "Os 1.000 USDT continuam parados na carteira do golpista, ele ainda não conseguiu mexer" (20:34) | **Falsa** | TQ5C transferiu tudo entre 20:25:09 e 20:25:21 BRT (`e313a2ce…`, `fe3a96b2…`, `78461df6…`); saldo 0 |
| 4 | "Fiz o bloqueio agora", com o hash | **Falsa** | Ver a seção 4. Além disso, um particular não consegue bloquear USDT: só o dono do contrato chama `addBlackList` |
| 5 | "Cancelei a permissão que o golpista tinha" | **Falsa** e **impossível** para terceiros | `allowance` vítima→TCdNN = 9.999.000 USDT (23:52:06 UTC). Só a vítima pode revogar, e ela não assinou nada depois das 20:24:39 |
| 6 | "Pode voltar a usar sua carteira normalmente" | **Falsa e perigosa** | Com a autorização ativa, qualquer USDT que entrar na carteira pode ser levado por `charge` |
| 7 | "Está tudo congelado pela Tether" | **Falsa** | `isBlackListed = não` em TQ5C, TEcW e em todos os intermediários; 997 USDT livres em TEcW |
| 8 | "Para liberar, a plataforma cobra 10%"; "é o único custo" | **Falsa** (não técnica, mas falsa quanto ao funcionamento) | A emissora não cobra "taxa de liberação" de vítimas. O congelamento e a eventual reemissão passam por pedido de autoridade. Não existe "plataforma" intermediária |
| 9 | "Não precisa de polícia nem de advogado, só atrasa e a Tether devolve pro golpista" | **Falsa** | É o contrário: a emissora atua por pedido de autoridade policial ou judicial. Registrar a ocorrência não "devolve" nada ao golpista |
| 10 | "Em até 24 horas cai na sua carteira" | **Falsa** | Nada está bloqueado e não há processo em curso. E, mesmo que algo fosse enviado à carteira da vítima, a autorização ativa permitiria ao drenador retirá-lo |

---

## 6. P4: O relato é compatível com a blockchain? Qual o mecanismo?

**Compatível, sim.**

| Relato | Blockchain |
|---|---|
| "Por volta das 20h20 abriu um link" | Autorização às 20:24:39 BRT |
| "Conectar a carteira" e depois "confirmar o recebimento do bônus"; reconhecimento facial | A "confirmação" foi a assinatura de `increaseApproval(TCdNN, 10.000.000)`. O rosto só desbloqueou a assinatura no aplicativo; não houve vazamento de senha |
| "Não digitou senha nem palavras de recuperação" | Compatível: o golpe não precisou da chave. A retirada foi assinada pela chave do golpista |
| "Pouco depois o saldo estava zerado" | `charge` 6 segundos depois (20:24:45) |
| "Ainda tem algum TRX" | 25 TRX (getaccount) |

**Mecanismo (fato):** golpe de **autorização** (*approval phishing*). Primeiro, a vítima assinou uma autorização de gasto praticamente ilimitada para o contrato `TCdNN…` ("DrenadorTeste", implantado por TQ5C 12 segundos antes). Depois, TQ5C chamou `charge(vítima, 1.000)` e o contrato executou um `transferFrom` usando essa autorização.

**Pontos que não batem bem e exigiriam esclarecimento num caso real (fato, depois inferência):**

- O mesmo endereço **TEhW** que mandou os 1.000 USDT à vítima ("comprados pouco antes") também abasteceu com TRX o golpista TQ5C (500 TRX) e o destino final TEcW (150 TRX), minutos antes.
- Os 25 TRX da vítima vieram **do próprio golpista** TQ5C, 6 segundos antes da autorização.
- A conta da vítima só foi ativada às 20:24:30 BRT.

Inferência: num caso real, isso indicaria que o "vendedor" do USDT faz parte do esquema (uma venda P2P usada como isca), ou que o relato está incompleto. Neste exercício, o mais provável é que seja efeito da montagem do cenário na rede de teste, em que um único operador abasteceu todas as contas. Registro o fato sem tirar conclusão contra a vítima.

---

## 7. P5: Onde está o valor, por qual caminho, e há bloqueio?

**Caminho (fato, `rastreio seguir TQ5C --desde 2026-11-16T23:20:00 --saltos 5`):**

```
vítima TXXj87… ──1.000 (40d6399f…)──▶ TQ5C
TQ5C ─410 (e313a2ce…)─▶ TUDB ─┬─ 1 (006fb48a…) ─▶ TUWTz
                              ├─ 5 (0ed9653a…) + 404 (d402f694…) ─▶ TQZ35 ─409 (73ac6075…)─▶ TEcW
TQ5C ─340 (fe3a96b2…)─▶ TG5V ─┬─ 1 (5a71864d…) ─▶ TUWTz
                              ├─ 5 (637c01ff…) + 334 (767a2f87…) ─▶ TSFL ─339 (1ec3c4fc…)─▶ TEcW
TQ5C ─250 (78461df6…)─▶ TK7M ─┬─ 1 (b45e4ca7…) ─▶ TUWTz
                              ├─ 5 (798bb149…) + 244 (863f0173…) ─▶ TAms ─249 (2f82638e…)─▶ TEcW
```

**Onde está hoje (23:52:36 UTC):**

- **997 USDT em `TEcWfhn3h7X8UYR5REz4s2w9PMA1B2f21X`**, sem nenhuma saída de USDT;
- **3 USDT em `TUWTzm2dnqKuBrkkM4s3JNoecD8H1UFi2y`**, conta não ativada, provável "pedágio" do operador;
- soma: 1.000.

**Bloqueio pela emissora: não.** `isBlackListed = não` para todos os 12 endereços consultados.

**Inferências:**

- TEcW **não** parece corretora nem carteira de serviço. Tem só 3 entradas e 5 transações próprias, e foi ela quem pagou as taxas dos endereços do 2º salto (30 TRX para TQZ35, TSFL e TAms). Ou seja, TEcW, TQ5C e os intermediários são controlados pelo mesmo operador.
- Ponto positivo: o valor está consolidado num único endereço que não é de serviço. É a melhor situação possível para um pedido de congelamento. Ponto negativo: pode ser movido a qualquer momento.

---

## 8. P6: Probabilidade de recuperação em 12 meses

Tratando o caso como se fosse na rede principal, com valor real (cerca de US$ 1.000):

| Caminho | Prob. | Justificativa |
|---|---|---|
| **Polícia + emissora** (congelar TEcW e depois reemitir à vítima) | **~10%** (5–20%) | A favor: valor parado e consolidado; a emissora congela endereços a pedido de autoridade e já reemitiu valores a vítimas. Contra: o pedido policial costuma levar dias ou semanas e o operador já mostrou que move rápido (lavagem em 2 minutos). Congelar não é devolver: a reemissão exige um segundo pedido formal. O valor baixo também reduz a prioridade |
| **Ação judicial cível** | **~3%** | Réu não identificado. O custo é comparável ou maior que o valor. Só ganha sentido se o valor chegar a uma corretora com cadastro (KYC), que possa ser oficiada |
| **"Recuperador"** | **<1%** | Não fez nada na blockchain; as afirmações são falsas (seções 4 e 5) |
| **MED (devolução do Pix de R$ 560)** | **~25%** (15–40%) | O MED cobre fraude, e o pedido pode ser feito pelo aplicativo do banco. O fator decisivo é haver saldo na conta recebedora quando o bloqueio cautelar acontecer. Golpistas costumam esvaziá-la em minutos. A chance sobe muito se a contestação for feita **hoje à noite** e cai rápido a cada hora. As regras recentes do Banco Central (autoatendimento e rastreio para contas seguintes) ajudam, mas a vigência e o alcance exatos devem ser confirmados com o banco |

---

## 9. P7: Providências, em ordem

1. **Agora: parar de interagir com R.** Não pagar mais nada (a próxima cobrança é previsível: "taxa de saque", "imposto", "taxa antirrobô"). Não informar palavras de recuperação, não instalar aplicativos, não "conectar a carteira" a nenhum "painel". Não apagar a conversa: salvar capturas com data e hora, o perfil de R. e o link do site do "bônus".
2. **Agora: contestar o Pix pelo MED** no aplicativo do banco, ou pelo telefone, como **fraude/golpe**. Pedir o bloqueio cautelar e anotar o protocolo. É o passo mais sensível ao tempo.
3. **Hoje: neutralizar a autorização.** Não mandar USDT para `TXXj87…`. Revogar a autorização com `approve(TCdNN…, 0)`, pelo gerenciador de autorizações da carteira ou de um explorador confiável; a vítima tem 25 TRX para a taxa. Usar uma **carteira nova**, com frase de recuperação nova, para qualquer uso futuro. Quem assina é a própria vítima: este parecer não assinou nada.
4. **Em 24 horas: registrar boletim de ocorrência** (delegacia de crimes cibernéticos ou delegacia online), cobrindo **os dois fatos**: (a) o dreno por fraude eletrônica e (b) o estelionato do "recuperador" (chave Pix, nome do favorecido no comprovante, perfil). Anexar a linha do tempo e os hashes deste parecer, e pedir expressamente que a autoridade **solicite à emissora o congelamento de `TEcWfhn3h7X8UYR5REz4s2w9PMA1B2f21X`** (e de `TUWTz…`).
5. **Em seguida:** notificar a emissora pelo canal de suporte, informando o número do BO (ela age por pedido de autoridade, mas o aviso deixa o caso registrado). Denunciar o perfil de R. e o link do "bônus" à rede social. Informar a desenvolvedora da carteira.
6. **Acompanhar** `TEcW…` (saldo e `isBlackListed`). Se o valor chegar a uma corretora, informar a polícia para que ela oficie a corretora.
7. **Esperar novas abordagens** de outros "recuperadores" ou de falsos "advogados/agentes da Tether" e recusá-las.

**Riscos que continuam ativos:**

- **Autorização de 9.999.000 USDT** de `TXXj87…` para `TCdNN…`. Qualquer USDT que entrar é retirável pelo drenador. R. disse o contrário ("pode usar normalmente"), o que agrava o risco. O TRX da vítima não é alcançado por essa autorização, que vale só para o token USDT.
- **R.**: nova cobrança, pedido de frase de recuperação ou indicação de outro "painel" que peça nova autorização. Ele também tem dados bancários da vítima, que aparecem no Pix, e pode usá-los para engenharia social.
- **O link do "bônus"** pode continuar no ar e pedir novas assinaturas.

---

## 10. P8: Que evidência mudaria os números

| Número | Subiria se… | Desceria se… |
|---|---|---|
| P1 (94%), golpista consciente | R. pedir nova taxa ou a frase de recuperação; o mesmo perfil aparecer em outros relatos; a chave Pix estar em nome de terceiro ("laranja") | Prova de que R. recebeu o hash de outra pessoa e repassou de boa-fé (aumenta H3). Devolução espontânea do Pix. Registro verificável de pedido real de R. a uma autoridade ou à emissora |
| Subhipótese "mesmo grupo" (~30%) | Ligação entre a chave Pix de R. e algum endereço ou serviço usado pelo drenador; R. ter sido indicado no mesmo link do "bônus" | R. ser identificado como golpista de recuperação atuando com muitas vítimas de golpes diferentes |
| Polícia + emissora (~10%) | `isBlackListed(TEcW) = true`; BO feito hoje e pedido à emissora em poucos dias; valor ainda parado | Saída de USDT de TEcW, sobretudo para ponte entre redes, misturador ou troca por outro ativo |
| Ação judicial (~3%) | Valor chegar a corretora com cadastro e ser bloqueado lá | Valor sair do USDT ou do sistema regulado |
| MED (~25%) | Contestação nas primeiras horas; banco confirmar bloqueio cautelar com saldo | Contestação depois de dias; conta recebedora esvaziada; banco entender que foi "pagamento por serviço" e não fraude |
| Relato compatível (P4) | Comprovante da compra dos 1.000 USDT mostrando um vendedor sem ligação com TEhW | Indício de que a vítima conhecia TEhW ou TQ5C (o que mudaria a leitura do caso) |

---

## Limites deste parecer

- **Rede de teste.** Tudo foi consultado na TRON Nile, onde o USDT não tem valor e a "emissora" de teste não é a Tether. As probabilidades da P6 imaginam o mesmo caso na rede principal e são estimativas de julgamento, não frequências medidas.
- **Retrato de um instante.** Saldos, bloqueios e autorizações foram lidos entre 23:51 e 23:53 UTC de 16/11/2026 e podem mudar a qualquer momento.
- **Fonte única.** Todas as leituras vieram da TronGrid (nile.trongrid.io), sem conferência em um segundo nó ou explorador independente.
- **Código do contrato.** Li a ABI e as funções `dono()`/`token()` do contrato `TCdNN…`, mas não descompilei o bytecode. A conclusão de que `charge` executa `transferFrom` se apoia no efeito observado (evento `Transfer` vítima→TQ5C e redução da autorização em exatamente 1.000), não no código-fonte.
- **Material não verificável.** A conversa, a imagem (vi só a descrição), o comprovante de Pix e o relato da vítima, que é de segunda mão, não podem ser conferidos na blockchain. Também não tenho acesso a dados bancários, à identidade de R. nem ao site do "bônus".
- **Atribuição.** A blockchain mostra que os endereços TQ5C, TEcW e os intermediários agem de forma coordenada, mas não diz quem os controla, nem liga R. a eles.
- **Sem acesso a outras análises.** Este é um trabalho independente; não consultei relatórios anteriores nem outras análises do caso, não contatei ninguém e não assinei nem enviei transações.
- **Regras do MED.** A descrição do MED segue o funcionamento geral conhecido; prazos e alcance atuais devem ser confirmados com o banco da vítima.
