# Análise independente: análise B

Você vai analisar um caso de fraude com criptomoeda **encenado numa rede de teste** (TRON Nile). As transações existem de fato na rede de teste, sem valor financeiro. Pessoas, conversa e Pix são fictícios, mas trate o material como se fosse um caso real.

Existem outras análises do mesmo caso. Você não tem acesso a elas nem a nenhum relatório anterior, e não deve procurá-los.

## Material

Use só o que está nesta pasta:

- `evidencias/LEIA-ME.md`: pontos de partida públicos (endereço da vítima, hash da perda, contrato do token);
- `evidencias/relato-vitima.md`: relato de segunda mão da vítima;
- `evidencias/conversa-ficticia.md`: conversa da vítima com quem se apresenta como "recuperador";
- `rastreio.py`: ferramenta somente-leitura de consulta à TronGrid. Use sempre `--rede nile`; rode `python3 rastreio.py -h`. Você também pode consultar `https://nile.trongrid.io` diretamente.

Refaça as consultas você mesmo. Toda afirmação de fato precisa apontar para uma consulta que você fez: hash, endereço, horário, valor.

## Proibições

- não contatar ninguém nem enviar mensagens;
- não assinar nem enviar transações (só leitura);
- não ler arquivos fora desta pasta;
- não usar bases de dados vazadas nem buscar dados pessoais.

## Perguntas

Para cada uma: probabilidade (quando couber), justificativa, evidência. Separe fato de inferência.

1. Qual a probabilidade de o "recuperador" estar cobrando por uma recuperação que sabe ser falsa?
2. Para cada prova que ele apresenta (hash, imagem descrita): autêntica, falsa ou inconclusiva, e o motivo técnico.
3. Cada afirmação técnica dele: verdadeira ou falsa, e por quê.
4. O relato da vítima sobre como perdeu o valor é compatível com a blockchain? Qual foi o mecanismo?
5. Onde está o valor hoje, por qual caminho chegou lá, e há algo bloqueado pela emissora?
6. Probabilidade de recuperar parte relevante em 12 meses, por caminho: polícia e emissora, ação judicial, "recuperador". E a chance de devolução do Pix pelo MED.
7. Que providências, em que ordem? Há algum risco que continua ativo para a vítima?
8. Que evidência nova faria cada número subir ou descer?

## Entrega

Grave **`PARECER.md` nesta pasta**. Comece por uma tabela-resumo com as probabilidades e termine com uma seção "Limites deste parecer". Não use os termos "perícia" nem "laudo pericial".
