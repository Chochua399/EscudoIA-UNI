"""Señales educativas deterministas: no garantizan diagnóstico de phishing."""
from __future__ import annotations
import re
from src.data.make_dataset import normalize_text

# Registros ficticios de documentación, sin URLs clicables ni accesos externos.
SIGNAL_RULES = {
    "Urgencia o presión": r"\b(?:urgente|urgencia|inmediat[ao]|inmediatamente|últim[ao] avis[oa]|hoy mismo|en 24 horas|bloquead[ao]|suspendid[ao]|cancelar[áa])\b",
    "Solicitud de credenciales o datos sensibles": r"\b(?:contraseña|clave|pin|credenciales|c[oó]digo de verificaci[oó]n|datos bancarios|tarjeta de cr[eé]dito|n[uú]mero de tarjeta|otp)\b",
    "Premio, regalo o beneficio inesperado": r"\b(?:premio|ganaste|gan[oó]|bonificaci[oó]n|herencia|regalo|sorteo|recompensa)\b",
    "Transferencia, cobro o depósito": r"\b(?:depositar|transferencia|pagar|pago pendiente|abonar|tarifa|dep[oó]sito|c[oó]rdobas)\b",
    "Suplantación de autoridad aparente": r"\b(?:banco|soporte t[eé]cnico|administraci[oó]n|equipo de seguridad|polic[ií]a|ministerio)\b",
}
LINK_RE = re.compile(r"(?i)(?:https?://|www\.|hxxps?://|\[\.\]|\(\.\))")


def detect_signals(text: str) -> list[str]:
    value = normalize_text(text).casefold()
    signals = [label for label, pattern in SIGNAL_RULES.items() if re.search(pattern, value, re.I)]
    if LINK_RE.search(value):
        signals.append("Incluye una dirección web o un enlace ofuscado (sin verificación de destino)")
    if value.count("!") >= 3:
        signals.append("Uso repetido de signos de exclamación")
    return signals


def signal_summary(text: str) -> dict:
    value = normalize_text(text)
    return {
        "n_caracteres": len(value),
        "n_palabras": len(value.split()),
        "contiene_enlace": bool(LINK_RE.search(value)),
        "senales": detect_signals(value),
    }
