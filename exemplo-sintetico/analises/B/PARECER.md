# Parecer técnico: análise B

Caso encenado na rede de teste TRON Nile (contrato USDT de teste `TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf`). Tratado como se fosse real. Consultas feitas em 16/11/2026, entre 23:51 e 23:56 UTC (20:51 a 20:56 em Brasília). Todos os horários on-chain estão em UTC, com o horário de Brasília (BRT = UTC−3) entre parênteses quando ajuda a comparar com a conversa.

## Tabela-resumo

| # | Pergunta | Resposta | Probabilidade / veredito |
|---|---|---|---|
| 1 | O "recuperador" cobra por uma recuperação que sabe ser falsa? | Sim, quase certo | **97%** (faixa 95–99%) |
| 2a | Prova: "hash do bloqueio" `1ec3c4fc…f77e` | A transação existe, mas é uma transferência comum entre carteiras do golpista, feita 10 min antes de ele dizer que bloqueou | **Falsa** como prova de bloqueio |
| 2b | Prova: imagem "PAINEL DE RECUPERAÇÃO … 1.000,00 USDT · RETIDO" | O conteúdo é desmentido pela blockchain (saldo 0, sem bloqueio). O arquivo da imagem não foi examinado | **Falsa** quanto ao conteúdo |
| 3 | Afirmações técnicas dele | 8 avaliadas: 7 falsas, 1 verdadeira e trivial (o endereço do golpista) | ver seção 3 |
| 4 | O relato da vítima bate com a blockchain? | Sim. Mecanismo: **autorização de gasto** (`increaseApproval`) assinada pela vítima, seguida de `transferFrom` por um contrato drenador. Não houve vazamento de senha | Compatível |
| 5 | Onde está o valor? | **997 USDT** em `TEcWfhn3h7X8UYR5REz4s2w9PMA1B2f21X` e **3 USDT** em `TUWTzm2dnqKuBrkkM4s3JNoecD8H1UFi2y`. **Nada bloqueado pela emissora** | Fato |
| 6a | Recuperar parte relevante (≥ 50%) em 12 meses: polícia + emissora | Depende de bloqueio rápido enquanto os 997 USDT estão parados | **7%** (3–15%) |
| 6b | Idem, ação judicial cível | Custo maior que o valor, réu não identificado | **3%** (1–8%), em boa parte sobreposta a 6a |
| 6c | Idem, pelo "recuperador" | Não tem meio técnico para isso | **< 1%** |
| 6d | Devolução dos R$ 560 do Pix pelo MED | Depende de pedir rápido e de haver saldo na conta recebedora | **25%** (10–40%) |
| 7 | Risco ainda ativo? | **Sim.** A autorização ao drenador continua valendo para **9.999.000 USDT**. Qualquer USDT que entrar na carteira da vítima pode ser levado. O "recuperador" disse o contrário | Fato |

As probabilidades são estimativas de julgamento. A seção 8 diz o que faria cada uma subir ou descer.

---

## Método e registro das consultas

Usei apenas o material da pasta, o `rastreio.py --rede nile` e chamadas diretas de leitura a `https://nile.trongrid.io`. Não assinei nem enviei nenhuma transação, não falei com ninguém e não consultei dados pessoais.

Cada afirmação de fato abaixo cita a consulta de onde saiu, por um código. As respostas brutas estão em `execucoes/`, cada pasta com o seu `MANIFEST.sha256`.

