#!/usr/bin/env python3
"""Consulta somente-leitura de transações e saldos de USDT (TRC-20) na rede TRON.

Nada aqui assina, envia ou altera estado na blockchain: só lê APIs públicas
(TronGrid). Cada execução grava as respostas brutas, a saída e um manifesto
SHA-256 em execucoes/, para que toda afirmação de um relatório aponte para um
arquivo conferível.

Uso:
  python3 rastreio.py [--rede mainnet|nile] tx HASH
  python3 rastreio.py [--rede ...] transferencias ENDERECO [--desde ISO] [--ate ISO]
  python3 rastreio.py [--rede ...] estado ENDERECO [ENDERECO ...]
  python3 rastreio.py [--rede ...] allowance DONO GASTADOR
  python3 rastreio.py [--rede ...] seguir ENDERECO --desde ISO [--saltos N] [--ignorar END ...]
  python3 rastreio.py [--rede ...] abastecimento ENDERECO [ENDERECO ...] [--desde ISO] [--ate ISO]

Opções gerais: --sem-registro (não grava em execucoes/), --pasta DIR.
Só biblioteca padrão do Python (3.10+).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REDES = {
    "mainnet": {"api": "https://api.trongrid.io", "usdt": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"},
    "nile": {"api": "https://nile.trongrid.io", "usdt": "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"},
}
DECIMAIS = 6

# Seletores (4 primeiros bytes do keccak-256 da assinatura). Conferíveis em 4byte.directory.
SELETORES = {
    "a9059cbb": ("transfer", ("address", "uint256")),
    "23b872dd": ("transferFrom", ("address", "address", "uint256")),
    "095ea7b3": ("approve", ("address", "uint256")),
    "d73dd623": ("increaseApproval", ("address", "uint256")),
    "39509351": ("increaseAllowance", ("address", "uint256")),
    # Nome comum em contratos drenadores: quem implanta chama charge(vitima, valor) e o
    # contrato executa transferFrom com a autorização dada antes pela vítima.
    "a3ffa9cd": ("charge", ("address", "uint256")),
}
# Tópicos de evento (keccak-256 da assinatura completa).
EVENTOS = {
    "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef": "Transfer",
    "8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925": "Approval",
}

# ---------------------------------------------------------------- endereços

_ALFABETO = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _sha256d(b: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()


def hex_para_base58(h: str) -> str:
    """'41' + 20 bytes (hex) -> endereço T... com checksum."""
    h = h.lower().removeprefix("0x")
    if len(h) == 40:
        h = "41" + h
    raw = bytes.fromhex(h)
    raw += _sha256d(raw)[:4]
    n = int.from_bytes(raw, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = _ALFABETO[r] + out
    return "1" * (len(raw) - len(raw.lstrip(b"\0"))) + out


def base58_para_hex(a: str) -> str:
    """Endereço T... -> '41' + 20 bytes (hex). Confere o checksum."""
    n = 0
    for c in a:
        n = n * 58 + _ALFABETO.index(c)
    raw = n.to_bytes(25, "big")
    if _sha256d(raw[:21])[:4] != raw[21:]:
        raise ValueError(f"checksum inválido: {a}")
    return raw[:21].hex()


def palavra_para_endereco(palavra: str) -> str:
    return hex_para_base58("41" + palavra[-40:])


def decodificar_chamada(data: str) -> dict:
    """Decodifica o 'data' de uma chamada a contrato TRC-20 conhecida."""
    data = data.lower().removeprefix("0x")
    sel, corpo = data[:8], data[8:]
    if sel not in SELETORES:
        return {"seletor": sel, "funcao": None}
    nome, tipos = SELETORES[sel]
    args = []
    for i, tipo in enumerate(tipos):
        palavra = corpo[i * 64:(i + 1) * 64]
        if tipo == "address":
            args.append(palavra_para_endereco(palavra))
        else:
            args.append(int(palavra, 16))
    return {"seletor": sel, "funcao": nome, "argumentos": args}


def valor_usdt(inteiro: int) -> str:
    return f"{inteiro / 10**DECIMAIS:,.6f}".replace(",", "X").replace(".", ",").replace("X", ".")


def hora_utc(ms: int) -> str:
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def iso_para_ms(s: str) -> int:
    t = dt.datetime.fromisoformat(s)
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return int(t.timestamp() * 1000)

# ---------------------------------------------------------------- registro


class Registro:
    """Guarda cada resposta bruta e a saída da execução, com manifesto SHA-256."""

    def __init__(self, base: pathlib.Path | None, comando: str):
        self.dir = None
        self.n = 0
        self.linhas: list[str] = []
        if base is not None:
            carimbo = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
            self.dir = base / f"{carimbo}-{comando}"
            (self.dir / "respostas").mkdir(parents=True, exist_ok=True)

    def resposta(self, rotulo: str, url: str, corpo: dict | None, resposta: dict) -> None:
        if self.dir is None:
            return
        self.n += 1
        nome = f"{self.n:03d}-{rotulo}.json"
        (self.dir / "respostas" / nome).write_text(
            json.dumps({"url": url, "corpo": corpo, "resposta": resposta}, ensure_ascii=False, indent=1))

    def dizer(self, texto: str = "") -> None:
        print(texto)
        self.linhas.append(texto)

    def fechar(self, argv: list[str]) -> None:
        if self.dir is None:
            return
        (self.dir / "saida.txt").write_text("\n".join(self.linhas) + "\n")
        (self.dir / "comando.txt").write_text(" ".join(argv) + "\n")
        manifesto = []
        for p in sorted(self.dir.rglob("*")):
            if p.is_file() and p.name != "MANIFEST.sha256":
                manifesto.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(self.dir)}")
        (self.dir / "MANIFEST.sha256").write_text("\n".join(manifesto) + "\n")
        print(f"\n[registro] {self.dir}", file=sys.stderr)

# ---------------------------------------------------------------- API


class Tron:
    def __init__(self, rede: str, reg: Registro):
        self.api = REDES[rede]["api"]
        self.usdt = REDES[rede]["usdt"]
        self.reg = reg

    def _req(self, rotulo: str, caminho: str, corpo: dict | None = None) -> dict:
        url = self.api + caminho
        dados = json.dumps(corpo).encode() if corpo is not None else None
        req = urllib.request.Request(url, data=dados, headers={"User-Agent": "rastreio-onchain/0.1",
                                                               "Content-Type": "application/json"})
        for tentativa in range(4):
            try:
                with urllib.request.urlopen(req, timeout=40) as r:
                    resp = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429 and tentativa < 3:
                    time.sleep(2 * (tentativa + 1))
                    continue
                raise
        self.reg.resposta(rotulo, url, corpo, resp)
        time.sleep(0.25)  # gentileza com o limite público
        return resp

    def transacao(self, h: str) -> tuple[dict, dict]:
        tx = self._req("tx", "/wallet/gettransactionbyid", {"value": h, "visible": True})
        info = self._req("tx-info", "/wallet/gettransactioninfobyid", {"value": h})
        return tx, info

    def constante(self, funcao: str, params_hex: str, rotulo: str) -> int:
        r = self._req(rotulo, "/wallet/triggerconstantcontract",
                      {"owner_address": self.usdt, "contract_address": self.usdt,
                       "function_selector": funcao, "parameter": params_hex, "visible": True})
        return int(r["constant_result"][0], 16)

    def transferencias(self, end: str, desde: int | None, ate: int | None, limite: int = 1000) -> list[dict]:
        itens, fingerprint = [], None
        while len(itens) < limite:
            q = {"limit": 200, "contract_address": self.usdt, "order_by": "block_timestamp,asc"}
            if desde:
                q["min_timestamp"] = desde
            if ate:
                q["max_timestamp"] = ate
            if fingerprint:
                q["fingerprint"] = fingerprint
            r = self._req("trc20", f"/v1/accounts/{end}/transactions/trc20?" + urllib.parse.urlencode(q))
            itens += r.get("data", [])
            fingerprint = r.get("meta", {}).get("fingerprint")
            if not fingerprint:
                break
        return itens

    def transacoes_conta(self, end: str, desde: int | None, ate: int | None, limite: int = 1000) -> list[dict]:
        """Todas as transações da conta (TRX, TRC-10, contratos), em ordem cronológica."""
        itens, fingerprint = [], None
        while len(itens) < limite:
            q = {"limit": 200, "order_by": "block_timestamp,asc"}
            if desde:
                q["min_timestamp"] = desde
            if ate:
                q["max_timestamp"] = ate
            if fingerprint:
                q["fingerprint"] = fingerprint
            r = self._req("conta", f"/v1/accounts/{end}/transactions?" + urllib.parse.urlencode(q))
            itens += r.get("data", [])
            fingerprint = r.get("meta", {}).get("fingerprint")
            if not fingerprint:
                break
        return itens


def eventos_trx(txs: list[dict], end: str) -> list[dict]:
    """Resume as transações de uma conta do ponto de vista de `end`.

    Tipos: TRX (envio de TRX), TRC10 (token TRC-10, não é USDT),
    CRIA_CONTRATO (implantação de contrato por `end`) e CONTRATO (chamada de contrato
    feita pela conta `end`, como as de USDT). Sentido: ENTRA ou SAI.
    """
    evs = []
    for t in txs:
        c = t["raw_data"]["contract"][0]
        v = c["parameter"]["value"]
        de = hex_para_base58(v["owner_address"]) if "owner_address" in v else None
        para = hex_para_base58(v["to_address"]) if "to_address" in v else None
        ok = (t.get("ret") or [{}])[0].get("contractRet", "SUCCESS") == "SUCCESS"
        base = {"hora": t["block_timestamp"], "hash": t["txID"], "ok": ok}
        if c["type"] == "TransferContract":
            evs.append({**base, "tipo": "TRX", "sentido": "SAI" if de == end else "ENTRA",
                        "outro": para if de == end else de, "valor": int(v.get("amount", 0))})
        elif c["type"] == "TransferAssetContract":
            evs.append({**base, "tipo": "TRC10", "sentido": "SAI" if de == end else "ENTRA",
                        "outro": para if de == end else de, "valor": int(v.get("amount", 0)),
                        "token": v.get("asset_name")})
        elif c["type"] == "CreateSmartContract" and de == end:
            evs.append({**base, "tipo": "CRIA_CONTRATO", "sentido": "SAI", "outro": None, "valor": 0})
        elif c["type"] == "TriggerSmartContract" and de == end:
            evs.append({**base, "tipo": "CONTRATO", "sentido": "SAI",
                        "outro": hex_para_base58(v["contract_address"]), "valor": int(v.get("call_value", 0))})
    return evs


def ligacoes_de_abastecimento(por_endereco: dict[str, list[dict]]) -> tuple[dict, list]:
    """Origens de TRX comuns a mais de um endereço e abastecimentos entre os próprios endereços."""
    origens: dict[str, set] = {}
    internos = []
    for end, evs in por_endereco.items():
        for e in evs:
            if e["tipo"] == "TRX" and e["sentido"] == "ENTRA" and e["ok"]:
                origens.setdefault(e["outro"], set()).add(end)
                if e["outro"] in por_endereco:
                    internos.append((e["outro"], end, e["valor"], e["hora"], e["hash"]))
    comuns = {o: sorted(d) for o, d in origens.items() if len(d) > 1}
    return comuns, internos

# ---------------------------------------------------------------- comandos


def p_endereco(a: str) -> str:
    return base58_para_hex(a)[2:].rjust(64, "0")


def cmd_tx(t: Tron, reg: Registro, a) -> None:
    tx, info = t.transacao(a.hash)
    if not tx:
        reg.dizer("transação não encontrada")
        return
    c = tx["raw_data"]["contract"][0]
    v = c["parameter"]["value"]
    reg.dizer(f"transação   {a.hash}")
    reg.dizer(f"bloco       {info.get('blockNumber')}  {hora_utc(info['blockTimeStamp']) if 'blockTimeStamp' in info else '?'}")
    reg.dizer(f"tipo        {c['type']}")
    perm = c.get("Permission_id", 0)
    tipo_perm = "dono" if perm == 0 else "não é a de dono: conferir as permissões da conta"
    reg.dizer(f"conta       {v.get('owner_address')}  (permissão {perm}, {tipo_perm}; {len(tx.get('signature', []))} assinatura(s))")
    reg.dizer(f"resultado   {tx.get('ret', [{}])[0].get('contractRet')}")
    if c["type"] == "TriggerSmartContract":
        reg.dizer(f"contrato    {v['contract_address']}")
        d = decodificar_chamada(v.get("data", ""))
        if d["funcao"]:
            args = ", ".join(valor_usdt(x) if isinstance(x, int) else x for x in d["argumentos"])
            reg.dizer(f"chamada     {d['funcao']}({args})")
        else:
            reg.dizer(f"chamada     seletor {d['seletor']} (não está na tabela)")
    elif c["type"] == "TransferContract":
        reg.dizer(f"envio de TRX {v['amount'] / 1e6:,.6f} para {v['to_address']}")
    for log in info.get("log", []):
        topicos = log.get("topics", [])
        nome = EVENTOS.get(topicos[0]) if topicos else None
        if nome and len(topicos) >= 3:
            de, para = palavra_para_endereco(topicos[1]), palavra_para_endereco(topicos[2])
            valor = int(log.get("data", "0") or "0", 16)
            emissor = hex_para_base58("41" + log["address"])
            reg.dizer(f"evento      {nome}  {de} -> {para}  {valor_usdt(valor)}  (contrato {emissor})")


def classificar(x: dict, end: str) -> tuple[str, str]:
    """Sentido de um item da lista TRC-20 em relação a `end` e a outra ponta.

    A lista do TronGrid mistura eventos Transfer e Approval. Uma autorização não move
    saldo: é marcada AUTORIZA (o "to" é quem passou a poder gastar) e não é seguida.
    """
    if x.get("type") == "Approval":
        return ("AUTORIZA" if x["from"] == end else "AUTORIZADO"), (x["to"] if x["from"] == end else x["from"])
    if x["from"] == end:
        return "SAI", x["to"]
    return "ENTRA", x["from"]


def cmd_transferencias(t: Tron, reg: Registro, a) -> None:
    itens = t.transferencias(a.endereco, iso_para_ms(a.desde) if a.desde else None,
                             iso_para_ms(a.ate) if a.ate else None)
    reg.dizer(f"{len(itens)} movimento(s) de USDT de/para {a.endereco} (transferências e autorizações)")
    for x in itens:
        sentido, outro = classificar(x, a.endereco)
        reg.dizer(f"{hora_utc(x['block_timestamp'])}  {sentido:10}  {valor_usdt(int(x['value'])):>20}  {outro}  {x['transaction_id']}")
    if any(x.get("type") == "Approval" for x in itens):
        reg.dizer("AUTORIZA = autorização de gasto (não move saldo). Conferir o valor vigente com o comando allowance.")


def cmd_estado(t: Tron, reg: Registro, a) -> None:
    reg.dizer(f"{'endereço':36} {'bloqueado pela emissora':>24} {'saldo USDT':>22}")
    for e in a.enderecos:
        bl = t.constante("isBlackListed(address)", p_endereco(e), "isBlackListed")
        sal = t.constante("balanceOf(address)", p_endereco(e), "balanceOf")
        reg.dizer(f"{e:36} {'SIM' if bl else 'não':>24} {valor_usdt(sal):>22}")


def cmd_allowance(t: Tron, reg: Registro, a) -> None:
    v = t.constante("allowance(address,address)", p_endereco(a.dono) + p_endereco(a.gastador), "allowance")
    reg.dizer(f"autorização de {a.dono} para {a.gastador}: {valor_usdt(v)} USDT")
    if v:
        reg.dizer("ATENÇÃO: autorização ativa; qualquer USDT que entrar nesse endereço pode ser retirado pelo gastador.")


def cmd_seguir(t: Tron, reg: Registro, a) -> None:
    """Segue as saídas de USDT a partir de um endereço e de uma hora, salto a salto.

    Para em endereços com muito movimento (provável carteira de serviço, como corretora),
    porque dali em diante os valores se misturam com os de terceiros.
    """
    ignorar = set(a.ignorar or [])
    fila = [(a.endereco, iso_para_ms(a.desde), 0)]
    vistos = set()
    while fila:
        end, desde, nivel = fila.pop(0)
        if end in vistos or nivel > a.saltos:
            continue
        vistos.add(end)
        itens = t.transferencias(end, desde, None, limite=a.limite)
        if len(itens) >= a.limite:
            reg.dizer(f"{'  ' * nivel}{end}: {len(itens)}+ movimentos desde a hora pedida -> provável carteira de serviço; parar aqui")
            continue
        for x in itens:
            if x.get("type") == "Approval" and x["from"] == end:
                reg.dizer(f"{'  ' * nivel}{end}: autorizou {x['to']} a gastar {valor_usdt(int(x['value']))} em {hora_utc(x['block_timestamp'])} (não é saída; não seguido)")
        saidas = [x for x in itens if x.get("type", "Transfer") == "Transfer" and x["from"] == end and x["to"] not in ignorar]
        reg.dizer(f"{'  ' * nivel}{end}: {len(saidas)} saída(s)")
        for x in saidas:
            reg.dizer(f"{'  ' * (nivel + 1)}{hora_utc(x['block_timestamp'])}  {valor_usdt(int(x['value'])):>18} -> {x['to']}  {x['transaction_id'][:16]}…")
            fila.append((x["to"], x["block_timestamp"], nivel + 1))


def cmd_abastecimento(t: Tron, reg: Registro, a) -> None:
    """Quem pagou o TRX (gás) de cada endereço e quem implantou contratos.

    Separa "carteira de serviço" de "mesmo operador": se o destino final abastece com TRX os
    endereços que lhe repassam valores, ou se vários endereços do caminho têm a mesma origem
    de TRX, a cadeia é coordenada por um só grupo, e não um serviço de terceiros.
    """
    desde = iso_para_ms(a.desde) if a.desde else None
    ate = iso_para_ms(a.ate) if a.ate else None
    por_end = {}
    for end in a.enderecos:
        evs = eventos_trx(t.transacoes_conta(end, desde, ate), end)
        por_end[end] = evs
        reg.dizer(f"\n{end}: {len(evs)} transação(ões) fora de USDT recebido")
        for e in evs:
            falha = "" if e["ok"] else "  [FALHOU]"
            if e["tipo"] == "TRX":
                reg.dizer(f"  {hora_utc(e['hora'])}  TRX {e['sentido']:5} {e['valor'] / 10**6:>14,.6f}  {e['outro']}  {e['hash']}{falha}")
            elif e["tipo"] == "TRC10":
                reg.dizer(f"  {hora_utc(e['hora'])}  TRC-10 {e['sentido']:5} token {e['token']} de/para {e['outro']} (token TRC-10, não é USDT)  {e['hash'][:16]}…")
            elif e["tipo"] == "CRIA_CONTRATO":
                _, info = t.transacao(e["hash"])
                novo = info.get("contract_address")
                reg.dizer(f"  {hora_utc(e['hora'])}  IMPLANTA CONTRATO {hex_para_base58(novo) if novo else '?'}  {e['hash']}{falha}")
            else:
                reg.dizer(f"  {hora_utc(e['hora'])}  chamada ao contrato {e['outro']}  {e['hash'][:16]}…{falha}")
    comuns, internos = ligacoes_de_abastecimento(por_end)
    reg.dizer("\n# Ligações por TRX")
    if internos:
        reg.dizer("Abastecimentos entre os endereços consultados:")
        for de, para, v, h, tx in internos:
            reg.dizer(f"  {hora_utc(h)}  {de} -> {para}  {v / 10**6:,.6f} TRX  {tx[:16]}…")
    if comuns:
        reg.dizer("Mesma origem de TRX para mais de um endereço consultado:")
        for o, ds in comuns.items():
            reg.dizer(f"  {o} abasteceu {len(ds)}: {', '.join(ds)}")
    if not internos and not comuns:
        reg.dizer("Nenhuma ligação por TRX entre os endereços consultados.")
    else:
        reg.dizer("Indício (inferência, não identificação): endereços ligados por TRX tendem a ser do mesmo controlador.")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--rede", choices=REDES, default="mainnet")
    ap.add_argument("--sem-registro", action="store_true")
    ap.add_argument("--pasta", default=str(pathlib.Path(__file__).parent / "execucoes"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("tx"); s.add_argument("hash")
    s = sub.add_parser("transferencias"); s.add_argument("endereco"); s.add_argument("--desde"); s.add_argument("--ate")
    s = sub.add_parser("estado"); s.add_argument("enderecos", nargs="+")
    s = sub.add_parser("allowance"); s.add_argument("dono"); s.add_argument("gastador")
    s = sub.add_parser("seguir"); s.add_argument("endereco"); s.add_argument("--desde", required=True)
    s.add_argument("--saltos", type=int, default=4); s.add_argument("--limite", type=int, default=400)
    s.add_argument("--ignorar", nargs="*", help="endereços a não seguir (ex.: cobrança de taxa de serviço)")
    s = sub.add_parser("abastecimento", help="quem pagou o TRX de cada endereço; ligações entre eles")
    s.add_argument("enderecos", nargs="+"); s.add_argument("--desde"); s.add_argument("--ate")
    a = ap.parse_args(argv)

    reg = Registro(None if a.sem_registro else pathlib.Path(a.pasta), a.cmd)
    t = Tron(a.rede, reg)
    reg.dizer(f"# rede {a.rede} · consulta em {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    {"tx": cmd_tx, "transferencias": cmd_transferencias, "estado": cmd_estado,
     "allowance": cmd_allowance, "seguir": cmd_seguir, "abastecimento": cmd_abastecimento}[a.cmd](t, reg, a)
    reg.fechar(["rastreio.py"] + argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
