#!/usr/bin/env python3
"""Extrae texto de un documento (PDF o .docx) para estructurarlo después.

PDF: separa páginas con marcadores `===== PAGE n =====`. Intenta varios
backends en orden de calidad: PyMuPDF > pdfplumber > pypdf > `pdftotext`.
DOCX: vuelca los párrafos en orden. Intenta python-docx > docx2txt > pandoc.

Uso:
    python3 extract.py entrada.pdf  --out salida.txt
    python3 extract.py entrada.docx --out salida.txt
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

PAGE_SEP = "\n\n===== PAGE {n} =====\n\n"


# ---- Backends PDF ------------------------------------------------------------
def _pdf_pymupdf(pdf: Path) -> list[str] | None:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return None
    with fitz.open(pdf) as doc:
        return [page.get_text("text") for page in doc]


def _pdf_pdfplumber(pdf: Path) -> list[str] | None:
    try:
        import pdfplumber
    except ImportError:
        return None
    with pdfplumber.open(pdf) as doc:
        return [(page.extract_text() or "") for page in doc.pages]


def _pdf_pypdf(pdf: Path) -> list[str] | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            return None
    reader = PdfReader(str(pdf))
    return [(p.extract_text() or "") for p in reader.pages]


def _pdf_pdftotext(pdf: Path) -> list[str] | None:
    if shutil.which("pdftotext") is None:
        return None
    out = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    return out.split("\f")


PDF_BACKENDS = [
    ("PyMuPDF", _pdf_pymupdf),
    ("pdfplumber", _pdf_pdfplumber),
    ("pypdf", _pdf_pypdf),
    ("pdftotext", _pdf_pdftotext),
]


# ---- Backends DOCX -----------------------------------------------------------
def _docx_python_docx(doc: Path) -> str | None:
    try:
        from docx import Document  # python-docx
    except ImportError:
        return None
    d = Document(str(doc))
    return "\n\n".join(p.text for p in d.paragraphs)


def _docx_docx2txt(doc: Path) -> str | None:
    try:
        import docx2txt
    except ImportError:
        return None
    return docx2txt.process(str(doc))


def _docx_pandoc(doc: Path) -> str | None:
    if shutil.which("pandoc") is None:
        return None
    return subprocess.run(
        ["pandoc", "-t", "plain", str(doc)],
        capture_output=True, text=True, check=True,
    ).stdout


DOCX_BACKENDS = [
    ("python-docx", _docx_python_docx),
    ("docx2txt", _docx_docx2txt),
    ("pandoc", _docx_pandoc),
]


# ---- Orquestación ------------------------------------------------------------
def extract_pdf(pdf: Path) -> tuple[list[str], str]:
    for name, fn in PDF_BACKENDS:
        try:
            pages = fn(pdf)
        except Exception as exc:  # noqa: BLE001
            print(f"  [{name}] error: {exc}", file=sys.stderr)
            continue
        if pages is not None and any(p.strip() for p in pages):
            return pages, name
    return [], "ninguno"


def extract_docx(doc: Path) -> tuple[str, str]:
    for name, fn in DOCX_BACKENDS:
        try:
            text = fn(doc)
        except Exception as exc:  # noqa: BLE001
            print(f"  [{name}] error: {exc}", file=sys.stderr)
            continue
        if text and text.strip():
            return text, name
    return "", "ninguno"


def guess_headings(text: str) -> list[str]:
    """Sugiere posibles títulos/secciones/artículos por heurística."""
    pat = re.compile(
        r"^\s*(cap[ií]tulo|secci[oó]n|parte|t[ií]tulo|art[ií]culo|chapter|part|article)\b",
        re.IGNORECASE,
    )
    out: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if not s or len(s) > 90:
            continue
        is_upper = s == s.upper() and any(c.isalpha() for c in s) and len(s) > 3
        if (pat.match(s) or is_upper) and s not in seen:
            seen.add(s)
            out.append(s)
    return out[:80]


def main() -> int:
    ap = argparse.ArgumentParser(description="Extrae texto de un PDF o .docx.")
    ap.add_argument("doc", type=Path, help="Ruta del documento (PDF o .docx)")
    ap.add_argument("--out", type=Path, required=True, help="Archivo .txt de salida")
    args = ap.parse_args()

    src: Path = args.doc
    if not src.exists():
        print(f"No existe el documento: {src}", file=sys.stderr)
        return 1

    suffix = src.suffix.lower()
    args.out.parent.mkdir(parents=True, exist_ok=True)

    if suffix in {".docx", ".doc"}:
        text, backend = extract_docx(src)
        if not text:
            print(
                "No se pudo extraer el .docx. Instala un backend: "
                "`pip install python-docx` o `pip install docx2txt`.",
                file=sys.stderr,
            )
            return 2
        args.out.write_text(text, encoding="utf-8")
        chars, pages = len(text), None
    elif suffix == ".pdf":
        page_list, backend = extract_pdf(src)
        if not page_list:
            print(
                "No se pudo extraer el PDF. Instala un backend (`pip install pymupdf`) "
                "o, si es escaneado, aplica OCR (`ocrmypdf in.pdf out.pdf`).",
                file=sys.stderr,
            )
            return 2
        with args.out.open("w", encoding="utf-8") as f:
            for i, t in enumerate(page_list, 1):
                f.write(PAGE_SEP.format(n=i))
                f.write(t)
        text = "".join(page_list)
        chars, pages = len(text), len(page_list)
    else:
        print(f"Formato no soportado: {suffix}. Usa PDF o .docx.", file=sys.stderr)
        return 1

    headings = guess_headings(text)
    print(f"Backend usado : {backend}")
    if pages is not None:
        print(f"Páginas       : {pages}")
    print(f"Caracteres    : {chars}")
    print(f"Salida        : {args.out}")
    if headings:
        print("\nPosibles títulos / secciones / artículos detectados:")
        for h in headings:
            print(f"  - {h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