| Código | Pasta em `execucoes/` | Consulta |
|---|---|---|
| E1 | `20261116-235140-tx` | `tx 40d6399f…a1b5` (hash da perda) |
| E2 | `20261116-235143-tx` | `tx 1ec3c4fc…f77e` ("hash do bloqueio") |
| E3 | `20261116-235147-transferencias` | movimentos USDT da vítima `TXXj87…Q8np` |
| E4 | `20261116-235155-tx` | `tx 8d4bfd76…7a9a` (autorização) |
| E5 | `20261116-235157-tx` | `tx d23cbcdc…9867` (entrada dos 1.000 USDT) |
| E6 | `20261116-235159-allowance` | autorização vigente vítima → contrato drenador |
| E7 | `20261116-235200-seguir` | rastreio salto a salto desde 23:00 UTC, 6 saltos |
| E8 | `20261116-235224-estado` | saldo USDT e `isBlackListed` de 12 endereços |
| E9 | `20261116-235247-transferencias` | movimentos USDT de `TEcWfhn…f21X` |
| E10 | `20261116-235248-transferencias` | movimentos USDT de `TUWTzm…Fi2y` |
| E11 | `20261116-235249-transferencias` | movimentos USDT de `TQ5CUe…1twE` |
| E12 | `20261116-235448-allowance` | autorização vigente vítima → `TQ5CUe…1twE` |
| E13 | `20261116-235557-transferencias` | movimentos USDT de `TEhWiZ…Q2RR` |
| M01–M13 | `20261116-manual-api/` | chamadas diretas: contrato drenador (M01, M11, M12), contrato USDT Nile (M02), conta da vítima (M03), transações TRX/TRC-10 da vítima (M04), de `TQ5CUe` (M05), `TEhWiZ` (M06), `TEcWfhn` (M07), token TRC-10 recebido (M08, M09), recibo da autorização (M10), conta `TVF2Mp9…` (M13). O arquivo `comandos.txt` lista cada URL e corpo |

## Cronologia reconstruída (fatos)

| UTC (BRT) | Evento | Hash / fonte |
|---|---|---|
| 23:19:54 (20:19) | `TVF2Mp9QY7FEGTnr3DBpFLobA6jguHyMvi` envia 1.000 TRX para `TEhWiZDs4aYvvG5bRQBfqjKPyzwepmQ2RR` | `c04632be…` (M06) |
| 23:22:03 (20:22) | `TVF2Mp9…` envia 1.000 USDT para `TEhWiZ…` | `d861fee4…8752` (E13) |
| 23:24:09 (20:24) | `TEhWiZ…` envia **500 TRX para `TQ5CUe…`** (a carteira que depois recebe o valor desviado) | `b19f6cc9…` (M05, M06) |
| 23:24:15 | `TEhWiZ…` envia **150 TRX para `TEcWfhn…`** (o destino final) | `b577e853…` (M06, M07) |
| 23:24:21 | `TEhWiZ…` envia **1.000 USDT para a vítima** (a "compra" de pouco antes) | `d23cbcdc…9867` (E5) |
| 23:24:27 | `TQ5CUe…` implanta o contrato `TCdNNrHkXBaxxSaD1beacDwmjMjEzDpof4`, de nome **"DrenadorTeste"**, com as funções `charge`, `dono` e `token` | `74ef2aa2…` (M01, M05) |
| 23:24:33 | `TQ5CUe…` envia **25 TRX para a vítima** | `0669f1e5…1755` (M04, M05) |
| 23:24:39 (20:24) | **A vítima assina `increaseApproval(TCdNNrHk…, 10.000.000 USDT)`** | `8d4bfd76…7a9a` (E4) |
| 23:24:45 (20:24) | `TQ5CUe…` chama `charge(vítima, 1.000)` no drenador, e 1.000 USDT vão da vítima para `TQ5CUe…` | `40d6399f…a1b5` (E1) |
| 23:24:51–23:25:03 | `TQ5CUe…` envia 40 TRX a cada uma de três carteiras intermediárias | (M05) |
| 23:25:09–23:25:21 | `TQ5CUe…` divide o valor: 410 → `TUDB9j…`, 340 → `TG5Vrr…`, 250 → `TK7M7X…` | `e313a2ce…`, `fe3a96b2…`, `78461df6…` (E7, E11) |
| 23:25:27–23:25:39 | `TEcWfhn…` envia 30 TRX a cada uma de três carteiras de segunda camada | (M07) |
| 23:25:45–23:26:33 | Cada intermediária manda 1 USDT para `TUWTzm…` e o resto para uma carteira de segunda camada (`TQZ35N…`, `TSFLcR…`, `TAmsXH…`) | (E7, E10) |
| 23:26:39 | `TQZ35N…` → `TEcWfhn…` 409 USDT | `73ac6075…3f90` (E9) |
| **23:26:45 (20:26)** | **`TSFLcR…` → `TEcWfhn…` 339 USDT. Este é o "hash do bloqueio" que R. apresenta** | `1ec3c4fc…f77e` (E2, E9) |
| 23:26:51 | `TAmsXH…` → `TEcWfhn…` 249 USDT | `2f82638e…eff2` (E9) |
| 20:31 BRT | A vítima procura R. | conversa |
| 20:34 BRT | R.: "os 1.000 USDT continuam parados na carteira do golpista" | conversa |
| 20:36 BRT | R.: "Fiz o bloqueio agora. Hash: 1ec3c4fc…" | conversa |
| 20:42 BRT | A vítima paga R$ 560 por Pix | relato e conversa |
| 23:52:24 UTC (20:52) | Situação no momento da consulta: vítima 0 USDT, `TQ5CUe` 0, `TEcWfhn` **997**, `TUWTzm` **3**. Nenhum dos 12 endereços está bloqueado | (E8) |

