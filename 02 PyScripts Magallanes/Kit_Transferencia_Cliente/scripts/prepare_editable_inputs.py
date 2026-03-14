#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path

from project_paths import BASE_DIR_PATH, EDITABLE_INPUTS_DIR_PATH, editable_target, ensure_editable_root, iter_catalog, write_catalog_csv


def files_to_copy(source: Path) -> list[Path]:
    if not source.exists():
        return []
    if source.suffix.lower() == ".shp":
        return sorted(p for p in source.parent.glob(f"{source.stem}.*") if p.is_file())
    if source.suffix.lower() == ".tif":
        return sorted(p for p in source.parent.glob(f"{source.name}*") if p.is_file())
    return [source]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepara Editable_Inputs para el proyecto Magallanes")
    parser.add_argument(
        "--category",
        action="append",
        dest="categories",
        help="Categoria a copiar (puede repetirse). Si se omite, copia todas.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescribe archivos ya existentes en Editable_Inputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    category_filter = set(args.categories or [])
    editable_root = ensure_editable_root()
    inventory_rows: list[dict[str, str]] = []

    for item in iter_catalog():
        if category_filter and item["category"] not in category_filter:
            continue

        rel = Path(item["relative_path"])
        src = BASE_DIR_PATH / rel
        dst = editable_target(rel)
        copied = 0
        skipped = 0

        for src_file in files_to_copy(src):
            rel_file = src_file.relative_to(BASE_DIR_PATH)
            dst_file = editable_root / rel_file
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            if dst_file.exists() and not args.overwrite:
                skipped += 1
                continue
            shutil.copy2(src_file, dst_file)
            copied += 1

        inventory_rows.append(
            {
                "category": item["category"],
                "relative_path": item["relative_path"],
                "source_exists": "yes" if src.exists() else "no",
                "editable_target": str(dst.relative_to(editable_root)),
                "files_copied": str(copied),
                "files_skipped": str(skipped),
            }
        )

    write_catalog_csv(editable_root / "input_catalog.csv")

    inventory_path = editable_root / "input_inventory.csv"
    with inventory_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["category", "relative_path", "source_exists", "editable_target", "files_copied", "files_skipped"],
        )
        writer.writeheader()
        writer.writerows(inventory_rows)

    readme = editable_root / "README.md"
    readme.write_text(
        "# Editable_Inputs\n\n"
        "Los scripts del proyecto usan automaticamente cualquier archivo presente en esta carpeta si conserva la misma ruta relativa respecto a 01 Magallanes.\n\n"
        "Flujo recomendado:\n\n"
        "1. Ejecutar prepare_editable_inputs.py una vez o por categoria.\n"
        "2. Editar aqui los SHP, raster, CSV, XLSX o JSON necesarios.\n"
        "3. Re-ejecutar los scripts del proyecto normalmente.\n"
        "4. Mantener los nombres de archivo y la ruta relativa.\n",
        encoding="utf-8",
    )

    print(f"[editable-inputs] OK: {editable_root}")
    print(f"[editable-inputs] Inventario: {inventory_path}")
    if category_filter:
        print(f"[editable-inputs] Categorias copiadas: {', '.join(sorted(category_filter))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
