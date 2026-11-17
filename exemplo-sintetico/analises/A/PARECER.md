# Parecer técnico: análise A (fraude com USDT, rede de teste TRON Nile)

Data das consultas: 16/11/2026, entre 23:51 e 23:56 UTC (20:51 a 20:56 em Brasília).
Rede: TRON Nile (teste). Contrato USDT de teste: `TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf`.
Horários abaixo em UTC, com o horário de Brasília (BRT = UTC−3) entre parênteses quando ajuda.

## Tabela-resumo

| # | Pergunta | Estimativa | Faixa | Base principal |
|---|---|---|---|---|
| 1 | "Recuperador" cobra por recuperação que sabe ser falsa | **97%** | 93–99% | 6 afirmações verificavelmente falsas em 10 minutos; "hash do bloqueio" é uma transferência comum feita antes de a vítima falar com ele |
| 2 | Provas apresentadas (hash e imagem) | **ambas falsas** como prova de bloqueio | – | Hash real, mas é uma transferência entre carteiras do golpista; imagem contradiz o saldo e a lista de bloqueio |
| 4 | Relato compatível com a blockchain | **sim**, no mecanismo | – | Autorização (`increaseApproval`) assinada pela vítima, seguida 6 s depois de `transferFrom` por contrato drenador |
| 5 | Algo bloqueado pela emissora | **não** (nada bloqueado) | – | `isBlackListed` = não para os 12 endereços; nenhum evento `AddedBlackList` desde 23:00 UTC |
| 6a | Recuperar parte relevante (≥ 30%) em 12 meses via polícia + emissora | **6%** | 2–15% | 997 USDT parados num só endereço, ainda não congelados; valor baixo para mobilizar a polícia a tempo |
| 6b | Idem via ação judicial (cível, isolada) | **2%** | 1–5% | Réu desconhecido, custo maior que o valor, depende da mesma identificação |
| 6c | Idem via "recuperador" | **< 1%** | 0–1% | Não há recuperação em curso; o risco é perder mais |
| 6d | Devolução do Pix de R$ 560 pelo MED | **25%** | 10–40% | Depende de haver saldo na conta recebedora quando o banco bloquear; contestação feita em horas melhora a chance |
| 7 | Risco ainda ativo | **sim, alto** | – | Autorização de 9.999.000 USDT ao drenador continua vigente; "recuperador" mandou voltar a usar a carteira |

"Parte relevante" aqui = pelo menos 300 dos 1.000 USDT. As faixas são juízo do analista, não frequências medidas.

---

## 1. Consultas feitas (fonte de cada fato)

Todas as respostas brutas estão em `execucoes/`, cada pasta com `MANIFEST.sha256`. As pastas `execucoes/AAAAMMDD-HHMMSS-*` são do `rastreio.py`. As pastas `execucoes/manual-*` são consultas diretas a `https://nile.trongrid.io` feitas com `execucoes/consulta_extra.py` (só leitura; cada JSON guarda URL, corpo e resposta).

| Ref. | Consulta | Pasta |
|---|---|---|
| C1 | `tx 40d6399f…` (perda) | `20261116-235134-tx` |
| C2 | `tx 1ec3c4fc…` ("hash do bloqueio") | `20261116-235137-tx` |
| C3 | `transferencias` da vítima | `20261116-235140-transferencias` |
| C4 | `tx 8d4bfd76…` (autorização) | `20261116-235151-tx` |
| C5 | `tx d23cbcdc…` (entrada dos 1.000 USDT na vítima) | `20261116-235153-tx` |
| C6 | `allowance` vítima → drenador / vítima → TQ5CUe | `20261116-235155-allowance`, `…235156-allowance` |
| C7 | `seguir` a partir da vítima, 6 saltos | `20261116-235157-seguir` |
| C8 | `estado` de 12 endereços (saldo e bloqueio) | `20261116-235222-estado` |
| C9 | `transferencias` de TEcWfhn, TUWTzm, TQ5CUe, TEhWiZ, TSFLcR7, drenador | `20261116-235253` a `…235258-transferencias` |
| C10 | `getaccount` vítima, TQ5CUe, TEcWfhn; `getcontract` e `getcontractinfo` do drenador | `manual-contas` |
| C11 | `dono()` e `token()` do drenador; histórico completo (TRX e contratos) de vítima, TQ5CUe, TEcWfhn; eventos `AddedBlackList` do USDT desde 23:00 UTC | `manual-historico` |
| C12 | ABI do contrato USDT; histórico de TEhWiZ e TUWTzm; últimas saídas de TVF2Mp | `manual-origem` |
| C13 | Checagem final: `estado`, `allowance`, saídas de TEcWfhn após 23:26:52 | `20261116-235541-estado`, `…235549-allowance`, `…235550-transferencias` |