Toda a perda, desde a assinatura até a consolidação, levou **2 min 12 s** (23:24:39 → 23:26:51) e terminou **4 minutos antes** de a vítima procurar R.

---

## 1. O "recuperador" cobra por uma recuperação que sabe ser falsa?

**Probabilidade: 97%** (faixa 95–99%).

**Fatos:**
- O hash que ele chama de "bloqueio" é uma transferência `transfer()` de 339 USDT assinada por `TSFLcR…`, uma carteira da própria cadeia de lavagem, às 23:26:45 UTC (20:26 BRT) (E2). Um bloqueio da emissora seria uma chamada `addBlackList` ao contrato do token, assinada pelo dono do contrato. Esse contrato tem a função (M02), mas a transação apresentada não é essa chamada.
- A transação é de 20:26, cinco minutos antes de a vítima procurar R. (20:31) e dez minutos antes de ele dizer que "fez agora" (20:36).
- Às 20:34 ele disse que o valor estava "parado" em `TQ5CUe…`. Essa carteira estava zerada desde 23:25:21 UTC (20:25 BRT) (E11), e o próprio hash que ele mostrou registra o dinheiro já na segunda camada da lavagem.
- O "painel" mostra `TQ5CUe…` com "1.000,00 USDT · RETIDO". O saldo real é 0 e a carteira não está bloqueada (E8).
- Ele disse que "cancelou a permissão". A autorização ao drenador continua em 9.999.000 USDT (E6).
- Ele cobrou R$ 560 de "taxa de liberação" e desaconselhou procurar a polícia.

**Inferência:** para escolher aquele hash, R. teve de olhar a cadeia de transações do golpista. Quem olhou a cadeia viu que o dinheiro tinha saído de `TQ5CUe`. Ainda assim afirmou o contrário, montou uma imagem com o saldo falso e cobrou. Isso exclui erro de boa-fé, por incompetência. O restante (3%) cobre hipóteses improváveis, como R. ser intermediário de outra pessoa sem saber o que repassa. Mesmo nesse caso, as provas continuariam falsas.

**Ligação com o golpista: inconclusiva.** A rapidez e a escolha de um hash de dentro da cadeia são compatíveis com ligação direta, mas qualquer pessoa com um explorador de blocos acha esse hash em poucos minutos a partir do endereço da vítima. Não há, nos dados consultados, nenhum endereço ou pagamento que ligue R. às carteiras do golpe.

## 2. As provas apresentadas

