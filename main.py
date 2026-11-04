"""Punto de entrada sencillo de EscudoIA para Visual Studio Code.

Uso:
    python main.py                # Abrir app Streamlit
    python main.py todo           # Preparar, EDA, entrenar
    python main.py todo --rapido  # Prueba del entrenamiento menos costosa
    python main.py estado         # Verificar datos/modelo
    python main.py verificar      # Confirmar que hay evidencia científica
    python main.py publicar       # Crear carpeta y ZIP listos para GitHub
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

from src.config import ROOT, MODEL_FILE, METRICS, RAW, SOURCE_URL, ensure_dirs


def main():
    parser = argparse.ArgumentParser(description="EscudoIA · ejecución desde Visual Studio Code")
    parser.add_argument("accion", nargs="?", default="app", choices=["app", "todo", "datos", "eda", "entrenar", "pruebas", "estado", "publicar", "verificar"])
    parser.add_argument("--input", help="Ruta opcional al CSV de SpaPhish")
    parser.add_argument("--rapido", action="store_true", help="Reduce la cuadrícula y utiliza CV de 3 pliegues")
    args = parser.parse_args()
    ensure_dirs()
    if args.accion == "estado":
        print("Proyecto:", ROOT)
        print("Python:", sys.version.split()[0])
        print("CSV locales:", [p.name for p in RAW.glob("*.csv")] or "ninguno")
        print("Modelo:", MODEL_FILE if MODEL_FILE.exists() else "SIN ENTRENAR")
        print("Resultados:", "disponibles" if (METRICS / "resultados.json").exists() else "pendientes")
        print("Dataset oficial:", SOURCE_URL)
    elif args.accion == "app":
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", str(ROOT / "app" / "app.py")],
                           cwd=ROOT, check=True)
        except subprocess.CalledProcessError as exc:
            raise SystemExit(f"No se pudo iniciar la interfaz. Instale requirements.txt. Código: {exc.returncode}")
    elif args.accion == "verificar":
        from src.release.package_github import check_ready
        check_ready(verbose=True)
    elif args.accion == "publicar":
        from src.release.package_github import package_release
        package_release(verbose=True)
    elif args.accion == "pruebas":
        subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, check=True)
    else:
        if args.accion in ("datos", "todo"):
            from src.data.make_dataset import prepare
            prepare(args.input)
            print("Dataset procesado.")
        if args.accion in ("eda", "todo"):
            from src.visualization.visualize import make_eda
            make_eda(args.input)
        if args.accion in ("entrenar", "todo"):
            from src.models.train_model import train
            train(args.input, quick=args.rapido)


if __name__ == "__main__":
    main()
