#!/usr/bin/env python3
"""Gera o PDF de um relatório no modelo "afirmação × prova", com as análises anexadas.

Converte o Markdown do relatório (e de cada anexo) para HTML com um estilo de impressão e
imprime com o Chrome ou Chromium em modo headless. Os anexos entram na íntegra, cada um
numa página nova, com um cabeçalho que diz de onde vêm.

O conversor cobre o que os modelos usam: títulos, parágrafos, ênfase, código, links,
citações, listas (inclusive aninhadas e coladas no parágrafo anterior), tabelas, blocos de
código e linhas horizontais. Só biblioteca padrão do Python 3.10+.

Uso:
  python3 relatorio_pdf.py RELATORIO.md --saida RELATORIO.pdf \\
      [--anexo "Análise A" analises/A/PARECER.md ...] [--anexo-autor "Comparação" COMPARACAO.md] [--html-somente]
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------- inline


def _link(m: re.Match) -> str:
    """Link externo vira <a>; caminho relativo vira texto, para o PDF não gravar o local da máquina."""
    texto, url = m[1], m[2]  # já escapados
    if re.match(r"^(https?:|mailto:)", url):
        return f'<a href="{url.replace(chr(34), "&quot;")}">{texto}</a>'
    return f"{texto} ({url})"


def _inline(texto: str) -> str:
    """Escapa HTML e aplica código, negrito, itálico e links, nessa ordem."""
    codigos: list[str] = []

    def guarda(m: re.Match) -> str:  # código sai do caminho antes da ênfase, que pode envolvê-lo
        codigos.append(f"<code>{html.escape(m[1])}</code>")
        return f"\x00{len(codigos) - 1}\x00"

    p = re.sub(r"`([^`]+)`", guarda, texto.replace("\x00", ""))
    p = html.escape(p, quote=False)
    p = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", _link, p)
    p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
    p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", p)
    return re.sub(r"\x00(\d+)\x00", lambda m: codigos[int(m[1])], p)

# ---------------------------------------------------------------- blocos


_ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
_SEPARADOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def _celulas(linha: str) -> list[str]:
    s = linha.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def _lista(linhas: list[str]) -> str:
    """Converte um bloco de itens de lista (com recuo) em <ul>/<ol> aninhados."""
    out: list[str] = []
    pilha: list[tuple[int, str]] = []  # (recuo, tag)
    aberto = False
    for linha in linhas:
        m = _ITEM.match(linha)
        if not m:  # continuação do item anterior
            if out:
                out[-1] = out[-1] + " " + _inline(linha.strip())
            continue
        recuo, marca, conteudo = len(m[1].expandtabs(4)), m[2], m[3]
        tag = "ol" if marca[0].isdigit() else "ul"
        while pilha and recuo < pilha[-1][0]:
            out.append(f"</li></{pilha.pop()[1]}>")
        if not pilha or recuo > pilha[-1][0]:
            if pilha and not aberto:
                out.append("<li>")
            inicio = int(marca[:-1]) if tag == "ol" else 1
            out.append(f'<ol start="{inicio}">' if inicio != 1 else f"<{tag}>")  # preserva a numeração original
            pilha.append((recuo, tag))
        else:
            out.append("</li>")
        out.append(f"<li>{_inline(conteudo)}")
        aberto = True
    while pilha:
        out.append(f"</li></{pilha.pop()[1]}>")
    return "".join(out)


def md_para_html(texto: str) -> str:
    linhas = texto.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    paragrafo: list[str] = []

    def fecha_paragrafo():
        if paragrafo:
            out.append(f"<p>{_inline(' '.join(l.strip() for l in paragrafo))}</p>")
            paragrafo.clear()

    while i < len(linhas):
        linha = linhas[i]
        s = linha.strip()
        if not s:
            fecha_paragrafo(); i += 1; continue
        if s.startswith("```"):
            fecha_paragrafo()
            j = i + 1
            while j < len(linhas) and not linhas[j].strip().startswith("```"):
                j += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(linhas[i + 1:j]))}</code></pre>")
            i = j + 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            fecha_paragrafo()
            n = len(m[1])
            out.append(f"<h{n}>{_inline(m[2])}</h{n}>")
            i += 1; continue
        if re.match(r"^(-{3,}|\*{3,})$", s):
            fecha_paragrafo(); out.append("<hr>"); i += 1; continue
        if s.startswith(">"):
            fecha_paragrafo()
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith(">"):
                bloco.append(re.sub(r"^\s*>\s?", "", linhas[i])); i += 1
            out.append(f"<blockquote>{md_para_html(chr(10).join(bloco))}</blockquote>")
            continue
        if s.startswith("|") and i + 1 < len(linhas) and _SEPARADOR.match(linhas[i + 1]):
            fecha_paragrafo()
            cab = _celulas(linha)
            i += 2
            corpo = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                corpo.append(_celulas(linhas[i])); i += 1
            th = "".join(f"<th>{_inline(c)}</th>" for c in cab)
            trs = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in corpo)
            out.append(f'<div class="tabela"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
            continue
        if _ITEM.match(linha) and not (paragrafo and linha.startswith(" ")):
            fecha_paragrafo()  # lista colada no parágrafo anterior também vira lista
            bloco = []
            while i < len(linhas) and linhas[i].strip() and (
                    _ITEM.match(linhas[i]) or linhas[i].startswith((" ", "\t"))):
                bloco.append(linhas[i]); i += 1
            # linhas em branco entre itens da mesma lista não a quebram
            while i < len(linhas) and not linhas[i].strip() and i + 1 < len(linhas) and _ITEM.match(linhas[i + 1]):
                i += 1
                while i < len(linhas) and linhas[i].strip() and (
                        _ITEM.match(linhas[i]) or linhas[i].startswith((" ", "\t"))):
                    bloco.append(linhas[i]); i += 1
            out.append(_lista(bloco))
            continue
        paragrafo.append(linha)
        i += 1
    fecha_paragrafo()
    return "\n".join(out)

# ---------------------------------------------------------------- documento


ESTILO = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
:root { --tinta: #1f2328; --suave: #57606a; --linha: #d0d7de; --fundo: #f6f8fa; --destaque: #0b5394; }
body { font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif; font-size: 10pt;
       line-height: 1.45; color: var(--tinta); }
h1 { font-size: 18pt; margin: 0 0 8pt; color: var(--destaque); }
h2 { font-size: 13pt; margin: 16pt 0 6pt; border-bottom: 1px solid var(--linha); padding-bottom: 2pt; }
h3 { font-size: 11pt; margin: 12pt 0 4pt; }
p, li { orphans: 3; widows: 3; }
code { font-family: "DejaVu Sans Mono", "Liberation Mono", monospace; font-size: 8.6pt;
       background: var(--fundo); padding: 0 2px; border-radius: 2px; overflow-wrap: anywhere; }
pre { background: var(--fundo); padding: 6pt; overflow-wrap: anywhere; white-space: pre-wrap; }
blockquote { margin: 8pt 0; padding: 4pt 10pt; border-left: 3px solid var(--destaque);
             background: var(--fundo); color: var(--suave); }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; font-size: 8.6pt; }
th, td { border: 1px solid var(--linha); padding: 3pt 4pt; vertical-align: top; text-align: left;
         overflow-wrap: anywhere; }
thead th { background: var(--fundo); }
tr { break-inside: avoid; }
a { color: var(--destaque); text-decoration: none; }
.anexo { break-before: page; }
.anexo-cabecalho { font-size: 9pt; color: var(--suave); border: 1px solid var(--linha);
                   padding: 4pt 8pt; margin-bottom: 10pt; }
"""