| Prova | Veredito | Motivo técnico |
|---|---|---|
| Hash `1ec3c4fc066243fc806eb504170d512b52795bf40f7964edc6be285038bdf77e` | **Falsa** como prova de bloqueio. A transação existe | Bloco 72776828, 23:26:45 UTC. É um `transfer(TEcWfhn…, 339 USDT)` assinado por `TSFLcR7iE9Bvw35JBhX4E9aQFAZmccRnix`, com resultado SUCCESS (E2). Não é `addBlackList` nem nenhuma outra ação da emissora. É anterior ao contato com a vítima. Movimenta 339 USDT, não 1.000. Envolve `TSFLcR` e `TEcWfhn`, não a carteira que ele diz ter bloqueado (`TQ5CUe`) |
| Imagem "PAINEL DE RECUPERAÇÃO", "Carteira TQ5CUe… · 1.000,00 USDT · STATUS: RETIDO", selo "bloqueio ativo" | **Falsa** quanto ao conteúdo. O arquivo não foi examinado, só a descrição | `balanceOf(TQ5CUe…)` = 0 e `isBlackListed(TQ5CUe…)` = não (E8). A carteira esvaziou às 23:25:21 UTC (E11). Não existe um "painel" público de bloqueio da Tether. Uma tela assim é só uma imagem feita por quem a envia |

## 3. As afirmações técnicas dele

| Hora | Afirmação | Veredito | Por quê (fonte) |
|---|---|---|---|
| 20:33 | "Sua carteira foi hackeada, sua senha vazou" | **Falsa** | A vítima assinou ela mesma uma autorização (E4). A saída dos fundos foi assinada por `TQ5CUe…` por meio do drenador, e não pela chave da vítima (E1). As permissões da conta continuam com uma única chave, a da vítima (M03). Quem tivesse a chave teria transferido direto, sem precisar de contrato nem de autorização, e teria levado também os 25 TRX que continuam lá (M03) |
| 20:33 | "100% de êxito" | **Sem fundamento** | Não há como conferir. Contradiz o que se observa: valores em USDT só voltam quando a emissora bloqueia, por pedido de autoridade, e ainda há saldo a bloquear |
| 20:34 | "Já localizei [a carteira do golpista]" | **Verdadeira, mas trivial** | `TQ5CUe…` é de fato quem recebeu os 1.000 USDT (E1). Isso aparece no histórico público da própria vítima (E3) |
| 20:34 | "Os 1.000 USDT continuam parados na carteira do golpista, ele ainda não conseguiu mexer" | **Falsa** | Às 20:34 BRT, `TQ5CUe…` estava zerada havia 9 minutos: três saídas de 410, 340 e 250 entre 23:25:09 e 23:25:21 UTC (E11). Saldo 0 (E8) |
| 20:36 | "Fiz o bloqueio agora" (com o hash) | **Falsa** | Ver seção 2. Nenhum dos 12 endereços está na lista de bloqueio (E8) |
| 20:38 | "Cancelei a permissão que o golpista tinha. Pode voltar a usar sua carteira normalmente" | **Falsa, e perigosa** | `allowance(vítima, TCdNNrHk…)` = 9.999.000 USDT (E6). Tecnicamente, só o dono dos fundos (a vítima) pode reduzir ou zerar uma autorização TRC-20, assinando `approve`/`decreaseApproval`. Terceiros não podem. Usar a carteira "normalmente" e receber USDT nela significa perder o valor de novo |
| 20:40 | "Está tudo congelado pela Tether. Para liberar, a plataforma cobra 10%" | **Falsa** | Nada está bloqueado (E8). A emissora não cobra "taxa de liberação" de vítimas. Bloqueio e eventual devolução seguem pedido de autoridade, não pagamento por Pix a um particular |
| 20:41 | "Não precisa de polícia… só atrasa e a Tether devolve pro golpista" | **Falsa** | Não existe mecanismo pelo qual registrar ocorrência devolva fundos ao golpista. Os bloqueios da emissora costumam vir justamente de pedidos de autoridades. Desaconselhar a polícia é um sinal típico de golpe de recuperação |

## 4. O relato da vítima bate com a blockchain? Qual foi o mecanismo?

**Sim, é compatível.**

