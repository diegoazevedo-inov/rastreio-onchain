#!/usr/bin/env python3
"""Encena na rede de teste Nile o padrão "drenagem por autorização + dispersão".

USO EXCLUSIVO EM REDE DE TESTE. O script recusa qualquer rede que não seja a Nile.

- Lê as chaves de teste de exemplo-sintetico/.env (gerado por carteiras.py).
- Grava cada passo em encenacao.json (hash, hora UTC). É retomável: passos já
  registrados são pulados, então pode ser rodado de novo após uma falha.
- encenacao.json é o "gabarito" do exemplo: o protocolo de rastreio deve
  reconstruir esse caminho sem consultá-lo.

Uso: python3 encenar.py   (com as dependências de requirements.txt instaladas)
"""
import json
import pathlib
import sys
import time
from datetime import datetime, timezone

from tronpy import Tron
from tronpy.contract import Contract
from tronpy.keys import PrivateKey, to_hex_address

REDE = "nile"
USDT = "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"  # USDT de teste da Nile
AQUI = pathlib.Path(__file__).parent
REGISTRO = AQUI / "encenacao.json"
U = 10**6        # 1 USDT (6 casas)
T = 10**6        # 1 TRX em sun
LIMITE_TAXA = 150 * T

chaves = {}
for linha in (AQUI / ".env").read_text().splitlines():
    if "_CHAVE=" in linha:
        papel, valor = linha.split("_CHAVE=", 1)
        chaves[papel.lower()] = PrivateKey(bytes.fromhex(valor.strip()))
end = {p: k.public_key.to_base58check_address() for p, k in chaves.items()}

cli = Tron(network=REDE)
usdt = cli.get_contract(USDT)
reg = json.loads(REGISTRO.read_text()) if REGISTRO.exists() else {"rede": REDE, "contrato_usdt": USDT, "passos": []}
feitos = {p["passo"] for p in reg["passos"]}


def gravar(passo, descricao, txid, extra=None):
    item = {"passo": passo, "descricao": descricao, "txid": txid,
            "hora_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    if extra:
        item.update(extra)
    reg["passos"].append(item)
    REGISTRO.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n")
    feitos.add(passo)
    print(f"ok  {passo:28} {txid}")


def esperar(txn):
    res = txn.broadcast()
    info = res.wait(timeout=90)
    r = info.get("receipt", {}).get("result")
    if r not in (None, "SUCCESS"):
        raise RuntimeError(f"{res.txid}: {r} {info.get('resMessage', '')}")
    time.sleep(2)
    return res.txid, info


def trx(passo, de, para, valor, descricao):
    if passo in feitos:
        return
    txn = cli.trx.transfer(end[de], end[para], valor).build().sign(chaves[de])
    txid, _ = esperar(txn)
    gravar(passo, descricao, txid)


def token(passo, de, para, valor, descricao):
    if passo in feitos:
        return
    txn = (usdt.functions.transfer(end[para], valor).with_owner(end[de])
           .fee_limit(LIMITE_TAXA).build().sign(chaves[de]))
    txid, _ = esperar(txn)
    gravar(passo, descricao, txid)


def saldo(papel):
    return usdt.functions.balanceOf(end[papel])


def drenador():
    for p in reg["passos"]:
        if p["passo"] == "implantar_drenador":
            return p["contrato"]
    art = json.loads((AQUI / "contratos" / "DrenadorTeste.json").read_text())
    arg = to_hex_address(USDT)[2:].rjust(64, "0")
    c = Contract(name="DrenadorTeste", bytecode=art["bytecode"] + arg, abi=art["abi"],
                 user_resource_percent=100, origin_energy_limit=10_000_000)
    txn = (cli.trx.deploy_contract(end["operador"], c).fee_limit(LIMITE_TAXA)
           .build().sign(chaves["operador"]))
    txid, info = esperar(txn)
    endereco = info.get("contract_address") or c.contract_address
    if endereco.startswith("41"):
        from tronpy.keys import to_base58check_address
        endereco = to_base58check_address(endereco)
    gravar("implantar_drenador", "operador implanta o contrato drenador de teste", txid, {"contrato": endereco})
    return endereco


def main():
    if REDE != "nile":
        sys.exit("recusado: só rede de teste")
    # 1. abastecimento (fora da história: equivale ao operador e ao serviço terem TRX)
    trx("abastecer_operador", "banco", "operador", 500 * T, "abastecimento de TRX do operador")
    trx("abastecer_servico", "banco", "servico", 150 * T, "abastecimento de TRX da carteira de serviço")
    # 2. a vítima "compra" USDT
    token("compra_vitima", "banco", "vitima", 1000 * U, "vítima recebe 1.000 USDT (compra)")
    # 3. o operador prepara o drenador e envia TRX à vítima ("aluguel de energia")
    dren = drenador()
    trx("aluguel_energia", "operador", "vitima", 25 * T, "operador envia TRX à vítima para ela conseguir assinar")
    # 4. a vítima assina a autorização no "site falso" (a confirmação biométrica no celular assina isto)
    if "autorizacao" not in feitos:
        txn = (usdt.functions.increaseApproval(dren, 10_000_000 * U).with_owner(end["vitima"])
               .fee_limit(LIMITE_TAXA).build().sign(chaves["vitima"]))
        txid, _ = esperar(txn)
        gravar("autorizacao", "vítima assina increaseApproval(drenador, 10.000.000 USDT)", txid)
    # 5. o operador drena
    if "charge" not in feitos:
        c = cli.get_contract(dren)
        valor = saldo("vitima")
        txn = (c.functions.charge(end["vitima"], valor).with_owner(end["operador"])
               .fee_limit(LIMITE_TAXA).build().sign(chaves["operador"]))
        txid, _ = esperar(txn)
        gravar("charge", f"operador chama charge(vitima, {valor // U} USDT)", txid)
    # 6. dispersão em três lotes
    for i in (1, 2, 3):
        trx(f"abastecer_intermediaria{i}", "operador", f"intermediaria{i}", 40 * T, f"TRX para a intermediária {i}")
    lotes = {1: 410, 2: 340, 3: 250}
    for i, v in lotes.items():
        token(f"lote_intermediaria{i}", "operador", f"intermediaria{i}", v * U, f"lote de {v} USDT para a intermediária {i}")
    # 7. o serviço abastece seus endereços de depósito (como faz uma corretora)
    for i in (1, 2, 3):
        trx(f"abastecer_deposito{i}", "servico", f"deposito{i}", 30 * T, f"TRX para o depósito {i}")
    # 8. cada intermediária paga a taxa, faz um depósito de teste e depois o valor cheio
    for i, v in lotes.items():
        token(f"taxa_intermediaria{i}", f"intermediaria{i}", "taxa", 1 * U, f"taxa fixa de 1 USDT (intermediária {i})")
        token(f"teste_deposito{i}", f"intermediaria{i}", f"deposito{i}", 5 * U, f"depósito de teste de 5 USDT (intermediária {i})")
        token(f"cheio_deposito{i}", f"intermediaria{i}", f"deposito{i}", (v - 6) * U, f"depósito do restante, {v - 6} USDT (intermediária {i})")
    # 9. os depósitos são varridos para a carteira de serviço
    for i in (1, 2, 3):
        if f"varredura_deposito{i}" not in feitos:
            token(f"varredura_deposito{i}", f"deposito{i}", "servico", saldo(f"deposito{i}"), f"varredura do depósito {i} para a carteira de serviço")
    print("\nsaldos finais (USDT):")
    for p in end:
        print(f"  {p:15} {saldo(p) / U:,.6f}")


if __name__ == "__main__":
    main()