### Linha do tempo on-chain (fatos)

| UTC (BRT) | Evento | Hash | Ref. |
|---|---|---|---|
| 23:19:54 (20:19) | `TEhWiZ…` recebe 1.000 TRX | `c04632be971be811…` | C12 |
| 23:22:03 (20:22) | `TVF2Mp…` envia 1.000 USDT a `TEhWiZ…` | `d861fee43afd6a0f…` | C9 |
| 23:24:09 (20:24) | `TEhWiZ…` envia **500 TRX a `TQ5CUe…`** (futuro golpista) | `b19f6cc90119ca2b…` | C11, C12 |
| 23:24:15 | `TEhWiZ…` envia **150 TRX a `TEcWfhn…`** (futuro destino final) | `b577e853606766b9…` | C11, C12 |
| 23:24:21 | `TEhWiZ…` envia **1.000 USDT à vítima** | `d23cbcdc…` | C5 |
| 23:24:27 | `TQ5CUe…` cria o contrato `TCdNNrHkXBaxxSaD1beacDwmjMjEzDpof4`, nome "DrenadorTeste" | `74ef2aa2991d6132…` | C10, C11 |
| 23:24:33 | `TQ5CUe…` envia **25 TRX à vítima** (primeiro TRX que o endereço recebeu; conta criada nesse momento) | `0669f1e5044599de…` | C10, C11 |
| 23:24:39 (20:24) | **Vítima assina `increaseApproval(TCdNNr…, 10.000.000 USDT)`** | `8d4bfd76…` | C4 |
| 23:24:45 (20:24) | `TQ5CUe…` chama `charge(vítima, 1.000)` no drenador → evento `Transfer` vítima → `TQ5CUe…` 1.000 USDT | `40d6399f…` | C1 |
| 23:24:51–23:25:03 | `TQ5CUe…` envia 40 TRX a cada uma de `TUDB9…`, `TG5Vr…`, `TK7M7…` | `d7a567ef…`, `5a6a1193…`, `a73987fc…` | C11 |
| 23:25:09–23:25:21 (20:25) | `TQ5CUe…` divide: 410 → `TUDB9…`, 340 → `TG5Vr…`, 250 → `TK7M7…` | `e313a2ce…`, `fe3a96b2…`, `78461df6…` | C7, C9 |
| 23:25:27–23:25:39 | **`TEcWfhn…` envia 30 TRX a cada uma de `TQZ35…`, `TSFLc…`, `TAmsX…`** | `66198476…`, `12b220ca…`, `2e4d7751…` | C11 |
| 23:25:45–23:26:33 | Cada carteira da 1ª camada manda 1 USDT a `TUWTzm…` e o resto (5 + saldo) à 2ª camada | ver C7 | C7 |
| 23:26:39–23:26:51 (20:26) | Consolidação em `TEcWfhn…`: 409 + **339 (`1ec3c4fc…`)** + 249 = 997 USDT | `73ac6075…`, `1ec3c4fc…`, `2f82638e…` | C7, C9 |
| 23:31 (20:31) | Vítima procura R. (relato) | – | relato |
| 23:55:50 (20:55) | `TEcWfhn…` sem nenhuma saída de USDT desde a consolidação | – | C13 |