**Fatos:**
1. A vítima recebeu 1.000 USDT às 23:24:21 UTC (20:24 BRT) (E5).
2. Às 23:24:39 (20:24 BRT), a carteira da vítima assinou `increaseApproval(TCdNNrHkXBaxxSaD1beacDwmjMjEzDpof4, 10.000.000 USDT)` no contrato USDT (E4). O evento `Approval` foi emitido (E4).
3. Seis segundos depois, `TQ5CUe…` chamou `charge(vítima, 1.000 USDT)` no contrato `TCdNNrHk…` (E1). O contrato se chama "DrenadorTeste", foi implantado por `TQ5CUe…` 12 segundos antes da autorização (M01, M05), tem `dono()` = `TQ5CUe…` (M11) e `token()` = contrato USDT (M12). O resultado foi um `Transfer` de 1.000 USDT da vítima para `TQ5CUe…` (E1).
4. As permissões da conta da vítima não mudaram: dono e ativo com a chave dela, limiar 1 (M03).

**Mecanismo (inferência sustentada pelos fatos acima):** golpe de **drenador por autorização** ("approval phishing"). O "conectar a carteira" e o "confirmar o recebimento do bônus" foram, na prática, o pedido para assinar uma autorização de gasto quase ilimitada a favor do contrato do golpista. O reconhecimento facial não "confirma bônus": só libera a assinatura na carteira do celular. Com a autorização dada, o golpista retirou o saldo sem precisar da senha nem das palavras de recuperação. Isso confirma o que a vítima diz, que não digitou nenhuma das duas.

**Detalhes do relato que a blockchain esclarece:**
- **O TRX que "ainda tem":** são exatamente **25 TRX**, e foram enviados **pelo próprio golpista** (`TQ5CUe…`) às 23:24:33, seis segundos antes da autorização (M04, M05). Na prática, o golpista "pagou" a taxa para a vítima conseguir assinar. A autorização consumiu 23.728 de energia sem cobrar TRX da vítima (M10).
- **Horário:** a vítima diz ter aberto o link "por volta das 20h20". O USDT chegou às 20:24:21 e a autorização foi assinada 18 segundos depois. Isso é compatível se ela já estava no site quando o saldo caiu.
- **A origem dos 1.000 USDT merece atenção (fato):** o endereço que mandou o USDT à vítima, `TEhWiZ…`, recebeu esses fundos 2 minutos antes (E13). Nos 12 segundos anteriores ao envio à vítima, ele também mandou **500 TRX para `TQ5CUe…`**, a carteira do golpista, e **150 TRX para `TEcWfhn…`**, o destino final (M06). Não tem perfil de corretora: tem só 5 transações, todas nessa janela (M06).
  **Inferência:** quem "vendeu" o USDT à vítima e quem bancou as carteiras do golpe partem do mesmo endereço. Num caso real, isso indicaria que a compra foi feita com alguém ligado ao grupo (por exemplo, um vendedor P2P que também opera o golpe). Neste caso encenado, também pode ser só o efeito de a montagem ter sido financiada de uma única carteira (`TVF2Mp9…`, com cerca de 19,85 milhões de TRX, provável distribuidora de fundos de teste; M13). Não dá para separar as duas hipóteses com os dados disponíveis. Em todo caso, vale perguntar à vítima **como e de quem comprou** (seção 8).
- **Ruído sem relevância:** às 23:24:39 a vítima recebeu 1 unidade do token TRC-10 `1007445` ("tenergy.dev"), de `TENERGYRup4Kh…` (M04, M08). O token se descreve como serviço de aluguel de energia (M09), e esse endereço manda a mesma quantia a dezenas de contas desde 20/10/2026. É divulgação em massa, não faz parte do golpe. Recomendação: não interagir com ele. [Nota editorial: a afirmação sobre o alcance desse envio não tem consulta guardada no repositório.]

## 5. Onde está o valor, por qual caminho chegou lá, e há algo bloqueado?

**Situação em 23:52:24 UTC (E8):**

| Endereço | Papel | Saldo USDT | Bloqueado pela emissora? |
|---|---|---:|---|
| `TEcWfhn3h7X8UYR5REz4s2w9PMA1B2f21X` | Consolidação (destino final) | **997,000000** | não |
| `TUWTzm2dnqKuBrkkM4s3JNoecD8H1UFi2y` | Recebeu 1 USDT de cada ramo | **3,000000** | não |
| `TXXj87…Q8np` (vítima), `TQ5CUe…`, `TUDB9j…`, `TG5Vrr…`, `TK7M7X…`, `TQZ35N…`, `TSFLcR…`, `TAmsXH…`, `TCdNNrHk…` (drenador), `TEhWiZ…` | — | 0 | não |

