# Protocolo de rastreamento técnico on-chain (USDT na rede TRON)

Este protocolo descreve como reconstruir, só com dados públicos, o que aconteceu com valores em USDT (TRC-20) depois de uma fraude, conferir afirmações de terceiros contra a blockchain e orientar as providências cabíveis. Não substitui exame oficial nem orientação jurídica.

## Princípios

1. **Cada afirmação aponta para um dado.** Todo fato do relatório tem ao lado a consulta que o sustenta: transação, chamada de contrato ou página citada. A saída bruta fica guardada com hash (`execucoes/`).
2. **Somente leitura.** Nada é assinado nem enviado. Não se pede nem se recebe frase de recuperação, chave privada, senha ou acesso remoto ao aparelho da vítima.
3. **Fato separado de inferência.** "A transação X transferiu Y" é fato. "O endereço Z é de uma corretora" é inferência, e o texto diz isso.
4. **Probabilidade é estimativa.** Quando houver números de chance, eles vêm de julgamento fundamentado e são apresentados assim, nunca como medição.
5. **Quem executa não audita.** A conclusão passa por análises independentes, conduzidas sem acesso ao trabalho de quem rastreou (seção 7).

## 1. Preservação

Antes de qualquer análise:

- exportar a conversa com quem aplicou o golpe e com qualquer "recuperador", **com mídia** (o arquivo `.zip` original);
- guardar prints, comprovantes de Pix e e-mails exatamente como chegaram;
- anotar a carteira usada (aplicativo, rede, endereço público) e os horários informados pela vítima, com o fuso.

## 2. A transação da perda

1. Achar, pelo endereço público da vítima, a transferência de saída do valor (`rastreio.py transferencias ENDERECO --desde ...`).
2. Decodificar essa transação (`rastreio.py tx HASH`) e responder:
   - **de qual conta saiu e com que permissão?** O `rastreio.py tx` mostra a conta (`owner_address`) e o número da permissão usada. Permissão 0 é a de dono. Se a transação saiu da conta da vítima com a permissão de dono, e as permissões da conta continuam as originais (consulta `getaccount`), foi a chave da vítima que assinou: ela autorizou algo, mesmo sem perceber. Outra permissão, ou permissões alteradas, indicam outra forma de acesso;
   - **qual função?** Uma `transfer` feita pela conta da vítima é diferente de uma `transferFrom` executada por terceiro.
3. Se a saída foi `transferFrom` por terceiro, procurar a **autorização anterior** (`approve`, `increaseApproval`, `increaseAllowance`) feita pela conta da vítima, normalmente minutos ou segundos antes. Ela mostra o "gastador" autorizado e o limite concedido.

### Padrões conhecidos

- **Drenagem por autorização.** O site falso pede uma "confirmação" que, na verdade, é uma autorização de gasto com limite enorme a um contrato do golpista. Depois, o golpista puxa o saldo sem precisar de nova assinatura. Nos aplicativos de celular, a confirmação costuma ser biométrica: a vítima "só usou o rosto ou o dedo" e não digitou senha. O relato é compatível com a blockchain.
- **Aluguel de energia.** Antes da autorização, o site pode pedir um pequeno envio de TRX para "alugar energia", que paga a transação seguinte.
- **Indício de que a chave privada não vazou:** a vítima mantém o saldo em TRX e as permissões da conta continuam as originais. Quem tem a chave transfere tudo diretamente.

## 3. O caminho dos valores

1. A partir do endereço do golpista e da hora da perda, seguir as saídas salto a salto (`rastreio.py seguir ENDERECO --desde ...`).
2. **Excluir endereços de cobrança.** Um endereço que recebe o mesmo valor pequeno em vários saltos e não repassa nada costuma ser de cobrança de taxa (por exemplo, de um serviço que paga o TRX das transferências). Ele não faz parte do caminho e contamina o rastreio se for seguido (`--ignorar`).
3. **Reconhecer endereços de depósito.** Um endereço que recebe e repassa tudo em cerca de um minuto, às vezes depois de um pequeno valor de teste, costuma ser o endereço de depósito de um cliente dentro de um serviço centralizado.
4. **Conferir quem pagou o TRX** (`rastreio.py abastecimento END1 END2 ...`), antes de concluir que um endereço é de serviço. Se o destino abasteceu com TRX os endereços que lhe repassam valores, ou se o operador e o destino têm a mesma origem de TRX, a cadeia é do mesmo grupo (circuito fechado), e o valor ainda não chegou a um serviço de terceiros.
5. **Parar na carteira de serviço.** Um endereço com saldo de milhões e dezenas de movimentos por minuto é, provavelmente, a carteira operacional de uma corretora, mesa de balcão ou processadora. Dali em diante, os valores se misturam com os de terceiros. Identificar o titular cabe a quem tem acesso a etiquetas pagas ou à autoridade.
6. Registrar a tabela do caminho: hora (UTC), origem, destino, valor, hash.

