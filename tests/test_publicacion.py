"""Pruebas de la preparación segura de una entrega pública."""
import json
from pathlib import Path
import zipfile
import pytest

from src.release.package_github import check_ready, package_release


def test_no_publicar_sin_modelo(tmp_path):
    with pytest.raises(RuntimeError, match="Faltan resultados"):
        package_release(root=tmp_path, output=tmp_path)


def test_publicacion_no_copia_datos_originales(tmp_path):
    # Copia local de *artefactos de prueba* y datos sintéticos preparados
    # en test_end_to_end.py. No forman parte de la publicación final.
    from src.models.train_model import train
    from src.visualization.visualize import make_eda
        # Mantener salida de test contenida en tmp_path, sin interferir con el proyecto.
    test_root = tmp_path / "testcode"
    test_root.mkdir()
    project_root = Path(__file__).resolve().parents[1]
    import shutil
    for directory in ("src", "app", "docs", "tests", ".streamlit", "notebooks"):
        shutil.copytree(project_root / directory, test_root / directory, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    for f in ("main.py", "requirements.txt", "README.md", "LICENSE", ".python-version"):
        shutil.copy2(project_root / f, test_root / f)
    from src.data.make_dataset import load_spaphish
    import pandas as pd
    raw_folder = test_root / "data/raw"
    raw_folder.mkdir(parents=True)
    rows = []
    for i in range(36):
        rows.append({"subject": f"URGENTE clave {chr(65+i%26)} sector {i}",
                     "body": f"Bloquearon cuenta, solicita contraseña verificando referencia {i} cliente", "Label": 1})
        rows.append({"subject": f"Reunión grupo {chr(65+i%26)} sección {i}",
                     "body": f"Hola, reunión de clase y materiales entregables profesor referencia {i}", "Label": 0})
    csv = raw_folder / "SOLO_TEST_SINTETICO.csv"
    pd.DataFrame(rows).to_csv(csv, sep=";", index=False)
    _, stats = load_spaphish(csv)
    # test synthetic: use strict=False; command for users ALWAYS uses strict=True.
    local_audit = test_root / "reports/metrics/auditoria_dataset.json"
    local_audit.parent.mkdir(parents=True,exist_ok=True)
    local_audit.write_text(json.dumps(stats,ensure_ascii=False),encoding="utf-8")
    train(csv, quick=True, model_dir=test_root / "models", report_dir=test_root / "reports", cv_folds=3)
    make_eda(csv, test_root / "reports/eda")
    # El modelo entrena con el mismo CSV sintético por diseño; el helper bloquea publicar por CLI.
    with pytest.raises(RuntimeError, match="no parece|cinco pliegues"):
        check_ready(root=test_root)
    release_dir, release_zip = package_release(root=test_root,output=tmp_path,strict=False)
    assert release_dir.is_dir() and release_zip.is_file()
    assert (release_dir / "models/modelo_estafas_v1.joblib").is_file()
    assert (release_dir / "reports/metrics/resultados.json").is_file()
    assert (release_dir / "deployment_manifest.json").is_file()
    assert not list((release_dir / "data/raw").glob("*.csv"))
    assert not list(release_dir.rglob("*.env"))
    with zipfile.ZipFile(release_zip) as archive:
        names = archive.namelist()
        assert "app/app.py" in names
        assert "models/modelo_estafas_v1.joblib" in names
        assert not any(x.startswith("data/raw/") and x.endswith(".csv") for x in names)
