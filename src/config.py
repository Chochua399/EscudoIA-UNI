"""Rutas del proyecto: independencia respecto del directorio de trabajo."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
EXTERNAL = ROOT / "data" / "external"
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"
METRICS = REPORTS / "metrics"
FIGURES = REPORTS / "figures"
EDA = REPORTS / "eda"
MODEL_FILE = MODELS / "modelo_estafas_v1.joblib"
MODEL_META = MODELS / "metadata_modelo.json"
SOURCE_URL = "https://data.mendeley.com/datasets/hz2d6gz7pc/5"
SOURCE_DOI = "10.17632/hz2d6gz7pc.5"


def ensure_dirs():
    for location in (RAW, PROCESSED, EXTERNAL, MODELS, METRICS, FIGURES, EDA):
        location.mkdir(parents=True, exist_ok=True)