## 4. A situação atual

Para cada endereço do caminho (`rastreio.py estado ...`):

- **bloqueio pela emissora** (`isBlackListed`): se a emissora do USDT já congelou o endereço;
- **saldo atual** (`balanceOf`);
- **autorização ainda ativa** (`rastreio.py allowance VITIMA GASTADOR`). Se o limite não foi zerado, **qualquer USDT que entrar na carteira da vítima pode ser retirado de novo.** É a providência técnica mais urgente: revogar a autorização ou abandonar a carteira.

## 5. Conferência das afirmações de terceiros

Depois da fraude, é comum aparecer um "recuperador". Cada afirmação dele vira uma linha do modelo `modelos/relatorio-afirmacao-prova.md`, conferida contra o dado:

| Tipo de afirmação | Como conferir |
|---|---|
| "Bloqueei" ou "está retido", com um hash como prova | Decodificar o hash: quem enviou, para onde, quando. Comparar a hora com o primeiro contato dele e ver se o valor seguiu adiante. |
| Print de painel com valor "bloqueado" | Procurar o valor exato nas transferências públicas. Conferir se, na hora do print, o valor ainda estava naquele endereço. |
| "Tudo bloqueado" | `isBlackListed` e saldo de cada endereço do caminho. |
| Programa ou "chave" que precisa ser comprada | Página oficial do software: licença, preço, para que serve e o que exige (por exemplo, chaves do próprio usuário). |
| "Taxa da plataforma" | Política oficial da carteira ou da emissora sobre reversão, congelamento e cobrança. Comparar a data do pedido de taxa com a do primeiro contato com a plataforma. |
| Comprovante de gasto | Data e valor contra a linha do tempo: um gasto anterior à fraude não pode ter saído do dinheiro da vítima. Conferir se o documento existe no formato que o emissor de fato usa. |

Sinais de comportamento estão em `modelos/sinais-golpe-recuperacao.md`, cada um com a forma de verificar.

## 6. Identificação do recebedor de valores em reais

Quando a vítima pagou o "recuperador" por Pix:

- o comprovante do banco pagador mostra o nome e parte do CPF do recebedor, e a instituição. Isso vem do cadastro bancário, não do nome salvo no contato;
- conferir os dígitos verificadores do CPF, quando ele aparece por completo (por exemplo, como chave Pix);
- busca em fontes abertas, se for o caso, **sem bases vazadas**, distinguindo autodeclaração, matéria de imprensa e registro oficial conferido na fonte.

Nada disso entra em material público.

## 7. Análises independentes

A conclusão passa por três análises conduzidas separadamente, nenhuma com acesso às outras nem ao relatório de quem rastreou (roteiro em `auditoria/ROTEIRO-ANALISTAS.md`):

- todas recebem só as evidências brutas e refazem as consultas;
- uma delas tem o papel explícito de **cética**: procura a hipótese mais favorável ao "recuperador" e só a descarta se a evidência obrigar;
- cada uma dá a sua estimativa para as mesmas perguntas. O relatório final mostra as três lado a lado, com onde concordam e onde divergem.

## 8. Providências

Em ordem de urgência:

1. **Não pagar mais nada** a quem promete recuperação. **Não avisar** o "recuperador" de que o golpe foi descoberto antes de pedir o bloqueio dos valores em reais.
2. **Revogar a autorização** ou abandonar a carteira.
3. **MED do Pix** (Mecanismo Especial de Devolução): pedir pelo aplicativo do banco pagador, pela conta que fez o Pix, o quanto antes. O prazo e as condições são os do regulamento do Pix, do Banco Central, e devem ser confirmados com o banco. A chance de haver saldo na conta recebedora cai a cada hora.
4. **Consultar advogado de confiança** **antes** de levar o caso à polícia, levando o relatório.
5. **Com o advogado, a autoridade policial**, que pode oficiar o serviço dono da carteira final e pedir à emissora o congelamento do que restar. Promessas de recuperação fora da via policial e judicial costumam ser o próprio golpe da recuperação.

## 9. Linguagem e limites

- Não usar "perícia" nem "laudo pericial": são termos com peso legal próprio.
- Dizer com clareza que a chance de recuperar cripto desviada é baixa.
- Não afirmar quem é o titular de uma carteira de serviço sem rótulo verificável.
- Não fazer reconhecimento facial nem afirmar identidade por foto. Se houver fotos, quem viu a pessoa compara.
- Material público usa **exemplo sintético** (rede de teste). Nenhum dado de caso real.