---

## Pergunta 1. Probabilidade de o "recuperador" cobrar por recuperação que sabe ser falsa

**Estimativa: 97% (faixa 93–99%).**

Fatos:
- Em 10 minutos (20:33–20:43 BRT) R. fez seis afirmações técnicas que a blockchain desmente (ver pergunta 3), entre elas a de que os fundos "continuam parados" em `TQ5CUe…`, que tinha saldo zero desde 23:25:21 UTC (C9, C8).
- O "hash do bloqueio" (`1ec3c4fc…`) é uma transferência de 339 USDT entre duas carteiras do golpista, registrada às 23:26:45 UTC (20:26 BRT), **quatro minutos antes de a vítima falar com R.** e dez minutos antes de ele dizer "fiz o bloqueio agora" (C2).
- Cobrou adiantado (R$ 560 por Pix), disse que era "o único custo" e desaconselhou polícia e advogado (conversa).

Inferência:
- Quem consegue escolher um hash que está exatamente no caminho do dinheiro sabe ler a blockchain e, portanto, sabe que esse hash não é bloqueio e que `TQ5CUe…` está vazio. A hipótese de "recuperador honesto mas incompetente" não explica essa combinação. Também não há explicação inocente para "fiz o bloqueio": um particular não consegue bloquear USDT. Só a emissora consegue, com `addBlackList` (C12, ABI).
- Os 3% restantes cobrem a possibilidade remota de R. ser um intermediário que acredita repassar a um terceiro. Mesmo nesse caso a cobrança continuaria indevida.
- **Hipótese aberta, sem probabilidade atribuída:** R. pode estar ligado ao próprio golpista. A favor: escolheu um hash de dentro da rota e mandou a vítima "voltar a usar a carteira", o que manteria a autorização do drenador útil (pergunta 7). Contra: a rota é pública, e qualquer pessoa que leia a blockchain encontra esse hash em minutos. Isso não está demonstrado.

## Pergunta 2. Provas apresentadas por R.

| Prova | Veredito | Motivo técnico |
|---|---|---|
| Hash `1ec3c4fc066243fc806eb504170d512b52795bf40f7964edc6be285038bdf77e` ("hash do bloqueio") | **Falsa como prova de bloqueio** (o hash existe, mas é outra coisa) | C2: tipo `TriggerSmartContract`, chamada `transfer(TEcWfhn…, 339 USDT)`, **assinada por `TSFLcR7…`**, bloco 72776828, 23:26:45 UTC. Um bloqueio seria uma chamada `addBlackList` assinada pela conta dona do contrato USDT e emitiria o evento `AddedBlackList`. Esse evento não aparece desde 23:00 UTC (C11), e `isBlackListed` dá "não" para todos os endereços (C8, C13). O horário é anterior ao primeiro contato da vítima com R. É um salto da lavagem (2ª camada → destino final) apresentado como bloqueio. |
| Imagem "PAINEL DE RECUPERAÇÃO": `TQ5CUe… · 1.000,00 USDT · STATUS: RETIDO`, selo "bloqueio ativo" | **Falsa** quanto ao conteúdo | Às 20:37 BRT (23:37 UTC), `TQ5CUe…` tinha 0 USDT: os 1.000 saíram entre 23:25:09 e 23:25:21 UTC (C9). O endereço não está na lista de bloqueio (C8). Não existe "painel" da Tether que mostre a carteira de um terceiro como "retida". Não vi a imagem, só a descrição. Por isso não digo nada sobre edição de pixels, e sim que o que ela afirma é falso. |

## Pergunta 3. Afirmações técnicas de R.

