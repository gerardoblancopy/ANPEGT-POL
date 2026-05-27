#!/usr/bin/env python3
"""Copia la plantilla web al directorio de salida e inserta el book.json.

Uso:
    python3 scaffold.py --out <dir-de-salida> [--book <ruta-book.json>]

Si no se pasa --book, se conserva el book.json de muestra de la plantilla.
No sobreescribe node_modules ni dist existentes en el destino.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_ROOT / "template"

SKIP = {"node_modules", "dist", ".vite"}


def copy_template(dst: Path) -> None:
    for src in TEMPLATE.rglob("*"):
        rel = src.relative_to(TEMPLATE)
        if any(part in SKIP for part in rel.parts):
            continue
        target = dst / rel
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold del libro de lectura asistida.")
    ap.add_argument("--out", type=Path, required=True, help="Directorio de salida")
    ap.add_argument("--book", type=Path, help="Ruta a un book.json para insertar")
    args = ap.parse_args()

    if not TEMPLATE.exists():
        print(f"No se encuentra la plantilla: {TEMPLATE}", file=sys.stderr)
        return 1

    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    copy_template(out)

    if args.book:
        if not args.book.exists():
            print(f"No existe el book.json: {args.book}", file=sys.stderr)
            return 1
        try:
            data = json.loads(args.book.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"book.json no es JSON válido: {exc}", file=sys.stderr)
            return 1
        dst_book = out / "src" / "book.json"
        dst_book.parent.mkdir(parents=True, exist_ok=True)
        dst_book.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        chapters = data.get("chapters", [])
        n_ch = len(chapters)
        n_sec = sum(len(c.get("sections", [])) for c in chapters)
        n_par = sum(len(s.get("paragraphs", [])) for c in chapters for s in c.get("sections", []))
        n_con = len(data.get("concepts", []))
        print(
            f"Insertado book.json: {n_ch} capítulos, {n_sec} secciones, "
            f"{n_par} párrafos, {n_con} conceptos."
        )

    print(f"Plantilla generada en: {out}")
    print("Siguiente: cd al directorio y `npm install && npm run build`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
