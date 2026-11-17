"""Testes offline do rastreio.py (sem rede). Rodar: python3 -m unittest -v teste_rastreio

Além das funções isoladas, `Reexecucao` refaz cada consulta guardada em
exemplo-sintetico/execucoes/ a partir das respostas brutas gravadas e exige a mesma saída.
"""
import contextlib
import hashlib
import io
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

import rastreio as r

USDT_B58 = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


class Enderecos(unittest.TestCase):
    def test_ida_e_volta(self):
        h = r.base58_para_hex(USDT_B58)
        self.assertEqual(len(h), 42)
        self.assertTrue(h.startswith("41"))
        self.assertEqual(r.hex_para_base58(h), USDT_B58)

    def test_aceita_20_bytes_sem_prefixo(self):
        h = r.base58_para_hex(USDT_B58)
        self.assertEqual(r.hex_para_base58(h[2:]), USDT_B58)

    def test_checksum_invalido_e_recusado(self):
        adulterado = USDT_B58[:-1] + ("u" if USDT_B58[-1] != "u" else "v")
        with self.assertRaises(ValueError):
            r.base58_para_hex(adulterado)

    def test_palavra_abi(self):
        h = r.base58_para_hex(USDT_B58)[2:]
        self.assertEqual(r.palavra_para_endereco(h.rjust(64, "0")), USDT_B58)


class Chamadas(unittest.TestCase):
    def _data(self, seletor, *args):
        partes = []
        for a in args:
            if isinstance(a, str):
                partes.append(r.base58_para_hex(a)[2:].rjust(64, "0"))
            else:
                partes.append(format(a, "064x"))
        return seletor + "".join(partes)

    def test_increase_approval(self):
        dez_milhoes = 10_000_000 * 10**6
        d = r.decodificar_chamada(self._data("d73dd623", USDT_B58, dez_milhoes))
        self.assertEqual(d["funcao"], "increaseApproval")
        self.assertEqual(d["argumentos"], [USDT_B58, dez_milhoes])

    def test_transfer_from(self):
        d = r.decodificar_chamada(self._data("23b872dd", USDT_B58, USDT_B58, 5))
        self.assertEqual(d["funcao"], "transferFrom")
        self.assertEqual(d["argumentos"][2], 5)

    def test_seletor_desconhecido(self):
        d = r.decodificar_chamada("deadbeef" + "0" * 64)
        self.assertIsNone(d["funcao"])
        self.assertEqual(d["seletor"], "deadbeef")


class Classificacao(unittest.TestCase):
    A, B = USDT_B58, "TEhWiZDs4aYvvG5bRQBfqjKPyzwepmQ2RR"

    def test_autorizacao_nao_e_saida(self):
        x = {"type": "Approval", "from": self.A, "to": self.B}
        self.assertEqual(r.classificar(x, self.A), ("AUTORIZA", self.B))

    def test_transferencia(self):
        x = {"type": "Transfer", "from": self.A, "to": self.B}
        self.assertEqual(r.classificar(x, self.A), ("SAI", self.B))
        self.assertEqual(r.classificar(x, self.B), ("ENTRA", self.A))

    def test_autorizado_aponta_quem_autorizou(self):
        x = {"type": "Approval", "from": self.B, "to": self.A}
        self.assertEqual(r.classificar(x, self.A), ("AUTORIZADO", self.B))


class Abastecimento(unittest.TestCase):
    A, B, C = USDT_B58, "TEhWiZDs4aYvvG5bRQBfqjKPyzwepmQ2RR", "TXXj87UjQReAAvu49t1N3Gs9NuXFSgQ8np"

    def _trx(self, de, para, valor, hora, h="aa"):
        return {"txID": h, "block_timestamp": hora, "ret": [{"contractRet": "SUCCESS"}],
                "raw_data": {"contract": [{"type": "TransferContract", "parameter": {"value": {
                    "owner_address": r.base58_para_hex(de), "to_address": r.base58_para_hex(para), "amount": valor}}}]}}

    def test_evento_trx_sentido(self):
        evs = r.eventos_trx([self._trx(self.B, self.A, 5_000_000, 1)], self.A)
        self.assertEqual((evs[0]["tipo"], evs[0]["sentido"], evs[0]["outro"], evs[0]["valor"]), ("TRX", "ENTRA", self.B, 5_000_000))

    def test_origem_comum_e_abastecimento_interno(self):
        por = {self.A: r.eventos_trx([self._trx(self.B, self.A, 1, 1)], self.A),
               self.C: r.eventos_trx([self._trx(self.B, self.C, 1, 2), self._trx(self.A, self.C, 1, 3)], self.C)}
        comuns, internos = r.ligacoes_de_abastecimento(por)
        self.assertEqual(comuns, {self.B: sorted([self.A, self.C])})
        self.assertEqual([(i[0], i[1]) for i in internos], [(self.A, self.C)])

    def test_sem_ligacao(self):
        por = {self.A: [], self.C: r.eventos_trx([self._trx(self.B, self.C, 1, 1)], self.C)}
        self.assertEqual(r.ligacoes_de_abastecimento(por), ({}, []))


