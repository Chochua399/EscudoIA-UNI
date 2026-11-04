"""Diagnóstico de dependencias para Windows / Visual Studio Code."""
from __future__ import annotations
import importlib
import platform
import sys
from importlib import metadata

DEPENDENCIAS = {
    "numpy": "numpy", "pandas": "pandas", "scipy": "scipy",
    "scikit-learn": "sklearn", "matplotlib": "matplotlib",
    "streamlit": "streamlit", "joblib": "joblib",
    "jupyterlab": "jupyterlab", "ipykernel": "ipykernel", "pytest": "pytest",
}


def main():
    print(f"Python: {platform.python_version()} | executable: {sys.executable}")
    print("Arquitectura:", platform.architecture()[0])
    missing = []
    for name, module in DEPENDENCIAS.items():
        try:
            importlib.import_module(module)
            version = metadata.version(name)
            print(f"[OK] {name}: {version}")
        except Exception as exc:
            print(f"[FALTA] {name}: {exc}")
            missing.append(name)
    if sys.version_info[:2] != (3, 14):
        print("[AVISO] Proyecto dirigido a Python 3.14.5; estás usando una versión distinta.")
    if missing:
        print("Instala con: .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt")
        return 1
    print("[OK] Entorno listo para entrenamiento real y Streamlit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