| Afirmação (horário BRT) | Veredito | Por quê (evidência) |
|---|---|---|
| "Sua carteira foi hackeada, sua senha vazou" (20:33) | **Falsa** | A única transação de contrato assinada pela vítima é a autorização `8d4bfd76…` (C4, C11: histórico completo da vítima tem 3 transações, e só essa foi assinada por ela). Os 1.000 USDT saíram por `transferFrom`, numa transação **assinada por `TQ5CUe…`**, e não pela vítima (C1). A permissão de dono da conta continua com uma chave só, a da própria vítima (C10). Os 25 TRX continuam lá (C10). Se a chave tivesse vazado, o golpista teria transferido direto, sem precisar de contrato nem de autorização, e provavelmente levaria o TRX também. |
| "Tenho 100% de êxito" (20:33) | **Não verificável, implausível** | Não há como conferir. Nenhum serviço legítimo de rastreio promete êxito, porque a recuperação depende de bloqueio pela emissora e de ordem judicial. |
| "Os 1.000 USDT continuam parados na carteira do golpista, ele ainda não conseguiu mexer" (20:34) | **Falsa** | `TQ5CUe…` repassou tudo entre 23:25:09 e 23:25:21 UTC (20:25 BRT), 9 minutos antes da frase (C9). Saldo 0 (C8). |
| "Fiz o bloqueio agora", com hash (20:36) | **Falsa** | Ver pergunta 2. Particular não bloqueia USDT, e o hash é uma transferência de 20:26. |
| "Cancelei a permissão que o golpista tinha. Pode voltar a usar sua carteira normalmente" (20:38) | **Falsa e perigosa** | `allowance(vítima, TCdNNr…)` = **9.999.000 USDT**, às 23:51:55 e de novo às 23:55:49 UTC (C6, C13). Só a própria vítima pode revogar uma autorização TRC-20, assinando `approve(gastador, 0)` com a chave dela. Um terceiro não tem como fazer isso. Não há nenhuma transação de revogação no histórico da vítima (C11). |
| "Está tudo congelado pela Tether" (20:40) | **Falsa** | `isBlackListed` = não para os 12 endereços da rota (C8). Nenhum `AddedBlackList` desde 23:00 UTC (C11). O contrato de teste tem essas funções, então a consulta é válida (C12: ABI com `addBlackList`, `isBlackListed`, `AddedBlackList`). |
| "Para liberar, a plataforma cobra 10%" (20:40) | **Falsa** (no mecanismo) | O contrato USDT não tem nenhuma função de "liberação mediante taxa" (C12, ABI). Fundos congelados pela emissora só são reemitidos por processo da própria emissora, a pedido de autoridade. Nenhum pagamento por Pix a um particular entra nesse processo. |
| "Não precisa de polícia nem advogado, só atrasa e a Tether devolve pro golpista" (20:41) | **Falsa** | O congelamento pela emissora não "volta ao golpista" por causa da polícia. Em regra, o pedido de autoridade é justamente o que leva ao congelamento (conhecimento geral sobre a política da emissora, não verificado neste material). Desestimular a ida à polícia é padrão típico de golpe. |
| "Em até 24 horas cai na sua carteira" (20:43) | **Não verificável ainda; tecnicamente sem base** | O prazo não venceu (consulta às 20:55 BRT). Não há bloqueio nem processo em andamento que justifique a promessa. Pior: **se qualquer USDT cair na carteira da vítima, o drenador pode levá-lo na hora** (pergunta 7). |
| "Já localizei" (20:34) | **Verdadeira só em parte** | `TQ5CUe…` é de fato o primeiro destino, mas isso está no próprio hash da perda, que é público (C1). Localizar não significa recuperar. |

## Pergunta 4. Compatibilidade do relato e mecanismo

**Compatível no mecanismo. Há um ponto da origem do saldo que precisa ser esclarecido.**

