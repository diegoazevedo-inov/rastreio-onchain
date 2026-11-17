# Rastreamento técnico on-chain com conferência por afirmação

Método para reconstruir, só com dados públicos, o que aconteceu com valores em USDT (TRC-20, rede TRON) depois de uma fraude, conferir afirmações de supostos "recuperadores" contra a blockchain e orientar as providências cabíveis. Inclui uma ferramenta de consulta somente-leitura e um caso completo encenado na rede de teste Nile.

## O que há aqui

| Caminho | Conteúdo |
|---|---|
| [`docs/PROTOCOLO.md`](docs/PROTOCOLO.md) | O método passo a passo: preservação, transação da perda, caminho dos valores, situação atual, conferência de afirmações, análises independentes, providências e limites |
| [`rastreio.py`](rastreio.py) | Consulta somente-leitura (TronGrid): decodifica transações, lista transferências e autorizações, consulta bloqueio pela emissora, saldo e autorização vigente, segue saídas salto a salto e mostra quem pagou o TRX de cada endereço. Grava as respostas brutas com manifesto SHA-256 |
| [`teste_rastreio.py`](teste_rastreio.py) | Testes offline, incluindo a reexecução de cada consulta guardada no exemplo a partir das respostas brutas |
| [`modelos/`](modelos/) | Modelo de relatório "afirmação × prova" e tabela de sinais do golpe da recuperação, cada um com a forma de verificar |
| [`auditoria/`](auditoria/) | Roteiro das três análises independentes (uma com papel cético) e o script que planta defeitos para medir os testes |
| [`exemplo-sintetico/`](exemplo-sintetico/) | Caso encenado na Nile: montagem, gabarito, consultas guardadas, evidências fictícias, relatório-exemplo e as três análises |

## Uso

```bash
python3 rastreio.py --rede nile tx HASH
python3 rastreio.py estado ENDERECO [ENDERECO ...]
python3 rastreio.py allowance DONO GASTADOR
python3 rastreio.py transferencias ENDERECO [--desde ISO] [--ate ISO]
python3 rastreio.py seguir ENDERECO --desde 2026-01-01T12:00:00 --ignorar ENDERECO_DE_TAXA
python3 rastreio.py abastecimento END1 END2 END3   # quem pagou o TRX; ligações entre eles
```

Sem `--rede`, a consulta é na rede principal. Cada execução grava as respostas brutas, a saída e um manifesto em `execucoes/AAAAMMDD-HHMMSS-comando/` (ou na pasta de `--pasta`; `--sem-registro` não grava). Nada é assinado nem enviado: o script só lê.

O `rastreio.py` usa só a biblioteca padrão do Python 3.10 ou mais recente. Os scripts que montaram o exemplo sintético precisam de dependências próprias (`exemplo-sintetico/requirements.txt`).

## Verificação

```bash
python3 -m unittest -v teste_rastreio            # testes offline
python3 auditoria/defeitos_plantados.py          # planta 22 defeitos conhecidos; cada um deve ser detectado
python3 exemplo-sintetico/conferir.py            # relatório-exemplo contra as consultas guardadas
```

## Limites

- Não substitui exame oficial nem orientação jurídica.
- A chance de recuperar cripto desviada é baixa. O caminho legítimo passa por advogado e autoridade policial.
- Titular de carteira de serviço sem rótulo verificável é inferência, não fato.

## Uso de IA

Os scripts e textos foram escritos com uma ferramenta de IA generativa (Claude, da Anthropic), sob supervisão humana. Nenhum dado vem do modelo: os fatos de um relatório saem das consultas registradas em `execucoes/`.

## Licença

Apache 2.0 ([`LICENSE`](LICENSE)). Para citar, veja [`CITATION.cff`](CITATION.cff).
