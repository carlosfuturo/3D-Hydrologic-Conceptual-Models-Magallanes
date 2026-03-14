#!/usr/bin/env python3
"""Genera un manifiesto SHA256 de archivos relevantes para entrega."""

from __future__ import annotations

import hashlib
from pathlib import Path
from datetime import datetime


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    kit_dir = script_dir.parent
    project_dir = kit_dir.parent
    output_dir = kit_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    include_dirs = [
        "Figuras_3D_Leapfrog",
        "Figuras_Obs6_ModeloSubterraneo",
        "Figuras_Obs7_ModeloSuperficial",
        "Figuras_Obs6_Obs7_Balance",
        "Texto_Correcciones_Obs67",
        "DEM_Copernicus_30m",
    ]

    include_files = [
        "datos_cuencas.json",
        "pozos_acuifero.csv",
        "pozos_acuifero.geojson",
        "dataset_estratigrafico_UH.csv",
    ]

    manifest_path = output_dir / f"manifest_sha256_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    rows = []

    for rel in include_files:
        p = project_dir / rel
        if p.exists() and p.is_file():
            rows.append((str(p.relative_to(project_dir)), p.stat().st_size, sha256_file(p)))

    for rel_dir in include_dirs:
        d = project_dir / rel_dir
        if not d.exists() or not d.is_dir():
            continue
        for p in d.rglob("*"):
            if not p.is_file():
                continue
            rows.append((str(p.relative_to(project_dir)), p.stat().st_size, sha256_file(p)))

    rows.sort(key=lambda x: x[0])

    total_size = sum(size for _, size, _ in rows)
    with manifest_path.open("w", encoding="utf-8") as f:
        f.write("# Manifest SHA256 - Proyecto Magallanes\n")
        f.write(f"# Generado: {datetime.now().isoformat()}\n")
        f.write(f"# Archivos: {len(rows)}\n")
        f.write(f"# Tamano total (bytes): {total_size}\n\n")
        f.write("# sha256  bytes  path\n")
        for rel_path, size, digest in rows:
            f.write(f"{digest}  {size}  {rel_path}\n")

    print(f"[manifest] OK: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
