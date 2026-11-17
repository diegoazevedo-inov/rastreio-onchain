#!/usr/bin/env python3
"""Gera as carteiras de teste do exemplo sintético (rede Nile) e grava as chaves em .env.

- As chaves privadas vão só para exemplo-sintetico/.env (permissão 600, fora do git).
- Os endereços públicos vão para exemplo-sintetico/carteiras.json (versionado).
- Não sobrescreve um .env existente: as carteiras de um exemplo são geradas uma única vez.

Uso: python3 carteiras.py   (com as dependências de requirements.txt instaladas)
"""
import json
import os
import pathlib
import sys

from tronpy.keys import PrivateKey

AQUI = pathlib.Path(__file__).parent
PAPEIS = [
    ("banco", "recebe TRX e USDT de teste da torneira e abastece os demais"),
    ("vitima", "assina a autorização no 'site falso'"),
    ("operador", "implanta o contrato drenador e chama charge"),
    ("intermediaria1", "recebe o 1º lote do operador e repassa"),
    ("intermediaria2", "recebe o 2º lote do operador e repassa"),
    ("intermediaria3", "recebe o 3º lote do operador e repassa"),
    ("deposito1", "endereço de depósito: repassa tudo à carteira de serviço"),
    ("deposito2", "endereço de depósito: repassa tudo à carteira de serviço"),
    ("deposito3", "endereço de depósito: repassa tudo à carteira de serviço"),
    ("servico", "concentra os valores (simula a carteira operacional de um serviço centralizado)"),
    ("taxa", "recebe uma taxa fixa a cada salto (deve ser excluída do rastreio)"),
]


def main() -> int:
    env = AQUI / ".env"
    if env.exists():
        print(f"{env} já existe; nada foi gerado.", file=sys.stderr)
        return 1
    linhas, publico = ["# Chaves de TESTE (rede Nile). Nunca usar em rede principal. Fora do git."], {}
    for papel, funcao in PAPEIS:
        k = PrivateKey.random()
        linhas.append(f"{papel.upper()}_CHAVE={k.hex()}")
        publico[papel] = {"endereco": k.public_key.to_base58check_address(), "funcao": funcao}
    fd = os.open(env, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write("\n".join(linhas) + "\n")
    (AQUI / "carteiras.json").write_text(json.dumps({"rede": "nile", "carteiras": publico}, ensure_ascii=False, indent=2) + "\n")
    for papel, d in publico.items():
        print(f"{papel:15} {d['endereco']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
