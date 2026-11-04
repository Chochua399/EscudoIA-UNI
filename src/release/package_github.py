"""Empaqueta una edición revisable en GitHub/Streamlit SIN corpus original.

Debe ejecutarse DESPUÉS del entrenamiento local con SpaPhish oficial.
No sube datos ni hace operaciones con GitHub; construye la carpeta de subida.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
import zipfile

import joblib

from src.config import ROOT, MODEL_FILE, MODEL_META, MODELS, REPORTS, EDA, FIGURES, METRICS

STAGE_NAME = "ESCUDOIA_LISTO_PARA_GITHUB"
REQUIRED_FIGURES = ("matriz_confusion.png", "curva_roc.png", "curva_precision_recall.png")
REQUIRED_EDA = (
    "01_distribucion_clases.png", "02_longitud_palabras.png", "03_indicadores_por_clase.png",
    "04_boxplot_longitud.png", "05_valores_ausentes.png", "06_enlaces_por_clase.png",
    "07_terminos_phishing.png",
)


def check_ready(*, strict=True, verbose=False, root=None):
    """Exige artefacto, evaluación y gráficos consistentes.

    strict=True protege al usuario contra la publicación accidental de datos
    diminutos/sintéticos; no es una validación criptográfica de la procedencia.
    """
    base = Path(root) if root else ROOT
    model_file = base / "models/modelo_estafas_v1.joblib"
    metrics = base / "reports/metrics/resultados.json"
    metadata = base / "models/metadata_modelo.json"
    eda = base / "reports/eda/eda_resumen.json"
    audit = base / "reports/metrics/auditoria_dataset.json"
    summary = base / "reports/RESUMEN_REAL_PARA_INFORME.md"
    comparisons = base / "reports/metrics/comparacion_validacion.csv"
    expected = [model_file, metrics, metadata, eda, audit, summary, comparisons]
    expected += [base / "reports/eda" / f for f in REQUIRED_EDA]
    expected += [base / "reports/figures" / f for f in REQUIRED_FIGURES]
    missing = [str(f.relative_to(base)) for f in expected if not f.is_file() or f.stat().st_size == 0]
    if missing:
        raise RuntimeError("Faltan resultados necesarios para publicar: " + ", ".join(missing) + ". Ejecuta primero: py -3.14 main.py todo")
    result = json.loads(metrics.read_text(encoding="utf-8"))
    meta = json.loads(metadata.read_text(encoding="utf-8"))
    original = json.loads(audit.read_text(encoding="utf-8"))
    if result.get("modelo_seleccionado_por_cv") != meta.get("modelo"):
        raise RuntimeError("Los metadatos y los resultados no corresponden al mismo modelo. Reentrena.")
    original_hash = original.get("sha256_archivo_original")
    if not original_hash or original_hash != meta.get("hash_dataset") or original_hash != result.get("dataset",{}).get("sha256_archivo_original"):
        raise RuntimeError("La auditoría y los resultados tienen hashes de dataset diferentes. Reentrena.")
    if not all(k in result.get("test_final", {}) for k in ("accuracy", "precision_phishing", "recall_phishing", "f1_phishing", "TN", "FP", "FN", "TP")):
        raise RuntimeError("El conjunto de métricas final está incompleto.")
    if len(result.get("comparacion_validacion", {})) != 3:
        raise RuntimeError("Falta la comparación de tres modelos.")
    if strict and (int(original.get("filas_originales", 0)) < 1000 or int(original.get("columnas_originales", 0)) < 40):
        raise RuntimeError(
            "El CSV usado no parece el corpus SpaPhish v5 de 1.395 registros/47 variables. "
            "No se publicará un modelo entrenado con ejemplos sintéticos o una tabla incompleta. "
            "Descarga el CSV original de Mendeley Data y ejecuta: py -3.14 main.py todo"
        )
    if strict and int(result.get("validacion_cruzada_pliegues", 0)) != 5:
        raise RuntimeError("La entrega académica requiere cinco pliegues. Ejecuta: py -3.14 main.py todo (sin --rapido).")
    model = joblib.load(model_file)  # Sólo artefactos creados por el propio usuario, jamás subidos por terceros.
    if not hasattr(model, "predict"):
        raise RuntimeError("El modelo serializado no permite predicción.")
    example = model.predict(["Hola, la reunión del curso es mañana a las 9."])
    if len(example) != 1 or int(example[0]) not in (0, 1):
        raise RuntimeError("El modelo no devolvió una clase binaria válida.")
    if verbose:
        print("VALIDACIÓN CORRECTA — modelo, 3 algoritmos, 5 pliegues, test y 10 figuras disponibles.")
        print(f"Archivo analizado: {original.get('archivo')}; filas originales: {original.get('filas_originales')}")
        print("Aviso: la estructura del CSV no prueba por sí sola la procedencia oficial; comprueba el DOI de la descarga.")
    return {"resultados": result, "modelo": meta, "auditoria": original}


def package_release(*, strict=True, verbose=False, root=None, output=None):
    """Construye carpeta y ZIP que sí incluyen el modelo ya entrenado."""
    base = Path(root) if root else ROOT
    check = check_ready(strict=strict, root=base)
    output_root = Path(output) if output else base
    target = output_root / STAGE_NAME
    zip_target = output_root / (STAGE_NAME + ".zip")
    output_root.mkdir(parents=True, exist_ok=True)
    if target.resolve() == base.resolve():
        raise ValueError("La carpeta de publicación no puede ser el directorio del proyecto.")
    with tempfile.TemporaryDirectory(prefix="escudoia_github_", dir=output_root) as tmp:
        stage = Path(tmp) / STAGE_NAME
        stage.mkdir()
        # Lista blanca: nunca copiar data/raw, data/processed, claves, .venv ni logs.
        root_files = ["main.py", "requirements.txt", "requirements-dev.txt", "pytest.ini", "README.md", "LICENSE", ".python-version"]
        for rel in root_files:
            origin = base / rel
            if origin.is_file():
                destination = stage / rel
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(origin, destination)
        source = base / ".streamlit/config.toml"
        if source.is_file():
            dest = stage / ".streamlit/config.toml"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        for directory, suffixes in (
            ("app", {".py"}), ("src", {".py"}), ("notebooks", {".ipynb"}),
            ("docs", {".md"}), ("tests", {".py"}), ("scripts", {".py"}),
        ):
            src = base / directory
            if not src.is_dir():
                continue
            for f in sorted(src.rglob("*")):
                if f.is_file() and f.suffix in suffixes:
                    dest = stage / f.relative_to(base)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
        for file in (base / "models").glob("*"):
            if file.name in {"modelo_estafas_v1.joblib", "metadata_modelo.json"}:
                dest = stage / "models" / file.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dest)
        for folder in ("metrics", "eda", "figures"):
            for f in (base / "reports" / folder).glob("*"):
                if f.is_file() and f.suffix.lower() in {".json", ".csv", ".txt", ".png"}:
                    dest = stage / "reports" / folder / f.name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
        summary = base / "reports/RESUMEN_REAL_PARA_INFORME.md"
        shutil.copy2(summary, stage / "reports" / summary.name)
        data_readme = base / "data/README.md"
        if data_readme.is_file():
            (stage / "data").mkdir(exist_ok=True)
            shutil.copy2(data_readme, stage / "data/README.md")
        (stage / "data/raw").mkdir(parents=True, exist_ok=True)
        (stage / "data/raw/.gitkeep").touch()
        (stage / ".gitignore").write_text(
            ".venv/\n__pycache__/\n*.py[cod]\n.pytest_cache/\n.ipynb_checkpoints/\n"
            ".DS_Store\n.env\n*.log\ndata/raw/*\n!data/raw/.gitkeep\n"
            "data/processed/\ndata/external/\n# Mantener models/*.joblib y reports/: los necesita el docente.\n",
            encoding="utf-8",
        )
        manifest = {
            "tipo": "PUBLICACION_ACADEMICA_SOLO_LECTURA",
            "creado_utc": datetime.now(timezone.utc).isoformat(),
            "csv_nombre_proporcionado": check["auditoria"].get("archivo"),
            "csv_sha256": check["auditoria"].get("sha256_archivo_original"),
            "version_sklearn": check["modelo"].get("version_sklearn_entrenamiento"),
            "modelo": check["modelo"].get("modelo"),
            "f1_test": check["resultados"]["test_final"]["f1_phishing"],
            "nota": "El dataset original no se publica. Las métricas reflejan el archivo proporcionado, no validación en mensajería instantánea. La procedencia real debe cotejarse con el DOI de SpaPhish.",
        }
        (stage / "deployment_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (stage / "IMPORTANTE_ANTES_DE_GITHUB.txt").write_text(
            "ESCUDOIA · ENTREGA ACADÉMICA\n\n"
            "Este paquete CONTIENE el modelo entrenado y las evidencias pero NO contiene el CSV original.\n"
            "Sube todos los archivos de esta carpeta a la RAÍZ de un repositorio de GitHub.\n"
            "En https://share.streamlit.io selecciona el repositorio, rama main, ruta app/app.py\n"
            "y en Advanced settings escoge Python 3.14.\n"
            "Este proyecto es preventivo y no garantiza que un mensaje sea seguro.\n",
            encoding="utf-8",
        )
        # Comprobar que no se filtró el corpus, archivos de entorno ni datos temporales.
        excluded = {".env", ".venv", "__pycache__"}
        for f in stage.rglob("*"):
            if f.is_file() and (f.name in excluded or any(part in excluded for part in f.parts)):
                raise RuntimeError(f"La publicación contiene un archivo no permitido: {f}")
            if f.is_file() and f.parent == stage / "data/raw" and f.name != ".gitkeep":
                raise RuntimeError("La publicación contiene el CSV original; se bloqueó por privacidad.")
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(stage, target)
        if zip_target.exists():
            zip_target.unlink()
        with zipfile.ZipFile(zip_target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for f in sorted(stage.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(stage).as_posix())
    if verbose:
        print("CARPETA PARA GITHUB:", target)
        print("ZIP PARA GITHUB:", zip_target)
        print("CÓMO PUBLICAR: usa app/app.py y Python 3.14 en Streamlit Community Cloud.")
        print("IMPORTANTE: el archivo CSV original NO se incluyó; sí se incluyeron el modelo y las evidencias.")
    return target, zip_target


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Prepara paquete seguro para GitHub + Streamlit")
    ap.add_argument("--verificar", action="store_true")
    args = ap.parse_args()
    if args.verificar:
        check_ready(verbose=True)
    else:
        package_release(verbose=True)
