"""Descarga opcional del CSV público SpaPhish v5 por la API oficial de Mendeley.

No es necesaria para usar el programa; siempre existe la alternativa de subir
manualmente el CSV descargado desde la página pública del dataset.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import json
import urllib.request
import urllib.error
import tempfile
import os

from src.config import RAW, ensure_dirs
from src.data.make_dataset import read_csv

DATASET_ID = "hz2d6gz7pc"
VERSION = 5
API_URL = f"https://api.data.mendeley.com/datasets/publics/{DATASET_ID}/files?version={VERSION}"
MAX_BYTES = 16 * 1024 * 1024


def _retrieve_bytes(url: str, maximum: int = MAX_BYTES) -> bytes:
    if not url.startswith("https://"):
        raise ValueError("Solo se admiten enlaces HTTPS públicos de Mendeley Data.")
    request = urllib.request.Request(url, headers={"User-Agent": "EscudoIA-Academic/1.0", "Accept": "application/json, text/csv, */*"})
    with urllib.request.urlopen(request, timeout=35) as response:
        payload = response.read(maximum + 1)
    if len(payload) > maximum:
        raise ValueError("El archivo descargado supera el tamaño máximo permitido.")
    return payload


def find_csv_entry(metadata) -> dict:
    """Admite listas y respuestas públicas con paginación o contenedores."""
    if isinstance(metadata, dict):
        for field in ("files", "data", "content", "results"):
            if isinstance(metadata.get(field), list):
                metadata = metadata[field]
                break
    if not isinstance(metadata, list):
        raise ValueError("La API devolvió un formato de lista de archivos no reconocido.")
    for item in metadata:
        if not isinstance(item, dict):
            continue
        filename = item.get("filename") or item.get("name") or item.get("file_name") or ""
        if str(filename).lower().endswith(".csv") and ("spaphish" in str(filename).lower() or "dataset" in str(filename).lower()):
            file_id = item.get("id") or item.get("file_id") or item.get("uuid")
            if file_id:
                return {"filename": filename, "id": str(file_id)}
    raise FileNotFoundError("No se encontró el CSV de SpaPhish en la lista pública de Mendeley Data.")


def download_spaphish(output: str | Path | None = None) -> Path:
    """Obtiene el archivo público, valida el esquema CSV y escribe de modo atómico."""
    ensure_dirs()
    if output is None:
        output = RAW / "SpaPhish_v5_oficial.csv"
    output = Path(output)
    if output.exists():
        raise FileExistsError(f"Ya existe el archivo {output}; no se sobrescribirá.")
    try:
        metadata = json.loads(_retrieve_bytes(API_URL, maximum=2 * 1024 * 1024).decode("utf-8"))
        csv_item = find_csv_entry(metadata)
        url = f"https://api.data.mendeley.com/datasets/{DATASET_ID}/files/{csv_item['id']}/file_downloaded?version={VERSION}"
        csv_bytes = _retrieve_bytes(url)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "No fue posible descargar automáticamente desde Mendeley. "
            "Abre https://data.mendeley.com/datasets/hz2d6gz7pc/5, "
            "descarga el CSV y súbelo manualmente desde la interfaz. "
            f"Detalle técnico: {exc}"
        ) from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    # El archivo temporal se limpia aunque el CSV no sea válido.
    fd, temp_path = tempfile.mkstemp(prefix="escudoia_v5_", suffix=".csv", dir=output.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(csv_bytes)
        table = read_csv(temp_path)
        if table.empty or "label" not in table.columns:
            raise ValueError("El archivo descargado no tiene registros o carece de etiquetas.")
        Path(temp_path).replace(output)
    finally:
        if Path(temp_path).exists():
            Path(temp_path).unlink()
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descarga opcional de SpaPhish v5 desde Mendeley")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    print("CSV guardado:", download_spaphish(args.output))