Mecanismo (fatos, C1, C4, C10, C11):
1. `TQ5CUe…` criou o contrato drenador `TCdNNr…` ("DrenadorTeste") às 23:24:27 UTC. A função `charge(usuario, valor)` só pode ser chamada pelo `dono` (= `TQ5CUe…`, conferido com `dono()`) e executa `transferFrom(usuario, dono, valor)` no USDT (`token()` = `TXYZop…`; o bytecode tem o seletor `23b872dd` e a mensagem "so o dono").
2. Às 23:24:39 (20:24 BRT) a vítima assinou `increaseApproval(TCdNNr…, 10.000.000 USDT)`. Corresponde ao "confirmar o recebimento do bônus" com reconhecimento facial: o rosto só desbloqueou a carteira para assinar. A transação foi paga com energia do próprio contrato (`origin_energy_usage` 23.728), e por isso o saldo de TRX ficou intacto.
3. Seis segundos depois, `TQ5CUe…` chamou `charge(vítima, 1.000)`, e os 1.000 USDT foram para `TQ5CUe…`.

Isso é golpe de **autorização de gasto** (*approval phishing*), e não roubo de senha ou de frase de recuperação. Bate com "não digitou senha nem as palavras de recuperação". O horário relatado ("por volta das 20h20") é compatível com 20:24 BRT.

Ponto a esclarecer (fato + inferência):
- Fato: o endereço da vítima recebeu os 1.000 USDT às 23:24:21 UTC, **18 segundos antes** da autorização, vindos de `TEhWiZ…` (C5). Esse mesmo `TEhWiZ…` mandou 500 TRX a `TQ5CUe…` e 150 TRX a `TEcWfhn…` doze e seis segundos antes (C12). O endereço da vítima só passou a existir on-chain às 23:24:30, ativado pelos 25 TRX que **o próprio golpista** mandou (C10, C11). Ou seja, o "algum TRX" que a vítima diz ainda ter veio de `TQ5CUe…`.
- Inferência: num caso real, ter o mesmo financiador para o saldo da vítima, para o gás do golpista e para a carteira final seria um dado forte. As leituras possíveis são: (a) a vítima comprou o USDT de um vendedor P2P ligado ao grupo; (b) "comprou" por indicação do próprio site ou perfil; (c) há imprecisão no relato. Num cenário encenado, (d) a explicação mais provável é que uma só carteira de montagem abasteceu todos os papéis. `TVF2Mp…`, que abasteceu `TEhWiZ…`, distribui 1.000 USDT a dezenas de endereços (C12), o que é típico de torneira (*faucet*) de rede de teste. Também é estranho, num caso real, o golpista dar 25 TRX à vítima. Há drenadores que fazem isso para ela ter com que pagar a taxa, mas aqui nem foi preciso. **Perguntar à vítima onde, de quem e a que horas comprou o USDT.**

## Pergunta 5. Onde está o valor, por qual caminho, e o que está bloqueado

Fatos (C7, C8, C9, C13):

```
vítima TXXj87…  ─(charge/transferFrom, 40d6399f…, 23:24:45)→  TQ5CUe… 1.000
  TQ5CUe… ─410→ TUDB9jNJ… ─1→ TUWTzm…   ─409 (5+404)→ TQZ35NhW… ─409 (73ac6075…)→ TEcWfhn…
          ─340→ TG5VrrxS… ─1→ TUWTzm…   ─339 (5+334)→ TSFLcR7i… ─339 (1ec3c4fc…)→ TEcWfhn…
          ─250→ TK7M7Xei… ─1→ TUWTzm…   ─249 (5+244)→ TAmsXHxv… ─249 (2f82638e…)→ TEcWfhn…
```

| Endereço | Saldo USDT (23:55:41 UTC) | Bloqueado pela emissora |
|---|---|---|
| `TEcWfhn3h7X8UYR5REz4s2w9PMA1B2f21X` | **997,000000** | não |
| `TUWTzm2dnqKuBrkkM4s3JNoecD8H1UFi2y` | **3,000000** | não |
| vítima, `TQ5CUe…`, 1ª e 2ª camadas, drenador, `TEhWiZ…` | 0 | não |

Soma: 997 + 3 = 1.000 USDT, tudo localizado. `TEcWfhn…` não teve nenhuma saída de USDT até 23:55:50 UTC (C13). `TUWTzm…` nunca fez nenhuma transação própria (C12).

