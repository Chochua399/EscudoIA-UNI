"""Pruebas con datos artificiosos; JAMÁS representan métricas científicas SpaPhish."""
from pathlib import Path
import json
import pandas as pd
import pytest
from src.data.make_dataset import identify_file, load_spaphish, prepare
from src.models.train_model import train
from src.models.predict_model import analyze_message, educational_signals_only, load_model
from src.visualization.visualize import make_eda
from src.features.build_features import detect_signals


def create_synthetic_csv(folder):
    """Registros ÚNICAMENTE para comprobar que el código corre de punta a punta."""
    folder.mkdir(exist_ok=True, parents=True)
    descriptors = [
        "azul", "rojo", "verde", "dorado", "violeta", "gris", "celeste", "morado",
        "naranja", "blanco", "negro", "marron", "claro", "oscuro", "rapido", "lento",
        "marino", "solar", "lunar", "urbano", "rural", "valle", "monte", "playa",
        "rio", "bosque", "costa", "prado", "llano", "isla", "norte", "sur",
        "este", "oeste", "centro", "campo", "pueblo", "ciudad", "alfa", "beta",
    ]
    rows = []
    for i in range(36):
        code = descriptors[i]
        rows.append({"subject": f"Cuenta bancaria {code} activo",
                     "body": f"URGENTE: confirma tu contraseña y clave de acceso para tu cuenta {code}. Entra a hxxps://sitio[.]example/actualiza.",
                     "Label": 1})
        rows.append({"subject": f"Reunión de grupo {code}",
                     "body": f"Hola compañeros, la reunión {code} es mañana en el salón de la facultad. Llevar apuntes y materiales de estudio.",
                     "Label": 0})
    file = folder / "datos_SINTETICOS_SOLO_TEST.csv"
    pd.DataFrame(rows).to_csv(file, sep=";", index=False, encoding="utf-8")
    return file


def test_full_training_and_predictions(tmp_path):
    csv = create_synthetic_csv(tmp_path / "raw")
    summary = train(csv, quick=True, model_dir=tmp_path / "models", report_dir=tmp_path / "reports", cv_folds=3)
    assert len(summary["comparacion_validacion"]) == 3
    assert summary["division"]["sin_solapamiento_de_grupos"] is True
    assert "f1_phishing" in summary["test_final"]
    model_path = tmp_path / "models" / "modelo_estafas_v1.joblib"
    assert model_path.exists()
    loaded = load_model(model_path)
    result = analyze_message(
        "URGENTE, su cuenta va a bloquearse. Introduzca contraseña y código de verificación.",
        model=loaded, metadata={"modelo": "test sintético"},
    )
    assert result["etiqueta"] in (0, 1)
    assert 0 <= result["puntaje_modelo"] <= 1
    assert (tmp_path / "reports" / "figures" / "matriz_confusion.png").exists()
    assert (tmp_path / "reports" / "RESUMEN_REAL_PARA_INFORME.md").exists()
    assert (tmp_path / "reports" / "metrics" / "predicciones_test_sin_texto.csv").exists()
    assert (tmp_path / "reports" / "metrics" / "analisis_errores_sin_texto.json").exists()
    assert "brier_score" in summary["test_final"]
    assert "accuracy_cv" in summary["comparacion_validacion"]["SVM lineal"]
    assert (tmp_path / "reports" / "metrics" / "busqueda_3.csv").exists()


def test_eda_outputs_are_created(tmp_path):
    csv = create_synthetic_csv(tmp_path / "raw")
    report = make_eda(csv, tmp_path / "eda")
    assert report["filas_preparadas"] == 72
    assert (tmp_path / "eda" / "01_distribucion_clases.png").exists()
    assert (tmp_path / "eda" / "señales_por_clase.csv").exists()
    assert (tmp_path / "eda" / "04_boxplot_longitud.png").exists()
    assert (tmp_path / "eda" / "05_valores_ausentes.png").exists()
    assert (tmp_path / "eda" / "top_terminos_por_clase.csv").exists()


def test_schema_must_include_label_subject_body(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("texto;clase\nHola;1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="subject"):
        load_spaphish(p)


def test_conflict_labels_for_same_text_dropped(tmp_path):
    p = tmp_path / "conflict.csv"
    pd.DataFrame({
        "subject": ["A", "A", "B", "C", "D", "E"],
        "body": ["misma frase", "misma frase", "texto phish", "texto legit", "otro phish", "otro legit"],
        "Label": [0, 1, 1, 0, 1, 0],
    }).to_csv(p, sep=";", index=False)
    df, audit = load_spaphish(p)
    assert audit["filas_conflicto_descartadas"] == 2
    assert len(df) == 4


def test_rule_demo_is_not_ai():
    demo = educational_signals_only("Su cuenta será suspendida urgente. Confirme sus datos bancarios.")
    assert "NO ES PREDICCIÓN DE IA" in demo["modo"]
    assert demo["senales"]


def test_dataset_with_000_and_001_labels(tmp_path):
    p = tmp_path / "labels.csv"
    pd.DataFrame({"subject": [f"Tema {i}" for i in range(12)],
                  "body": [f"mensaje texto {i} color amarillo" for i in range(12)],
                  "Label": ["000" if i < 6 else "001" for i in range(12)]}).to_csv(p, sep=";", index=False)
    df, _ = load_spaphish(p)
    assert set(df["label"]) == {0, 1}