**Caminho (E1, E7, E9, E10, E11):**

```
vítima TXXj87… ──1.000 (charge/transferFrom via drenador TCdNNrHk…)──▶ TQ5CUe…
TQ5CUe… ─410─▶ TUDB9j… ─1─▶ TUWTzm…   ─409 (5+404)─▶ TQZ35N… ─409─▶ TEcWfhn…
        ─340─▶ TG5Vrr… ─1─▶ TUWTzm…   ─339 (5+334)─▶ TSFLcR… ─339─▶ TEcWfhn…  ← "hash do bloqueio"
        ─250─▶ TK7M7X… ─1─▶ TUWTzm…   ─249 (5+244)─▶ TAmsXH… ─249─▶ TEcWfhn…
                                                         total em TEcWfhn… = 997
```

O `seguir` encerra em `TEcWfhn…` e `TUWTzm…` sem nenhuma saída (E7). Isso foi confirmado pelo histórico de cada um, só com entradas (E9, E10).

**Inferências:**
- `TEcWfhn…` não é carteira de corretora. Tem só 3 entradas de USDT (E9) e foi ela que mandou TRX às três carteiras de segunda camada antes de elas lhe devolverem o USDT (M07). Ou seja, quem controla `TEcWfhn` também controla essa camada. O desenho todo (dividir, passar por uma segunda camada, reunir de novo) é de **lavagem em circuito fechado**, e o valor ainda está com o golpista, sem ter passado por nenhum serviço que identifique clientes.
- Os 3 × 1 USDT para `TUWTzm…` combinam com uma **comissão** (por exemplo, o operador de um serviço de drenagem cobrando por uso). É hipótese, não fato.

**Bloqueio pela emissora: não há nenhum.** `isBlackListed` = não para todos os 12 endereços (E8). O contrato USDT da Nile (nome "TetherToken", implantado por `TKGRE6oiU3rEzasue4MsB6sCXXSTx9BAe3`) tem `addBlackList` e `destroyBlackFunds` (M02), então o bloqueio seria tecnicamente possível, mas não foi feito.

## 6. Probabilidade de recuperar parte relevante (≥ 50%) em 12 meses

| Caminho | Probabilidade | Justificativa |
|---|---|---|
| **Polícia + emissora** | **7%** (3–15%) | A favor: os 997 USDT estão parados numa carteira só, e a emissora pode bloquear (M02, E8). Contra: o bloqueio depende de pedido de autoridade chegar à emissora **antes** de o golpista mover o saldo, o que costuma levar horas ou dias. Uma perda de cerca de R$ 5,6 mil raramente tem prioridade. Mesmo com o bloqueio, a devolução ainda exige um processo (ordem judicial e queima e reemissão dos tokens), demorado. A chance de **bloqueio** é maior (talvez 10–15%) do que a de **devolução** em 12 meses |
| **Ação judicial cível** | **3%** (1–8%) | Não há réu identificado. O custo passa do valor. Só ganha sentido se o dinheiro chegar a uma corretora que identifique clientes, ou se o vendedor `TEhWiZ…` for identificável (seção 4). Em boa parte depende dos mesmos fatos do caminho anterior, então os dois **não se somam** |
| **"Recuperador"** | **< 1%** | Ele não tem meio técnico. As provas dele são falsas (seções 2 e 3). O mais provável é cobrar novas "taxas" |
| **Combinado** (algum caminho dá certo) | **cerca de 8–10%** | |
| **MED, devolução do Pix de R$ 560** | **25%** (10–40%) | A favor: pedido no mesmo dia (o Pix foi às 20:42), e o MED cobre Pix feito por causa de golpe. Contra: contas recebedoras de golpe costumam ser repassadas ou sacadas em minutos. A devolução depende de haver saldo quando o banco bloquear. O banco recebedor pode recusar se avaliar que não houve fraude. Cada hora de atraso reduz a chance |

