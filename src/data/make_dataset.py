"""SpaPhish: validación, deduplicación y preparación SIN modificar el original."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

from src.config import RAW, PROCESSED, METRICS, SOURCE_DOI, ensure_dirs

REQUIRED_COLUMNS = {"subject", "body", "label"}


def normalize_text(value: object) -> str:
    """Uniformiza Unicode y espacios, sin borrar números, URL ni dinero."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value))).strip()


def identify_file(path: str | Path | None = None) -> Path:
    """Encuentra un CSV oficial descargado; nunca descarga mensajes privados."""
    if path:
        found = Path(path).expanduser().resolve()
        if not found.is_file():
            raise FileNotFoundError(f"No se encontró el CSV: {found}")
        return found
    matches = sorted(RAW.glob("*.csv"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(
            f"No hay CSV en {RAW}. Descargue SpaPhish v5 desde "
            "https://data.mendeley.com/datasets/hz2d6gz7pc/5 y copie el CSV allí."
        )
    raise ValueError(
        "Hay varios CSV en data/raw/. Indique cuál usar con --input RUTA. "
        f"Encontrados: {[p.name for p in matches]}"
    )


def read_csv(path: str | Path) -> pd.DataFrame:
    """Admite ';' (formato oficial), coma y BOM; exige columnas reales."""
    path = Path(path)
    errors = []
    for sep in (";", ",", "\t"):
        try:
            df = pd.read_csv(path, sep=sep, encoding="utf-8-sig", low_memory=False, dtype={"Label": "string"})
            df.columns = [str(col).strip().lower().lstrip("\ufeff") for col in df.columns]
            if REQUIRED_COLUMNS.issubset(df.columns):
                return df
            errors.append(f"Separador {repr(sep)}: columnas {list(df.columns)[:8]}")
        except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"Separador {repr(sep)}: {exc}")
    raise ValueError(
        "El CSV no contiene las columnas subject, body y Label esperadas. "
        "Compruebe que haya descargado el CSV de SpaPhish v5. " + " / ".join(errors)
    )


def _fingerprint(text: str) -> str:
    """Clave de plantillas parecidas para impedir solapamiento train/test."""
    text = text.casefold()
    text = re.sub(r"(?:https?://|www\.)\S+", " ENLACE ", text)
    text = re.sub(r"\b\d+(?:[.,]\d+)*\b", " NUMERO ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]


def load_spaphish(path: str | Path) -> tuple[pd.DataFrame, dict]:
    """Retorna texto y etiqueta 0=legítimo, 1=phishing; nunca usa anotaciones como predictores."""
    p = identify_file(path)
    raw = read_csv(p)
    original_missing = {col: int(raw[col].isna().sum()) for col in ("subject", "body", "label")}
    df = raw.copy()
    y = df["label"].astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    y = y.str.replace(r"^0+(?=\d)", "", regex=True)
    df["label"] = pd.to_numeric(y, errors="coerce")
    invalid_count = int((~df["label"].isin([0, 1])).sum())
    df = df[df["label"].isin([0, 1])].copy()
    df["label"] = df["label"].astype(int)
    for col in ("subject", "body"):
        df[col] = df[col].fillna("").map(normalize_text)
    df["text"] = (df["subject"] + " " + df["body"]).str.strip()
    empty_count = int((df["text"].str.len() < 4).sum())
    df = df[df["text"].str.len() >= 4].copy()
    df["text_key"] = df["text"].str.casefold()
    conflicts = df.groupby("text_key")["label"].nunique()
    conflict_keys = set(conflicts[conflicts > 1].index)
    conflict_count = int(df["text_key"].isin(conflict_keys).sum())
    df = df[~df["text_key"].isin(conflict_keys)].copy()
    duplicates_count = int(df.duplicated("text_key").sum())
    df = df.drop_duplicates("text_key", keep="first")
    df["group"] = df["text"].map(_fingerprint)
    groups_conflict = df.groupby("group")["label"].nunique()
    mixed_groups = int((groups_conflict > 1).sum())
    df = df.drop(columns=["text_key"]).reset_index(drop=True)
    if df["label"].nunique() != 2:
        raise ValueError("El CSV procesado debe tener ejemplos de ambas clases (0/1).")
    stat = {
        "fuente": "SpaPhish; archivo local proporcionado por el investigador",
        "doi_esperado": SOURCE_DOI,
        "archivo": p.name,
        "sha256_archivo_original": hashlib.sha256(p.read_bytes()).hexdigest(),
        "filas_originales": int(len(raw)),
        "columnas_originales": int(len(raw.columns)),
        "nulos_originales": original_missing,
        "etiquetas_invalidas_descartadas": invalid_count,
        "textos_vacios_descartados": empty_count,
        "filas_conflicto_descartadas": conflict_count,
        "duplicados_exactos_descartados": duplicates_count,
        "duplicados_descartados": duplicates_count,
        "plantillas_normalizadas_grupos": int(df["group"].nunique()),
        "grupos_con_etiquetas_mixtas": mixed_groups,
        "filas_preparadas": int(len(df)),
        "legitimos_0": int((df["label"] == 0).sum()),
        "phishing_1": int((df["label"] == 1).sum()),
        "nota": "Las cifras de origen no se confunden con registros retenidos después de limpiar.",
    }
    return df, stat


def prepare(input_path=None, output=None):
    ensure_dirs()
    path = identify_file(input_path)
    data, stats = load_spaphish(path)
    out = Path(output) if output else PROCESSED / "mensajes_preparados.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    data[["subject", "body", "text", "label", "group"]].to_csv(out, index=False, encoding="utf-8")
    (METRICS / "auditoria_dataset.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    return out, stats


def main():
    parser = argparse.ArgumentParser(description="Prepara el dataset SpaPhish sin modificar data/raw")
    parser.add_argument("--input", help="CSV original de SpaPhish; opcional si hay uno en data/raw")
    parser.add_argument("--output", help="Ruta opcional para el CSV procesado")
    args = parser.parse_args()
    out, info = prepare(args.input, args.output)
    print("Archivo preparado:", out)
    print(json.dumps(info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
