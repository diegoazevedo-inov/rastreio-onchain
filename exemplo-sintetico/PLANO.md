# Exemplo sintético (rede de teste Nile)

Reprodução, numa rede de teste e sem dinheiro real, do padrão completo de uma drenagem por autorização seguida de dispersão, com um "recuperador" fictício. Serve para exercitar o protocolo e o `rastreio.py` com saídas brutas conferíveis.

## Personagens

Carteiras de teste geradas só para isto (`carteiras.json`; as chaves ficam num `.env` local, fora do repositório).

| Papel | O que faz |
|---|---|
| banco | Recebe TRX e USDT de teste da torneira oficial da Nile e abastece os demais |
| vítima | Recebe 1.000 USDT; assina a autorização no "site falso" |
| contrato drenador | `contratos/DrenadorTeste.sol`: `charge(usuario, valor)` executa `transferFrom` para quem o implantou |
| operador | Implanta o drenador, envia TRX à vítima e chama `charge` |
| intermediárias (3) | Recebem lotes do operador e repassam |
| endereços da 2ª camada (3) | Recebem um valor de teste e o restante, e repassam tudo ao destino |
| destino | Concentra os valores e paga o TRX da 2ª camada |
| cobrança | Recebe 1 USDT de cada intermediária |

## Roteiro encenado

28 transações, registradas em `encenacao.json` (o gabarito):

1. abastecimento de TRX do operador e do destino;
2. a vítima recebe 1.000 USDT ("compra");
3. o operador implanta o drenador e envia 25 TRX à vítima ("aluguel de energia");
4. a vítima assina `increaseApproval(drenador, 10.000.000 USDT)`;
5. o operador chama `charge(vítima, 1.000)`;
6. o operador abastece as intermediárias com TRX e envia lotes de 410, 340 e 250 USDT;
7. o destino abastece a 2ª camada com TRX;
8. cada intermediária paga 1 USDT de cobrança, envia 5 USDT de teste e depois o restante;
9. a 2ª camada repassa tudo ao destino.

## Arquivos

| Caminho | Conteúdo |
|---|---|
| `carteiras.py`, `encenar.py` | Geram as carteiras e executam o roteiro (retomável) |
| `contratos/` | Fonte do drenador, artefato compilado e `compilar.py` |
| `encenacao.json` | Gabarito: cada passo com hash e hora |
| `execucoes/` | Consultas do protocolo com `rastreio.py --rede nile`, com respostas brutas e manifesto |
| `evidencias/` | Relato e conversa fictícios: o que as análises receberam |
| `relatorio-exemplo.md` | Relatório no modelo "afirmação × prova" |
| `relatorio-exemplo.pdf` | O mesmo relatório em PDF, com as três análises e a comparação anexadas (`relatorio_pdf.py`) |
| `analises/` | As três análises independentes, com briefings, consultas e comparação |
| `conferir.py` | Confere o relatório contra as consultas guardadas e o gabarito |

## Como reproduzir

- **Sem rede:** `python3 -m unittest teste_rastreio` reexecuta cada consulta de `execucoes/` a partir das respostas guardadas; `python3 exemplo-sintetico/conferir.py` confere o relatório.
- **PDF:** `python3 relatorio_pdf.py exemplo-sintetico/relatorio-exemplo.md --saida exemplo-sintetico/relatorio-exemplo.pdf --anexo "Análise A" exemplo-sintetico/analises/A/PARECER.md --anexo "Análise B" exemplo-sintetico/analises/B/PARECER.md --anexo "Análise C (papel cético)" exemplo-sintetico/analises/C/PARECER.md --anexo-autor "Comparação das análises" exemplo-sintetico/analises/COMPARACAO.md`.
- **Contra a Nile:** os comandos de `execucoes/*/comando.txt` refazem as consultas; as saídas devem bater com `saida.txt`, salvo a hora da consulta, enquanto os saldos não mudarem. Duas linhas mudaram de rótulo depois da gravação: em `tx`, "assinada por …" virou "conta … (permissão …)"; no TRC-10 de `abastecimento`, o comentário final virou "(token TRC-10, não é USDT)". O `teste_rastreio.py` aplica essa troca ao comparar.
- **Remontar a encenação:** exige instalar `requirements.txt`, gerar carteiras novas e pedir TRX e USDT de teste na torneira da Nile (com verificação humana). Os endereços e hashes serão outros.

## Limites

- Uma única carteira abasteceu a vítima, o operador e o destino, o que liga todos os papéis e denuncia a montagem. Num caso real, origem comum assim apontaria para um vendedor ligado ao grupo.
- Uma carteira de serviço de verdade, com milhares de movimentos, não pode ser simulada com poucas carteiras. A regra de parar em carteira de serviço é coberta só pelos testes.
- O contrato se chama "DrenadorTeste", de propósito, para que não seja confundido com código de uso real.
- O "recuperador" fictício só faz afirmações verificavelmente falsas. O exemplo não cobre afirmações ambíguas ou parcialmente verdadeiras.

## Cuidados

- O contrato drenador só existe na rede de teste, e o repositório não traz instrução de uso em rede principal.
- Nenhum endereço, valor, data, texto ou imagem de caso real.