## 7. Providências, em ordem

**Hoje, em minutos:**
1. **Não pagar mais nada a R.** e não responder a novas cobranças ("taxa de gás", "imposto", "taxa de saque"). Não instalar aplicativos nem permitir acesso remoto.
2. **Contestar o Pix no aplicativo do banco** (botão de contestação ou devolução por golpe, ou a central de atendimento), informando que foi golpe. É o passo mais urgente porque o saldo da conta recebedora some rápido. Guardar o protocolo.
3. **Revogar a autorização** ao drenador `TCdNNrHkXBaxxSaD1beacDwmjMjEzDpof4`. A vítima precisa assinar uma transação que zere a autorização (`approve(TCdNNrHk…, 0)`), pelo gerenciador de autorizações da própria carteira ou de um explorador de blocos acessado **digitando o endereço**, nunca por link recebido. A carteira tem 25 TRX (M03), o que deve bastar para a taxa. Até isso ser feito, **não receber USDT nesse endereço**. Como precaução, criar uma carteira nova (novas palavras de recuperação) e usar só ela daqui em diante. Não há indício de que as palavras vazaram (seção 4), mas o endereço antigo já está marcado.

**Hoje ou amanhã:**
4. **Guardar as evidências:** capturas da conversa com R. (com perfil, nome de usuário e link), o comprovante do Pix (nome e CPF/CNPJ mascarado do recebedor, banco, chave Pix, identificador E2E), o link do site do "bônus" e onde ele foi divulgado, e os hashes e endereços deste parecer. Não confrontar R.
5. **Registrar boletim de ocorrência** (delegacia de crimes cibernéticos, ou BO online) por **dois fatos**: (a) o desvio dos USDT, com os hashes `8d4bfd76…`, `40d6399f…`, o endereço `TEcWfhn…` com 997 USDT e o pedido para a autoridade solicitar **bloqueio à emissora**; (b) o estelionato de R. A chave Pix dele é a melhor pista de identificação, porque o banco tem os dados cadastrais do titular. Anexar o protocolo do MED.
6. **Avisar a emissora** pelo canal público dela, com o número do BO. O bloqueio efetivo costuma depender do pedido da autoridade, mas o aviso deixa registro.
7. **Denunciar** o perfil de R. e o link do site na rede social.

**Depois:**
8. Acompanhar `TEcWfhn…`. Se o saldo for para uma corretora, passar o hash à autoridade, que pode pedir bloqueio e dados cadastrais à corretora.
9. Desconfiar de qualquer novo "recuperador", "advogado" ou "policial" que apareça por conta própria. É comum a segunda abordagem vir do mesmo grupo.

**Riscos que continuam ativos (fatos e inferências):**
- **Autorização ilimitada ainda vigente:** 9.999.000 USDT a favor do drenador (E6), com `dono()` = `TQ5CUe…` (M11). Qualquer USDT que entrar em `TXXj87…` pode ser levado na hora com `charge`. É fato. R. orientou o contrário ("pode voltar a usar normalmente"), o que agrava o risco. A autorização direta para `TQ5CUe…` é zero (E12): o risco está só no contrato.
- **Nova extorsão por R.:** ele já recebeu uma vez e sabe que a vítima paga. Pelo Pix, também pode ter obtido o nome dela e o banco que ela usa.
- **O site do "bônus"** provavelmente continua no ar, fazendo outras vítimas.

## 8. Que evidência mudaria cada número

