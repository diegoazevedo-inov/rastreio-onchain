#!/usr/bin/env python3
"""Confere o relatório-exemplo contra as consultas guardadas e o gabarito da encenação.

O que confere:
- toda abreviação de endereço (Txxxxx…yyy) e de hash (`xxxxxxxx…`) corresponde a um endereço
  de carteiras.json/contrato ou a um hash de encenacao.json;
- toda pasta de execução citada existe;
- seção 3 (caminho): em cada linha com hash, o valor e as pontas (De, Para), quando abreviadas,
  batem com a transferência registrada nas respostas brutas (`execucoes/*/respostas`);
- seção 4 (situação atual): saldo e bloqueio de cada endereço abreviado batem com a consulta
  `estado` mais recente;
- quais passos do gabarito aparecem nas saídas das consultas.

O que não confere: o texto corrido, as afirmações da seção 5, horários, e os papéis atribuídos
(operador, destino etc.), que são inferência do relatório.

Sai com código 1 se houver divergência. Uso: python3 conferir.py
"""
import json
import pathlib
import re
import sys

AQUI = pathlib.Path(__file__).parent
EXE = AQUI / "execucoes"
rel = (AQUI / "relatorio-exemplo.md").read_text()
gab = json.loads((AQUI / "encenacao.json").read_text())
cart = json.loads((AQUI / "carteiras.json").read_text())["carteiras"]
contratos = [p["contrato"] for p in gab["passos"] if "contrato" in p]
enderecos = [v["endereco"] for v in cart.values()] + contratos
hashes = [p["txid"] for p in gab["passos"]]
pastas = {d.name for d in EXE.iterdir()}
saidas = "".join(p.read_text() for p in EXE.rglob("saida.txt"))
ABREV = re.compile(r"\b(T[1-9A-HJ-NP-Za-km-z]{5})…([1-9A-HJ-NP-Za-km-z]{3,8})\b")
HASH = re.compile(r"`([0-9a-f]{8})…`")

# transferências registradas nas respostas brutas (TronGrid /transactions/trc20)
transf = {}
for f in EXE.glob("*/respostas/*.json"):
    d = json.loads(f.read_text())
    for x in (d.get("resposta") or {}).get("data", []) if isinstance(d.get("resposta"), dict) else []:
        if isinstance(x, dict) and x.get("type") == "Transfer" and "transaction_id" in x:
            transf[x["transaction_id"]] = x

# situação atual: consulta `estado` mais recente
estado = {}
ultima = sorted(p for p in EXE.iterdir() if p.name.endswith("-estado"))[-1]
for linha in (ultima / "saida.txt").read_text().splitlines():
    m = re.match(r"^(T\w{33})\s+(SIM|não)\s+([\d.,]+)$", linha.strip())
    if m:
        estado[m[1]] = (m[2].lower(), float(m[3].replace(".", "").replace(",", ".")))


def numero(s):
    return float(s.replace(".", "").replace(",", "."))


def secao(n):
    m = re.search(rf"^## {n}\..*?(?=^## {n + 1}\.)", rel, re.S | re.M)
    return m.group(0) if m else ""


def resolve(a, b):
    achados = [e for e in enderecos if e.startswith(a) and e.endswith(b)]
    return achados[0] if len(achados) == 1 else None


erros = []
n3 = n4 = 0
for a, b in ABREV.findall(rel):
    if not resolve(a, b):
        erros.append(f"endereço abreviado sem correspondente: {a}…{b}")
for h in HASH.findall(rel):
    if not any(x.startswith(h) for x in hashes):
        erros.append(f"hash abreviado sem correspondente: {h}…")
for d in sorted(set(re.findall(r"`(\d{8}-\d{6}-\w+)`", rel)) - pastas):
    erros.append(f"pasta de execução citada e inexistente: {d}")

# seção 3: valores e pontas
for linha in secao(3).splitlines():
    cols = [c.strip() for c in linha.strip().strip("|").split("|")]
    if len(cols) < 6 or not HASH.search(cols[4]):
        continue
    hs = [next((t for t in transf if t.startswith(h)), None) for h in HASH.findall(cols[4])]
    vals = [numero(v) for v in re.findall(r"\d[\d.]*", cols[3])]
    if len(vals) == 1:
        vals = vals * len(hs)
    if len(vals) != len(hs):
        erros.append(f"seção 3: não consegui casar valores e hashes em: {linha.strip()[:80]}")
        continue
    n3 += 1
    for h, v in zip(hs, vals):
        if h is None:
            erros.append(f"seção 3: hash sem transferência registrada nas consultas: {linha.strip()[:80]}")
            continue
        x = transf[h]
        if int(x["value"]) != int(round(v * 10**6)):
            erros.append(f"seção 3: valor {v:g} diverge do registrado ({int(x['value']) / 10**6:g}) em {h[:8]}…")
        for col, ponta in ((cols[1], "from"), (cols[2], "to")):
            m = ABREV.search(col)
            if m and resolve(*m.groups()) != x[ponta]:
                erros.append(f"seção 3: '{ponta}' de {h[:8]}… é {x[ponta]}, não {m[1]}…{m[2]}")

# seção 4: saldo e bloqueio
for linha in secao(4).splitlines():
    cols = [c.strip() for c in linha.strip().strip("|").split("|")]
    m = ABREV.search(cols[0]) if len(cols) >= 3 else None
    if not m:
        continue
    end = resolve(*m.groups())
    if end not in estado:
        erros.append(f"seção 4: {m[1]}…{m[2]} não está na consulta {ultima.name}")
        continue
    bloq, saldo = estado[end]
    n4 += 1
    if cols[1].lower() != bloq:
        erros.append(f"seção 4: bloqueio de {m[1]}…{m[2]} é '{bloq}' na consulta, não '{cols[1]}'")
    if abs(numero(re.findall(r"\d[\d.,]*", cols[2])[0]) - saldo) > 1e-6:
        erros.append(f"seção 4: saldo de {m[1]}…{m[2]} é {saldo:g} na consulta, não {cols[2]}")

if n3 == 0 or n4 == 0:
    erros.append(f"tabelas das seções 3 e 4 não reconhecidas ({n3} e {n4} linhas)")
print(f"seção 3: {n3} linhas conferidas contra as transferências; seção 4: {n4} contra {ultima.name}")
vistos = [p["passo"] for p in gab["passos"] if p["txid"][:16] in saidas]
fora = [p["passo"] for p in gab["passos"] if p["txid"][:16] not in saidas]
print(f"{len(vistos)} de {len(gab['passos'])} passos do gabarito aparecem nas consultas")
print("não aparecem:", ", ".join(fora) or "nenhum")
for e in erros:
    print("ERRO", e)
print("PASSA" if not erros else "NÃO PASSA")
sys.exit(1 if erros else 0)
