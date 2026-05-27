#!/usr/bin/env python3
"""Extrae texto de un PDF, separando páginas con marcadores.

Intenta varios backends en orden de calidad: PyMuPDF (fitz) > pdfplumber >
pypdf > el binario `pdftotext`. Escribe el texto en --out e imprime un breve
resumen (páginas, títulos candidatos) en stdout para orientar la estructuración.

Uso:
    python3 extract_pdf.py entrada.pdf --out salida.txt
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

PAGE_SEP = "\n\n===== PAGE {n} =====\n\n"


def _try_pymupdf(pdf: Path) -> list[str] | None:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return None
    pages = []
    with fitz.open(pdf) as doc:
        for page in doc:
            pages.append(page.get_text("text"))
    return pages


def _try_pdfplumber(pdf: Path) -> list[str] | None:
    try:
        import pdfplumber
    except ImportError:
        return None
    pages = []
    with pdfplumber.open(pdf) as doc:
        for page in doc.pages:
            pages.append(page.extract_text() or "")
    return pages


def _try_pypdf(pdf: Path) -> list[str] | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            return None
    reader = PdfReader(str(pdf))
    return [(p.extract_text() or "") for p in reader.pages]


def _try_pdftotext(pdf: Path) -> list[str] | None:
    if shutil.which("pdftotext") is None:
        return None
    # -layout preserva mejor la estructura; \f separa páginas.
    out = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return out.split("\f")


BACKENDS = [
    ("PyMuPDF", _try_pymupdf),
    ("pdfplumber", _try_pdfplumber),
    ("pypdf", _try_pypdf),
    ("pdftotext", _try_pdftotext),
]


def extract(pdf: Path) -> tuple[list[str], str]:
    for name, fn in BACKENDS:
        try:
            pages = fn(pdf)
        except Exception as exc:  # noqa: BLE001 - reportar y seguir
            print(f"  [{name}] error: {exc}", file=sys.stderr)
            continue
        if pages is not None and any(p.strip() for p in pages):
            return pages, name
    return [], "ninguno"


def guess_headings(pages: list[str]) -> list[str]:
    """Heurística simple para sugerir títulos: líneas cortas en mayúsculas o que
    empiezan con CAPÍTULO/SECCIÓN/numeración romana o arábiga."""
    pat = re.compile(
        r"^\s*(cap[ií]tulo|secci[oó]n|parte|chapter|part)\b",
        re.IGNORECASE,
    )
    candidates: list[str] = []
    for text in pages:
        for line in text.splitlines():
            s = line.strip()
            if not s or len(s) > 80:
                continue
            is_upper = s == s.upper() and any(c.isalpha() for c in s) and len(s) > 3
            if pat.match(s) or is_upper:
                candidates.append(s)
    # Deduplicar conservando orden.
    seen, out = set(), []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out[:60]


def main() -> int:
    ap = argparse.ArgumentParser(description="Extrae texto de un PDF por páginas.")
    ap.add_argument("pdf", type=Path, help="Ruta del PDF de entrada")
    ap.add_argument("--out", type=Path, required=True, help="Archivo .txt de salida")
    args = ap.parse_args()

    pdf: Path = args.pdf
    if not pdf.exists():
        print(f"No existe el PDF: {pdf}", file=sys.stderr)
        return 1

    pages, backend = extract(pdf)
    if not pages:
        print(
            "No se pudo extraer texto. Instala un backend (`pip install pymupdf`) "
            "o, si el PDF es escaneado, aplica OCR (`ocrmypdf in.pdf out.pdf`).",
            file=sys.stderr,
        )
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for i, text in enumerate(pages, 1):
            f.write(PAGE_SEP.format(n=i))
            f.write(text)

    chars = sum(len(p) for p in pages)
    headings = guess_headings(pages)
    print(f"Backend usado : {backend}")
    print(f"Páginas       : {len(pages)}")
    print(f"Caracteres    : {chars}")
    print(f"Salida        : {args.out}")
    if headings:
        print("\nPosibles títulos/secciones detectados:")
        for h in headings:
            print(f"  - {h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