| Número | Subiria se… | Desceria se… |
|---|---|---|
| **1. R. sabe que é falso (97%)** | (praticamente no teto) R. pedir nova taxa; aparecer pagamento ou endereço que ligue R. a `TQ5CUe`, `TEcWfhn` ou `TEhWiZ`; o mesmo perfil aparecer em outras denúncias | Em 24 h, os USDT voltarem de fato à vítima, ou `isBlackListed(TEcWfhn)` passar a "SIM" por pedido documentado ligado a ele, o que é muito improvável. Ficar demonstrado que ele recebeu as "provas" de terceiro e as repassou sem saber |
| **6a. Polícia + emissora (7%)** | BO e pedido da autoridade à emissora em poucos dias, com `TEcWfhn` ainda com os 997; `isBlackListed(TEcWfhn)` = SIM; o saldo ir para uma corretora que identifique clientes e coopere; o vendedor `TEhWiZ` ser uma pessoa identificável (P2P com cadastro, ou Pix pago a ele), o que também abriria uma pista penal | O saldo de `TEcWfhn` sair para serviços de mistura, pontes entre redes ou troca por TRX, ou ficar espalhado por muitos endereços; nenhum BO; demora de semanas |
| **6b. Judicial (3%)** | Identificação de um titular solvente (vendedor P2P, titular da conta Pix de R., corretora de destino) | Ninguém identificado; valor parado abaixo do custo de ação |
| **6c. "Recuperador" (< 1%)** | Nada plausível | — |
| **6d. MED (25%)** | Contestação aberta ainda hoje; o banco recebedor confirmar bloqueio de saldo; a conta de R. ser de pessoa física com movimento normal, e não uma conta "laranja" | Contestação só depois de dias; o banco informar saldo zero ou repasse; R. alegar "serviço prestado" e o banco aceitar |
| **4. Mecanismo** (alta confiança) | — | Aparecer, para esse endereço, alguma transação assinada pela chave da vítima que ela não reconheça, além da autorização. Isso indicaria comprometimento da chave e mudaria a recomendação 3 de "precaução" para "obrigatória" |

---

## Limites deste parecer

- **Rede de teste.** As transações são reais na Nile, mas sem valor. A "emissora" aqui é o dono do contrato de teste `TXYZop…` (`TKGRE6…`), não a Tether. As probabilidades de bloqueio e recuperação descrevem o comportamento esperado na rede principal, por analogia.
- **Momento da consulta.** Os saldos e o estado de bloqueio valem para 23:52–23:56 UTC de 16/11/2026 (E8, E6). O golpista pode mover os 997 USDT a qualquer momento. Antes de usar esses números, é preciso rodar `estado` e `allowance` de novo.
- **Fonte única de dados.** Todas as leituras vieram da TronGrid (Nile), pelo `rastreio.py` e por chamadas diretas. Não conferi com um segundo nó ou explorador independente. As listas de transações por conta (`/v1/accounts/...`) dependem do índice da TronGrid. As chamadas ao contrato (`balanceOf`, `allowance`, `isBlackListed`) leem o estado diretamente.
- **Profundidade do rastreio.** Segui 6 saltos a partir da vítima (E7), além das origens de `TEhWiZ` e `TVF2Mp9`. Não investiguei o resto da atividade de `TVF2Mp9…`, que é uma conta antiga e muito movimentada (M13), nem outras transações TRC-10/TRX de todas as carteiras intermediárias.
- **Material não examinado.** Não vi a imagem do "painel" nem o comprovante do Pix, só as descrições. Não posso dizer nada sobre o arquivo da imagem (edição, metadados), só sobre o conteúdo descrito. Também não vi o site do "bônus", então o mecanismo do lado do site é inferido a partir das transações.
- **Relato de segunda mão.** O relato da vítima foi transcrito por terceiro e os horários foram informados por ela. A conversa é fictícia e não tem como ser autenticada.
- **Identidades.** Nada aqui identifica pessoas. Ligar endereços a pessoas depende de dados cadastrais (bancos, corretoras), que só a autoridade pode obter.
- **Probabilidades.** São estimativas de julgamento, baseadas no padrão desse tipo de golpe e nos fatos acima, e não cálculos sobre uma base estatística. As faixas indicam a incerteza.
- **MED.** Não verifiquei o regulamento vigente do Banco Central nem as regras do banco da vítima. Prazos e alcance (por exemplo, o rastreio além da primeira conta recebedora) devem ser confirmados com o banco.
- **Escopo.** Não fiz contato com nenhuma pessoa ou serviço, não assinei transações e não consultei bases vazadas ou dados pessoais, como determina o briefing.