**Nada está bloqueado pela emissora.** Nenhum endereço da rota está na lista (C8, C13), e não houve evento `AddedBlackList` no contrato desde 23:00 UTC (C11).

Inferência: um só operador controla toda a cadeia. `TQ5CUe…` pagou o gás da 1ª camada, `TEcWfhn…` pagou o gás da 2ª camada (C11), e `TEhWiZ…` abasteceu tanto `TQ5CUe…` quanto `TEcWfhn…` (C12). As "camadas" não separam nada de verdade, o que ajuda num pedido de congelamento: dá para mostrar a ligação de ponta a ponta em uma página. O padrão "1 USDT a `TUWTzm…`" pode ser comissão de quem opera o drenador (hipótese).

## Pergunta 6. Probabilidade de recuperação em 12 meses

| Caminho | Estimativa | Raciocínio |
|---|---|---|
| Polícia + emissora | **6%** (2–15%) | A favor: 99,7% do valor está parado num único endereço, ainda não congelado, com ligação clara ao drenador. A emissora tem como congelar, e o contrato tem `addBlackList` e `destroyBlackFunds`. Contra: o operador pode mover o saldo a qualquer momento. Pedidos de congelamento costumam exigir ofício de autoridade, e casos de cerca de US$ 1.000 raramente andam em horas. Mesmo depois de congelado, a devolução depende de processo e de ordem judicial, que levam meses. |
| Ação judicial (cível, isolada) | **2%** (1–5%) | Réu desconhecido. Identificar exigiria ordens a corretoras quando o dinheiro chegar a uma, e por enquanto não chegou. O custo supera o valor. Só faz sentido acoplada a um congelamento já obtido, ou contra o recebedor do Pix, que é identificável pelo banco. |
| "Recuperador" | **< 1%** | Não há recuperação em curso (perguntas 2 e 3). O mais provável é aparecer uma nova "taxa". |
| MED (devolução do Pix de R$ 560) | **25%** (10–40%) | A contestação no banco da vítima leva ao bloqueio cautelar na conta recebedora, se ainda houver saldo. Golpistas esvaziam contas de passagem em minutos ou horas. Contestar logo (o Pix foi às 20:42) aumenta a chance. O prazo para contestar é de até 80 dias, mas a chance cai rápido. O BC anunciou em 2025 uma versão ampliada do MED, que segue o dinheiro além da primeira conta; não verifiquei se já vale no banco da vítima. |

## Pergunta 7. Providências, em ordem, e riscos ativos

**Riscos que continuam ativos (fatos):**
1. **Autorização de 9.999.000 USDT ao drenador** (C6, C13). Qualquer USDT que entrar em `TXXj87…` pode ser retirado na hora por `TQ5CUe…` via `charge`. R. disse o contrário ("pode voltar a usar normalmente"), o que empurra a vítima para uma nova perda. A autorização vale só para esse USDT. Os 25 TRX e o token TRC-10 não estão expostos a ela, e não há sinal de chave comprometida (pergunta 3).
2. **Nova extorsão por R.** ("taxa de saque", "imposto", "antilavagem") e abordagem por outros falsos recuperadores.
3. **Perda de prazo:** o saldo em `TEcWfhn…` pode sair a qualquer momento, e o saldo da conta Pix recebedora também.

