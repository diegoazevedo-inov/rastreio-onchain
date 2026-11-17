#!/usr/bin/env python3
"""Planta defeitos conhecidos, um de cada vez, e exige que a verificação correspondente falhe.

Mede se os testes e o conferir.py pegam o que deveriam pegar. Os defeitos vêm das auditorias
do repositório (M, N e R); medem esses casos, não a cobertura em geral. Cada defeito é aplicado a uma
cópia temporária; o repositório não é alterado. Sai com código 1 se algum defeito passar.

Uso: python3 auditoria/defeitos_plantados.py
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# (id, descrição, arquivo, trecho original, trecho com defeito)
RASTREIO = [
    ("M1", "seguir volta a tratar Approval como saída", "rastreio.py",
     'x.get("type", "Transfer") == "Transfer" and x["from"] == end', 'x["from"] == end'),
    ("M2", "seguir ignora --ignorar", "rastreio.py",
     'and x["to"] not in ignorar]', ']'),
    ("M3", "estado inverte SIM/não do bloqueio", "rastreio.py",
     "'SIM' if bl else 'não'", "'não' if bl else 'SIM'"),
    ("M4", "manifesto deixa de cobrir respostas/", "rastreio.py",
     'if p.is_file() and p.name != "MANIFEST.sha256":', 'if p.is_file() and p.name != "MANIFEST.sha256" and "respostas" not in p.parts:'),
    ("M5", "TRX que falhou conta como abastecimento", "rastreio.py",
     'e["sentido"] == "ENTRA" and e["ok"]:', 'e["sentido"] == "ENTRA":'),
    ("M6", "seguir nunca para em carteira de serviço", "rastreio.py",
     "if len(itens) >= a.limite:", "if False:"),
    ("M7", "classificar devolve a ponta errada para AUTORIZADO", "rastreio.py",
     '(x["to"] if x["from"] == end else x["from"])', 'x["to"]'),
    ("M8", "allowance com dono e gastador trocados", "rastreio.py",
     "p_endereco(a.dono) + p_endereco(a.gastador)", "p_endereco(a.gastador) + p_endereco(a.dono)"),
    ("M9", "tx zera o valor dos eventos", "rastreio.py",
     'valor = int(log.get("data", "0") or "0", 16)', "valor = 0"),
    ("M10", "volta a exigir Python 3.11 (datetime.UTC)", "rastreio.py",
     "def hora_utc(ms: int) -> str:\n    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc)",
     "def hora_utc(ms: int) -> str:\n    return dt.datetime.fromtimestamp(ms / 1000, dt.UTC)"),
    ("N1", "estado sempre diz que não há bloqueio", "rastreio.py",
     "'SIM' if bl else 'não'", "'não'"),
    ("N2", "tx rotula qualquer permissão como de dono", "rastreio.py",
     'tipo_perm = "dono" if perm == 0 else', 'tipo_perm = "dono" if True else'),
    ("N3", "tx ignora Permission_id", "rastreio.py",
     'perm = c.get("Permission_id", 0)', "perm = 0"),
    ("N4", "seguir com erro de um no limite de saltos", "rastreio.py",
     "nivel > a.saltos:", "nivel >= a.saltos:"),
    ("N6", "transferencias lê só a primeira página", "rastreio.py",
     'f"/v1/accounts/{end}/transactions/trc20?" + urllib.parse.urlencode(q))\n            itens += r.get("data", [])\n            fingerprint = r.get("meta", {}).get("fingerprint")',
     'f"/v1/accounts/{end}/transactions/trc20?" + urllib.parse.urlencode(q))\n            itens += r.get("data", [])\n            fingerprint = None'),
    ("N9", "falha que não seja REVERT conta como sucesso", "rastreio.py",
     '.get("contractRet", "SUCCESS") == "SUCCESS"', '.get("contractRet", "SUCCESS") != "REVERT"'),
    ("N12", "contagem de assinaturas fixa em 1", "rastreio.py",
     "{len(tx.get('signature', []))} assinatura(s)", "1 assinatura(s)"),
]
RELATORIO = "exemplo-sintetico/relatorio-exemplo.md"
CONFERIR = [
    ("R1", "saldo final 997 → 897", RELATORIO, "| destino `TEcWfh…B2f21X` | não | 997 |", "| destino `TEcWfh…B2f21X` | não | 897 |"),
    ("R2", "destino marcado como bloqueado", RELATORIO, "| destino `TEcWfh…B2f21X` | não | 997 |", "| destino `TEcWfh…B2f21X` | sim | 997 |"),
    ("R3", "lote 1 de 410 → 140", RELATORIO, "| 410 | `e313a2ce…` |", "| 140 | `e313a2ce…` |"),
    ("R4", "hash da perda atribuído ao lote 2", RELATORIO, "| 340 | `fe3a96b2…` |", "| 340 | `40d6399f…` |"),
    ("R5", "endereço abreviado inexistente", RELATORIO, "| 23:25:09 | operador | `TUDB9j…3pHn` |", "| 23:25:09 | operador | `TUDB9j…3pHX` |"),
]


def rodar(copia: pathlib.Path, verificacao: str) -> bool:
    """True se a verificação passou."""
    cmd = ([sys.executable, "-m", "unittest", "-q", "teste_rastreio"] if verificacao == "testes"
           else [sys.executable, "exemplo-sintetico/conferir.py"])
    return subprocess.run(cmd, cwd=copia, capture_output=True).returncode == 0


def main() -> int:
    falhas = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = pathlib.Path(tmp) / "repo"
        shutil.copytree(RAIZ, base, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".env"))
        for verificacao, defeitos in (("testes", RASTREIO), ("conferir", CONFERIR)):
            if not rodar(base, verificacao):
                print(f"ERRO: {verificacao} já falha sem defeito plantado"); return 1
            for ident, desc, arq, antes, depois in defeitos:
                alvo = base / arq
                texto = alvo.read_text()
                if texto.count(antes) != 1:
                    print(f"{ident}  trecho não encontrado exatamente uma vez em {arq}: ajustar o script"); falhas += 1; continue
                alvo.write_text(texto.replace(antes, depois))
                pegou = not rodar(base, verificacao)
                alvo.write_text(texto)
                print(f"{ident:4} {'pegou' if pegou else 'NÃO PEGOU'}  ({verificacao}) {desc}")
                falhas += not pegou
    print("PASSA" if not falhas else f"NÃO PASSA: {falhas} defeito(s) sem detecção")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
