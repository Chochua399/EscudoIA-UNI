"""Predicción local (sin conexiones de red, sin persistir mensajes de usuarios)."""
from __future__ import annotations
import json
from pathlib import Path

import joblib

from src.config import MODEL_FILE, MODEL_META
from src.data.make_dataset import normalize_text
from src.features.build_features import detect_signals

RECOMMENDATIONS = [
    "No abras enlaces ni descargues archivos que no esperabas recibir.",
    "Contacta a la organización por su sitio o teléfono oficial, buscado independientemente.",
    "Nunca compartas contraseñas, PIN, códigos de verificación o datos bancarios.",
    "Si sospechas una estafa, conserva evidencia y utiliza el canal oficial para reportarla.",
]


def load_model(path=None):
    filename = Path(path) if path else MODEL_FILE
    if not filename.exists():
        raise FileNotFoundError("No se ha entrenado la IA. Ejecuta en VS Code: python -m src.models.train_model")
    # joblib (pickle) solamente para artefactos generados localmente y confiables.
    return joblib.load(filename)


def load_metadata(path=None):
    filename = Path(path) if path else MODEL_META
    if not filename.exists():
        return {}
    return json.loads(filename.read_text(encoding="utf-8"))


def analyze_message(message: str, model=None, model_path=None, metadata=None):
    text = normalize_text(message)
    if len(text) < 12:
        raise ValueError("Introduce un mensaje de al menos 12 caracteres para ofrecer suficiente contexto.")
    if len(text) > 20000:
        raise ValueError("El mensaje supera el máximo de 20.000 caracteres.")
    model = model if model is not None else load_model(model_path)
    predicted = int(model.predict([text])[0])
    probability = None
    if hasattr(model, "predict_proba"):
        classes = list(model.classes_) if hasattr(model, "classes_") else [0, 1]
        probability = float(model.predict_proba([text])[0][classes.index(1)])
    meta = metadata if metadata is not None else load_metadata()
    thresholds = meta.get("umbrales_riesgo", {"bajo_hasta": .35, "alto_desde": .70,
                                              "estado": "provisionales"})
    if probability is None:
        risk = "Sin puntaje probabilístico"
    elif probability < thresholds["bajo_hasta"]:
        risk = "Bajo (orientativo)"
    elif probability >= thresholds["alto_desde"]:
        risk = "Alto (orientativo)"
    else:
        risk = "Medio (orientativo)"
    return {
        "clase": "Posible phishing" if predicted == 1 else "No se observan suficientes señales para clasificar como phishing",
        "etiqueta": predicted,
        "riesgo": risk,
        "puntaje_modelo": probability,
        "senales": detect_signals(text),
        "recomendaciones": RECOMMENDATIONS,
        "advertencia": "Este modelo compara patrones textuales. No verifica el remitente ni la seguridad de sitios o enlaces; puede equivocarse.",
        "modelo": meta.get("modelo", "Modelo local"),
        "umbrales_estado": thresholds.get("estado", "no documentado"),
    }


def educational_signals_only(message):
    """Vista de demostración SIN modelo: NO realiza inferencia de IA."""
    text = normalize_text(message)
    if len(text) < 12:
        raise ValueError("Introduce al menos 12 caracteres.")
    if len(text) > 20000:
        raise ValueError("El mensaje supera 20.000 caracteres.")
    return {
        "modo": "DEMO DE REGLAS: NO ES PREDICCIÓN DE IA",
        "senales": detect_signals(text),
        "recomendaciones": RECOMMENDATIONS,
        "advertencia": "Las palabras encontradas no demuestran que exista fraude. Falta entrenar el modelo SpaPhish.",
    }
