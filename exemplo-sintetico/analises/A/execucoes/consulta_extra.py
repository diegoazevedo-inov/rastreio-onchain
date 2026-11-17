#!/usr/bin/env python3
"""Consultas somente-leitura extras à nile.trongrid.io; grava resposta bruta + manifesto."""
import json, sys, pathlib, hashlib, datetime as dt, urllib.request, time
API = "https://nile.trongrid.io"
base = pathlib.Path(sys.argv[1]); base.mkdir(parents=True, exist_ok=True)
pedidos = json.loads(sys.argv[2])  # lista de [rotulo, caminho, corpo|null]
for rot, cam, corpo in pedidos:
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(API + cam, data=dados, headers={"User-Agent": "rastreio-onchain/0.1", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        resp = json.load(r)
    (base / f"{rot}.json").write_text(json.dumps({"url": API + cam, "corpo": corpo, "consultado_em": dt.datetime.now(dt.UTC).isoformat(), "resposta": resp}, ensure_ascii=False, indent=1))
    print(f"== {rot}\n" + json.dumps(resp, ensure_ascii=False)[:3000])
    time.sleep(0.3)
m = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in sorted(base.glob('*.json'))]
(base / "MANIFEST.sha256").write_text("\n".join(m) + "\n")