**Ordem recomendada:**
1. **Agora:** contestar o Pix no app do banco ou na central (MED), informando golpe. Não pagar mais nada a R. e não mandar documentos nem fotos. Não depositar USDT em `TXXj87…`.
2. **Agora:** guardar as provas: prints da conversa com horário, perfil de R. (link e nome de usuário), **dados do recebedor do Pix (nome, chave, banco)**, que são a melhor pista de identificação do caso, link do site do "bônus", e os hashes e endereços deste parecer.
3. **Hoje:** registrar boletim de ocorrência (delegacia eletrônica ou de crimes cibernéticos) com estelionato e com a cadeia on-chain, pedindo que a autoridade solicite com urgência à emissora o congelamento de `TEcWfhn…` (997 USDT) e `TUWTzm…` (3 USDT). A vítima também pode comunicar o caso diretamente à emissora, anexando o B.O.
4. **Hoje:** revogar a autorização, assinando na própria carteira `approve(TCdNNrHkXBaxxSaD1beacDwmjMjEzDpof4, 0)` no contrato USDT, pelo app oficial da carteira e nunca por link recebido. Há TRX para a taxa. De preferência, passar a usar uma carteira nova, com frase nova, e tratar `TXXj87…` como descartada para USDT.
5. Denunciar o perfil de R. e o link do "bônus" na rede social. Bloquear R.
6. Desconfiar de qualquer novo contato que ofereça recuperação, inclusive de quem diga ser polícia, advogado ou "da Tether" e cobre adiantado.

## Pergunta 8. Que evidência nova mexeria em cada número

| Número | Subiria se… | Desceria se… |
|---|---|---|
| 1 (R. sabe que é falso, 97%) | Novo pedido de "taxa"; perfil de R. ligado a outras denúncias; recebedor do Pix sem relação com "plataforma" alguma; ligação on-chain entre R. e a rota | Prova de que R. repassou o dinheiro a um terceiro que o enganou (ainda assim, a cobrança continuaria indevida) |
| 6a (polícia + emissora, 6%) | `isBlackListed(TEcWfhn…)` passar a "SIM"; ofício enviado nas primeiras horas; saldo seguir parado; mais vítimas do mesmo drenador (o caso ganha peso) | Saída de `TEcWfhn…` para ponte, misturador ou troca descentralizada; demora no registro |
| 6b (judicial, 2%) | Fundos chegarem a corretora com cadastro (dá para pedir dados por ordem); congelamento já obtido | Destino sem cadastro; saldo pulverizado |
| 6c (recuperador, < 1%) | (nenhuma evidência realista) | – |
| 6d (MED, 25%) | Contestação nas primeiras horas; banco confirmar bloqueio cautelar com saldo | Conta recebedora esvaziada; contestação tardia |
| 4 (compatibilidade) | Vítima confirmar compra do USDT por volta de 20:24 e explicar a origem | Vítima negar ter recebido os 25 TRX, ou a compra não bater com `TEhWiZ…`. Aí a origem do saldo vira linha de investigação (vendedor ligado ao grupo) |
| Risco ativo | – | `allowance` voltar a 0 (revogação feita) |

---

## Limites deste parecer

- **Rede de teste e cenário encenado.** As transações são reais na Nile, mas sem valor. O contrato "USDT" de teste não é o da emissora real, e a "emissora" aqui é quem controla esse contrato. Probabilidades sobre polícia, emissora, Justiça e MED se apoiam em conhecimento geral sobre casos reais, não em dados medidos neste material.
- **Fonte única de dados on-chain:** TronGrid Nile (API e índice `/v1`). Não comparei com outro nó ou explorador. A busca de eventos `AddedBlackList` cobre só a partir de 23:00 UTC de 16/11/2026, com até 200 resultados.
- **Retrato no tempo:** saldos, bloqueio e autorização foram conferidos às 23:55 UTC (20:55 BRT). O dinheiro pode se mover, e um congelamento pode acontecer, depois disso. Refazer `estado` e `allowance` antes de usar este texto.
- **Material de segunda mão:** relato e conversa são transcrições. Não vi a imagem do "painel", só sua descrição, nem o comprovante Pix. Não sei quem é o recebedor do Pix nem qual é a chave.
- **Atribuição:** dizer que um só operador controla a cadeia é inferência a partir de financiamento cruzado de gás. Não identifica pessoas. A ligação entre R. e o golpista não foi demonstrada.
- **Faixas de probabilidade** são juízo do analista, para orientar decisões, e não estatística.
- Fiquei restrito ao material desta pasta e a consultas públicas de leitura. Não contatei ninguém, não assinei transações, não usei bases de dados vazadas nem busquei dados pessoais.
