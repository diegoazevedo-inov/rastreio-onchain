#!/usr/bin/env python3
"""Compila DrenadorTeste.sol e grava DrenadorTeste.json (ABI + bytecode). Uso exclusivo em rede de teste.

Requer py-solc-x (requirements.txt); baixa o compilador oficial solc 0.8.6 na primeira execução.
Uso: python3 contratos/compilar.py
"""
import json
import pathlib

import solcx

AQUI = pathlib.Path(__file__).parent
VERSAO = "0.8.6"
solcx.install_solc(VERSAO)
fonte = (AQUI / "DrenadorTeste.sol").read_text()
saida = solcx.compile_standard({
    "language": "Solidity",
    "sources": {"DrenadorTeste.sol": {"content": fonte}},
    "settings": {"evmVersion": "istanbul", "optimizer": {"enabled": True, "runs": 200},
                 "outputSelection": {"*": {"*": ["abi", "evm.bytecode.object"]}}},
}, solc_version=VERSAO)
c = saida["contracts"]["DrenadorTeste.sol"]["DrenadorTeste"]
(AQUI / "DrenadorTeste.json").write_text(json.dumps({
    "compilador": f"solc {VERSAO}, evmVersion istanbul, optimizer 200",
    "abi": c["abi"], "bytecode": c["evm"]["bytecode"]["object"]}, indent=2) + "\n")
print(len(c["evm"]["bytecode"]["object"]) // 2, "bytes")