def titulo_de(texto: str, padrao: str = "Relatório") -> str:
    m = re.search(r"^#\s+(.+)$", texto, re.M)
    return m[1].strip() if m else padrao


def montar_documento(relatorio: str, anexos: list[tuple]) -> str:
    """HTML completo: relatório e, depois, cada anexo numa página nova.

    Cada anexo é (rótulo, texto) ou (rótulo, texto, entregue). `entregue=False` marca texto do
    próprio autor do relatório (por exemplo, uma comparação), e não material recebido de terceiros.
    """
    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    partes = [md_para_html(relatorio)]
    for n, (rotulo, texto, *resto) in enumerate(anexos):
        nota = ("Texto como entregue; notas editoriais, quando houver, aparecem entre colchetes."
                if (resto[0] if resto else True) else "Texto do autor deste relatório.")
        cab = (f'<div class="anexo-cabecalho"><strong>Anexo {letras[n]}: {html.escape(rotulo)}.</strong> '
               f"{nota}</div>")
        partes.append(f'<section class="anexo">{cab}{md_para_html(texto)}</section>')
    titulo = html.escape(titulo_de(relatorio))
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{titulo}</title>'
            f"<style>{ESTILO}</style></head><body>{''.join(partes)}</body></html>")


def achar_navegador() -> str | None:
    for nome in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        if caminho := shutil.which(nome):
            return caminho
    return None


def imprimir_pdf(html_doc: str, saida: pathlib.Path, navegador: str | None = None) -> None:
    navegador = navegador or achar_navegador()
    if not navegador:
        raise RuntimeError("Chrome ou Chromium não encontrado; use --html-somente e imprima pelo navegador.")
    saida = saida.resolve()
    with tempfile.TemporaryDirectory(dir=saida.parent) as tmp:  # perto da saída: Chromium em snap não lê /tmp
        pagina = pathlib.Path(tmp) / "relatorio.html"
        pagina.write_text(html_doc, encoding="utf-8")
        p = subprocess.run([navegador, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                            f"--user-data-dir={tmp}/perfil", f"--print-to-pdf={saida}", pagina.as_uri()],
                           capture_output=True, text=True, timeout=180)
        if p.returncode != 0 or not saida.exists():
            raise RuntimeError(f"falha ao imprimir: {p.stderr.strip()[-500:]}")


class _Anexo(argparse.Action):
    """--anexo e --anexo-autor vão para a mesma lista, na ordem em que aparecem."""

    def __call__(self, parser, ns, valores, opcao=None):
        lista = list(getattr(ns, self.dest) or [])
        lista.append((valores[0], valores[1], opcao == "--anexo"))
        setattr(ns, self.dest, lista)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("relatorio")
    ap.add_argument("--saida", required=True, help="arquivo .pdf (ou .html, com --html-somente)")
    ap.add_argument("--anexo", nargs=2, action=_Anexo, dest="anexos", default=[], metavar=("ROTULO", "ARQUIVO"),
                    help="material recebido (ex.: parecer de uma análise), anexado como entregue")
    ap.add_argument("--anexo-autor", nargs=2, action=_Anexo, dest="anexos", metavar=("ROTULO", "ARQUIVO"),
                    help="texto do próprio autor do relatório (ex.: comparação das análises)")
    ap.add_argument("--html-somente", action="store_true")
    a = ap.parse_args(argv)
    rel = pathlib.Path(a.relatorio).read_text(encoding="utf-8")
    anexos = [(rot, pathlib.Path(arq).read_text(encoding="utf-8"), entregue) for rot, arq, entregue in a.anexos]
    doc = montar_documento(rel, anexos)
    saida = pathlib.Path(a.saida)
    if a.html_somente:
        saida.write_text(doc, encoding="utf-8")
    else:
        imprimir_pdf(doc, saida)
    print(f"{saida} ({len(anexos)} anexo(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