class AbastecimentoFalho(unittest.TestCase):
    def test_trx_que_falhou_nao_conta(self):
        a, b = USDT_B58, "TEhWiZDs4aYvvG5bRQBfqjKPyzwepmQ2RR"
        tx = {"txID": "aa", "block_timestamp": 1, "ret": [{"contractRet": "REVERT"}],
              "raw_data": {"contract": [{"type": "TransferContract", "parameter": {"value": {
                  "owner_address": r.base58_para_hex(b), "to_address": r.base58_para_hex(a), "amount": 1}}}]}}
        evs = r.eventos_trx([tx], a)
        self.assertFalse(evs[0]["ok"])
        self.assertEqual(r.ligacoes_de_abastecimento({a: evs, b: []}), ({}, []))


# ---------------------------------------------------------------- keccak-256 independente
# Implementação mínima (Keccak-f[1600], padding 0x01) só para conferir, por fora, a tabela
# de seletores e de tópicos do rastreio.py. hashlib.sha3_256 usa outro padding e não serve.

_RC = [0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
       0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
       0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
       0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
       0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
       0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008]
_ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
_M = (1 << 64) - 1


def _rol(v, n):
    return ((v << n) | (v >> (64 - n))) & _M if n else v


def keccak256(dados: bytes) -> bytes:
    taxa = 136
    p = bytearray(dados) + b"\x01"
    p += b"\x00" * (-len(p) % taxa)
    p[-1] |= 0x80
    A = [[0] * 5 for _ in range(5)]
    for i in range(0, len(p), taxa):
        bloco = p[i:i + taxa]
        for j in range(taxa // 8):
            A[j % 5][j // 5] ^= int.from_bytes(bloco[8 * j:8 * j + 8], "little")
        for rc in _RC:
            C = [A[x][0] ^ A[x][1] ^ A[x][2] ^ A[x][3] ^ A[x][4] for x in range(5)]
            D = [C[(x - 1) % 5] ^ _rol(C[(x + 1) % 5], 1) for x in range(5)]
            A = [[A[x][y] ^ D[x] for y in range(5)] for x in range(5)]
            B = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    B[y][(2 * x + 3 * y) % 5] = _rol(A[x][y], _ROT[x][y])
            A = [[B[x][y] ^ (~B[(x + 1) % 5][y] & B[(x + 2) % 5][y]) for y in range(5)] for x in range(5)]
            A[0][0] ^= rc
    return b"".join(A[j % 5][j // 5].to_bytes(8, "little") for j in range(4))


class TabelasConferidasPorFora(unittest.TestCase):
    def test_vetor_conhecido(self):
        self.assertEqual(keccak256(b"").hex(), "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470")

    def test_seletores(self):
        for sel, (nome, tipos) in r.SELETORES.items():
            with self.subTest(nome=nome):
                self.assertEqual(keccak256(f"{nome}({','.join(tipos)})".encode())[:4].hex(), sel)

    def test_topicos_de_evento(self):
        for topico, nome in r.EVENTOS.items():
            with self.subTest(nome=nome):
                self.assertEqual(keccak256(f"{nome}(address,address,uint256)".encode()).hex(), topico)


# ---------------------------------------------------------------- registro e manifesto

class Manifesto(unittest.TestCase):
    def test_manifesto_cobre_respostas_saida_e_comando(self):
        with tempfile.TemporaryDirectory() as d:
            reg = r.Registro(pathlib.Path(d), "teste")
            reg.resposta("x", "https://exemplo", None, {"ok": 1})
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                reg.dizer("linha")
                reg.fechar(["rastreio.py", "teste"])
            linhas = (reg.dir / "MANIFEST.sha256").read_text().split("\n")
            mapa = {l.split("  ", 1)[1]: l.split("  ", 1)[0] for l in linhas if l}
            self.assertEqual(set(mapa), {"respostas/001-x.json", "saida.txt", "comando.txt"})
            for nome, h in mapa.items():
                self.assertEqual(hashlib.sha256((reg.dir / nome).read_bytes()).hexdigest(), h)


class Python310(unittest.TestCase):
    def test_roda_sem_datetime_utc(self):
        """datetime.UTC só existe a partir do 3.11; o script declara 3.10+."""
        codigo = (
            "import datetime, sys; del datetime.UTC; sys.path.insert(0, sys.argv[1]); import rastreio as r\n"
            "r.Tron._req = lambda self, *a, **k: {'constant_result': ['0' * 64]}\n"
            "r.hora_utc(0); r.iso_para_ms('2026-01-01T00:00:00')\n"
            "sys.exit(r.main(['--rede', 'nile', '--sem-registro', 'allowance', sys.argv[2], sys.argv[2]]))\n")
        p = subprocess.run([sys.executable, "-c", codigo, str(pathlib.Path(__file__).parent), USDT_B58],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)


# ---------------------------------------------------------------- reexecução das consultas guardadas

EXECUCOES = pathlib.Path(__file__).parent / "exemplo-sintetico" / "execucoes"
# Linhas cujo texto mudou depois que as consultas foram gravadas (mesmo dado, outro rótulo).
RENOMEADAS = [
    (re.compile(r"^assinada por (\S+)  \((\d+) assinatura\(s\)\)$"), r"conta       \1  (permissão 0, dono; \2 assinatura(s))"),
    (re.compile(r"\(costuma ser divulgação em massa\)"), "(token TRC-10, não é USDT)"),
]


def _chave(url, corpo):
    return url, json.dumps(corpo, sort_keys=True)


def reexecutar(pasta: pathlib.Path, argv_extra=None, substituir=None) -> str:
    respostas = {}
    for f in sorted((pasta / "respostas").glob("*.json")):
        d = json.loads(f.read_text())
        respostas[_chave(d["url"], d["corpo"])] = d["resposta"]
    argv = (pasta / "comando.txt").read_text().split()[1:]
    if "--pasta" in argv:
        i = argv.index("--pasta"); del argv[i:i + 2]
    argv = ["--sem-registro"] + (substituir(argv) if substituir else argv) + (argv_extra or [])

    def _req(self, rotulo, caminho, corpo=None):
        return respostas[_chave(self.api + caminho, corpo)]

    original = r.Tron._req
    r.Tron._req = _req
    try:
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            r.main(argv)
    finally:
        r.Tron._req = original
    return saida.getvalue()


def _corpo(texto):
    return [l for l in texto.rstrip("\n").split("\n")[1:]]  # sem a linha do carimbo de hora


class Reexecucao(unittest.TestCase):
    def test_cada_consulta_guardada_reproduz_a_saida(self):
        pastas = sorted(p for p in EXECUCOES.iterdir() if (p / "comando.txt").exists())
        self.assertGreaterEqual(len(pastas), 13)
        for pasta in pastas:
            with self.subTest(pasta=pasta.name):
                esperado = _corpo((pasta / "saida.txt").read_text())
                for padrao, novo in RENOMEADAS:
                    esperado = [padrao.sub(novo, l) for l in esperado]
                self.assertEqual(_corpo(reexecutar(pasta)), esperado)

    def test_seguir_para_em_endereco_com_muito_movimento(self):
        pasta = next(p for p in sorted(EXECUCOES.iterdir()) if p.name.endswith("-seguir"))
        saida = reexecutar(pasta, ["--limite", "3"])
        self.assertIn("provável carteira de serviço", saida)
        self.assertNotIn("saída(s)", saida)


# ---------------------------------------------------------------- casos que o exemplo não tem
# Respostas sintéticas para ramos que as consultas guardadas não exercitam: endereço
# bloqueado, permissão que não é a de dono, várias assinaturas, paginação e limite de saltos.

def rodar_com(respostas_por_req, argv) -> str:
    original = r.Tron._req
    r.Tron._req = lambda self, rotulo, caminho, corpo=None: respostas_por_req(caminho, corpo)
    try:
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            r.main(["--rede", "nile", "--sem-registro"] + argv)
    finally:
        r.Tron._req = original
    return saida.getvalue()


A_, B_, C_, D_ = (USDT_B58, "TEhWiZDs4aYvvG5bRQBfqjKPyzwepmQ2RR",
                  "TXXj87UjQReAAvu49t1N3Gs9NuXFSgQ8np", "TQ5CUe1QqQmRvd7Vx8gTCdCnu5nAFH1twE")


def _transf(de, para, valor, hora, h):
    return {"transaction_id": h, "block_timestamp": hora, "from": de, "to": para, "type": "Transfer", "value": str(valor)}


class CasosSinteticos(unittest.TestCase):
    def test_estado_mostra_bloqueio(self):
        def resp(caminho, corpo):
            if corpo["function_selector"] == "isBlackListed(address)":
                return {"constant_result": ["0" * 63 + "1"]}
            return {"constant_result": [format(5_000_000, "064x")]}
        saida = rodar_com(resp, ["estado", C_])
        self.assertRegex(saida, rf"{C_}\s+SIM\s+5,000000")

    def test_tx_com_permissao_que_nao_e_de_dono_e_duas_assinaturas(self):
        def resp(caminho, corpo):
            if caminho.endswith("gettransactionbyid"):
                return {"ret": [{"contractRet": "SUCCESS"}], "signature": ["aa", "bb"],
                        "raw_data": {"contract": [{"type": "TransferContract", "Permission_id": 2,
                                                   "parameter": {"value": {"owner_address": C_, "to_address": D_, "amount": 1_000_000}}}]}}
            return {"blockNumber": 1, "blockTimeStamp": 0}
        saida = rodar_com(resp, ["tx", "00" * 32])
        self.assertIn("permissão 2, não é a de dono", saida)
        self.assertIn("2 assinatura(s)", saida)

    def test_transferencias_le_todas_as_paginas(self):
        def resp(caminho, corpo):
            if "fingerprint=" in caminho:
                return {"data": [_transf(C_, D_, 2, 2000, "bb")], "meta": {}}
            return {"data": [_transf(B_, C_, 1, 1000, "aa")], "meta": {"fingerprint": "pagina2"}}
        saida = rodar_com(resp, ["transferencias", C_])
        self.assertIn("2 movimento(s)", saida)

    def test_seguir_respeita_o_limite_de_saltos(self):
        cadeia = {A_: _transf(A_, B_, 3, 1000, "a1"), B_: _transf(B_, C_, 3, 2000, "b1"), C_: _transf(C_, D_, 3, 3000, "c1")}
        def resp(caminho, corpo):
            end = caminho.split("/v1/accounts/")[1].split("/")[0]
            return {"data": [cadeia[end]] if end in cadeia else [], "meta": {}}
        saida = rodar_com(resp, ["seguir", A_, "--desde", "1970-01-01T00:00:00", "--saltos", "1"])
        self.assertIn(f"{B_}: 1 saída(s)", saida)
        self.assertNotIn(f"{C_}: 1 saída(s)", saida)

    def test_falha_por_energia_nao_conta_como_sucesso(self):
        tx = {"txID": "aa", "block_timestamp": 1, "ret": [{"contractRet": "OUT_OF_ENERGY"}],
              "raw_data": {"contract": [{"type": "TransferContract", "parameter": {"value": {
                  "owner_address": r.base58_para_hex(B_), "to_address": r.base58_para_hex(A_), "amount": 1}}}]}}
        self.assertFalse(r.eventos_trx([tx], A_)[0]["ok"])


class Formatos(unittest.TestCase):
    def test_valor_usdt_formato_brasileiro(self):
        self.assertEqual(r.valor_usdt(1_234_567_890_123), "1.234.567,890123")

    def test_iso_sem_fuso_e_utc(self):
        self.assertEqual(r.iso_para_ms("1970-01-01T00:00:01"), 1000)


if __name__ == "__main__":
    unittest.main()
