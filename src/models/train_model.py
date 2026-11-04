"""Comparación reproducible, CV estratificada por plantillas y test reservado."""
from __future__ import annotations

import argparse
import json
import hashlib
import sys
import time
from importlib import metadata as package_metadata
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import __version__ as sklearn_version
from sklearn.calibration import CalibratedClassifierCV
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, average_precision_score,
    classification_report, RocCurveDisplay, PrecisionRecallDisplay,
    brier_score_loss, ConfusionMatrixDisplay,
)
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, StratifiedGroupKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from src.config import MODELS, METRICS, FIGURES, REPORTS, MODEL_FILE, MODEL_META, ensure_dirs
from src.data.make_dataset import load_spaphish, identify_file
from src.features.build_features import detect_signals, LINK_RE

SEED = 42


def model_candidates(quick=False):
    def tfidf():
        return TfidfVectorizer(
            ngram_range=(1, 2), min_df=1, max_df=0.95,
            sublinear_tf=True, strip_accents="unicode", lowercase=True,
        )

    tfidf_grid = {
        "tfidf__ngram_range": [(1, 1), (1, 2)] if not quick else [(1, 2)],
        "tfidf__min_df": [1, 2, 3] if not quick else [1],
        "tfidf__max_df": [0.90, 0.95, 1.0] if not quick else [0.95],
        "tfidf__sublinear_tf": [True, False] if not quick else [True],
    }
    return {
        "Naive Bayes Multinomial": (
            Pipeline([("tfidf", tfidf()), ("model", MultinomialNB())]),
            {**tfidf_grid, "model__alpha": [0.1, 0.5, 1.0] if not quick else [1.0]},
        ),
        "Regresión Logística": (
            Pipeline([("tfidf", tfidf()), ("model", LogisticRegression(max_iter=2000, random_state=SEED))]),
            {**tfidf_grid, "model__C": [0.1, 1.0, 5.0, 10.0] if not quick else [1.0],
             "model__class_weight": [None, "balanced"] if not quick else [None]},
        ),
        "SVM lineal": (
            Pipeline([("tfidf", tfidf()), ("model", LinearSVC(random_state=SEED))]),
            {**tfidf_grid, "model__C": [0.1, 1.0, 5.0] if not quick else [1.0],
             "model__class_weight": [None, "balanced"] if not quick else [None]},
        ),
    }


def metrics_for(y, predictions, score=None) -> dict:
    y = np.asarray(y)
    pred = np.asarray(predictions)
    matrix = confusion_matrix(y, pred, labels=[0, 1])
    data = {
        "accuracy": float(accuracy_score(y, pred)),
        "precision_phishing": float(precision_score(y, pred, zero_division=0)),
        "recall_phishing": float(recall_score(y, pred, zero_division=0)),
        "f1_phishing": float(f1_score(y, pred, zero_division=0)),
        "matriz_confusion_orden_0_1": matrix.tolist(),
        "TN": int(matrix[0, 0]), "FP": int(matrix[0, 1]),
        "FN": int(matrix[1, 0]), "TP": int(matrix[1, 1]),
    }
    if score is not None and len(set(y)) == 2:
        data["roc_auc"] = float(roc_auc_score(y, score))
        data["average_precision"] = float(average_precision_score(y, score))
    return data


def split_by_groups(df, folds=5):
    y = df["label"].to_numpy()
    groups = df["group"].to_numpy()
    splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=SEED)
    candidates = []
    for train_idx, test_idx in splitter.split(df["text"], y, groups):
        if len(set(y[train_idx])) == 2 and len(set(y[test_idx])) == 2:
            balance_error = abs(np.mean(y[test_idx]) - np.mean(y))
            size_error = abs(len(test_idx) / len(df) - 1 / folds)
            candidates.append((balance_error + size_error * 0.5, train_idx, test_idx))
    if not candidates:
        raise ValueError("No fue posible separar entrenamiento/prueba por grupos con ambas clases. Revise el dataset.")
    _, train_idx, test_idx = sorted(candidates, key=lambda x: x[0])[0]
    return train_idx, test_idx


def _plots(y_test, y_pred, score, figures):
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(6.2, 4.8))
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0, 1], ["Legítimo (0)", "Phishing (1)"])
    ax.set_yticks([0, 1], ["Legítimo (0)", "Phishing (1)"])
    ax.set_xlabel("Clase predicha")
    ax.set_ylabel("Clase real")
    ax.set_title("Matriz de confusión — test reservado")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=16)
    fig.tight_layout()
    fig.savefig(figures / "matriz_confusion.png", dpi=175)
    plt.close(fig)
    if score is not None:
        fig, ax = plt.subplots(figsize=(6, 5))
        RocCurveDisplay.from_predictions(y_test, score, ax=ax, name="Modelo final")
        ax.plot([0, 1], [0, 1], linestyle="--", color="gray")
        ax.set_title("Curva ROC — test reservado")
        fig.tight_layout()
        fig.savefig(figures / "curva_roc.png", dpi=175)
        plt.close(fig)
        fig, ax = plt.subplots(figsize=(6, 5))
        PrecisionRecallDisplay.from_predictions(y_test, score, ax=ax, name="Modelo final")
        ax.set_title("Precisión-Recall — test reservado")
        fig.tight_layout()
        fig.savefig(figures / "curva_precision_recall.png", dpi=175)
        plt.close(fig)


def _top_terms(pipeline, topn=15):
    """Términos globales descriptivos del modelo entrenado; NO explicaciones causales."""
    tfidf = pipeline.named_steps["tfidf"]
    model = pipeline.named_steps["model"]
    vocab = tfidf.get_feature_names_out()
    if hasattr(model, "coef_"):
        weights = np.asarray(model.coef_[0])
    elif hasattr(model, "feature_log_prob_"):
        weights = np.asarray(model.feature_log_prob_[1] - model.feature_log_prob_[0])
    else:
        return {"phishing": [], "legitimo": []}
    most = np.argsort(weights)
    return {
        "phishing": [{"termino": str(vocab[i]), "peso": float(weights[i])} for i in most[-topn:][::-1]],
        "legitimo": [{"termino": str(vocab[i]), "peso": float(weights[i])} for i in most[:topn]],
    }


def train(input_path=None, *, quick=False, model_dir=None, report_dir=None, cv_folds=None):
    ensure_dirs()
    csv_path = identify_file(input_path)
    df, data_info = load_spaphish(csv_path)
    folds = cv_folds or (3 if quick else 5)
    if min(df["label"].value_counts()) < folds + 2:
        raise ValueError(f"Se requieren más ejemplos por clase para usar CV de {folds} pliegues.")
    model_dir = Path(model_dir) if model_dir else MODELS
    report_dir = Path(report_dir) if report_dir else REPORTS
    metrics_dir, figures_dir = report_dir / "metrics", report_dir / "figures"
    for folder in (model_dir, metrics_dir, figures_dir):
        folder.mkdir(parents=True, exist_ok=True)
    train_idx, test_idx = split_by_groups(df)
    train_data = df.iloc[train_idx].copy()
    test_data = df.iloc[test_idx].copy()
    X_train, y_train = train_data["text"], train_data["label"]
    X_test, y_test = test_data["text"], test_data["label"]
    group_train = train_data["group"]
    if set(group_train).intersection(set(test_data["group"])):
        raise AssertionError("Fuga de plantillas entre entrenamiento y prueba.")
    cv = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=SEED)
    splits = list(cv.split(X_train, y_train, groups=group_train))
    for a, b in splits:
        if y_train.iloc[a].nunique() != 2 or y_train.iloc[b].nunique() != 2:
            raise ValueError("Un pliegue de validación carece de clase. Amplíe el conjunto de entrenamiento.")
    summary = {
        "estado": "ENTRENAMIENTO_REAL_CON_CSV_LOCAL",
        "fuente_archivo": csv_path.name,
        "dataset": data_info,
        "ejecutado_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "scikit_learn": sklearn_version,
        "bibliotecas": {name: package_metadata.version(name) for name in
                        ("numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "joblib")},
        "seed": SEED,
        "division": {"entrenamiento": len(train_idx), "test_reservado": len(test_idx),
                     "entrenamiento_phishing": int(y_train.sum()), "test_phishing": int(y_test.sum()),
                     "sin_solapamiento_de_grupos": True},
        "validacion_cruzada_pliegues": folds,
        "busqueda": "GridSearchCV exhaustivo en modo rápido; RandomizedSearchCV de 18 configuraciones por modelo en modo completo",
        "comparacion_validacion": {},
        "nota_metodologica": "Los candidatos se seleccionan exclusivamente con CV en train. El test se evalúa solo con el ganador final.",
        "verificacion_fuente": "El software valida columnas y etiquetas, pero NO puede certificar que un archivo CSV local sea la edición oficial SpaPhish. Verifique DOI y SHA-256 del archivo descargado.",
    }
    searches = {}
    print(f"CSV: {csv_path.name} | muestras limpias: {len(df)} | train={len(train_idx)}, test={len(test_idx)}")
    for name, (model, params) in model_candidates(quick).items():
        print(f"\nEntrenando {name}...")
        start = time.perf_counter()
        search_type = GridSearchCV if quick else RandomizedSearchCV
        search_args = {} if quick else {"n_iter": 18, "random_state": SEED}
        search = search_type(
            model, params, scoring={"f1": "f1", "recall": "recall", "precision": "precision", "accuracy": "accuracy"},
            refit="f1", cv=splits, n_jobs=1, error_score="raise", return_train_score=False,
            **search_args
        )
        search.fit(X_train, y_train)
        i = search.best_index_
        summary["comparacion_validacion"][name] = {
            "f1_cv": float(search.cv_results_["mean_test_f1"][i]),
            "desviacion_f1_cv": float(search.cv_results_["std_test_f1"][i]),
            "recall_cv": float(search.cv_results_["mean_test_recall"][i]),
            "precision_cv": float(search.cv_results_["mean_test_precision"][i]),
            "accuracy_cv": float(search.cv_results_["mean_test_accuracy"][i]),
            "parametros": search.best_params_,
            "duracion_segundos": round(time.perf_counter() - start, 2),
        }
        searches[name] = search
        pd.DataFrame(search.cv_results_).to_csv(
            metrics_dir / f"busqueda_{list(model_candidates(quick)).index(name)+1}.csv", index=False, encoding="utf-8-sig")
        summary["comparacion_validacion"][name]["configuraciones_evaluadas"] = int(len(search.cv_results_["params"]))
        summary["comparacion_validacion"][name]["tipo_busqueda"] = "GridSearchCV" if quick else "RandomizedSearchCV"
        print(f"  F1-CV={search.best_score_:.3f}")

    ordered = sorted(
        searches, key=lambda name: (
            summary["comparacion_validacion"][name]["f1_cv"],
            summary["comparacion_validacion"][name]["recall_cv"],
        ), reverse=True,
    )
    best_name = ordered[0]
    # Si la diferencia F1 es mínima, preferir Regresión Logística por sencillez.
    logname = "Regresión Logística"
    if (best_name != logname and
        summary["comparacion_validacion"][best_name]["f1_cv"] -
        summary["comparacion_validacion"][logname]["f1_cv"] <= 0.01):
        best_name = logname
    winner_pipe = searches[best_name].best_estimator_
    top_terms = _top_terms(winner_pipe)
    final_model = winner_pipe
    # Calibrar sólo con train y sin repetir grupos de plantillas en pliegues.
    # Los splits son índices relativos al entrenamiento y separan las plantillas.
    final_model = CalibratedClassifierCV(estimator=winner_pipe, method="sigmoid", cv=splits)
    final_model.fit(X_train, y_train)
    summary["calibracion"] = (
        f"Calibración sigmoide (Platt) con {folds} pliegues agrupados usando solo entrenamiento. "
        "Las probabilidades NO demuestran seguridad; los umbrales siguen provisionales."
    )
    predictions = final_model.predict(X_test)
    probabilities = None
    if hasattr(final_model, "predict_proba"):
        classes = list(final_model.classes_)
        probabilities = final_model.predict_proba(X_test)[:, classes.index(1)]
    baseline = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
    summary["baseline_test"] = metrics_for(y_test, baseline.predict(X_test))
    summary["modelo_seleccionado_por_cv"] = best_name
    summary["test_final"] = metrics_for(y_test, predictions, probabilities)
    if probabilities is not None:
        summary["test_final"]["brier_score"] = float(brier_score_loss(y_test, probabilities))
    summary["classification_report_test"] = classification_report(
        y_test, predictions, labels=[0, 1], target_names=["legítimo", "phishing"], zero_division=0,
    )
    summary["umbrales_riesgo"] = {"bajo_hasta": 0.35, "alto_desde": 0.70,
        "estado": "provisionales; NO optimizados ni validados para despliegue real"}
    summary["nota_generalizacion"] = (
        "Los resultados miden desempeño sobre una partición de correos del CSV aportado, "
        "no sobre WhatsApp, SMS, Nicaragua ni campañas nuevas."
    )
    (metrics_dir / "resultados.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (metrics_dir / "versiones_entorno.txt").write_text(
        "Python: " + summary["python"] + "\n" +
        "\n".join(f"{name}=={version}" for name, version in summary["bibliotecas"].items()) + "\n",
        encoding="utf-8")
    (metrics_dir / "terminos_globales.json").write_text(json.dumps(top_terms, indent=2, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame([
        {"modelo": name, **{k: v for k, v in values.items() if isinstance(v, (float, int))}}
        for name, values in summary["comparacion_validacion"].items()
    ]).to_csv(metrics_dir / "comparacion_validacion.csv", index=False, encoding="utf-8-sig")
    pred_test = pd.DataFrame({
        "id_anonimo": [hashlib.sha256(t.encode("utf-8")).hexdigest()[:16] for t in X_test],
        "real": y_test.to_numpy(), "predicho": predictions,
        "puntaje": probabilities if probabilities is not None else [np.nan] * len(predictions),
    })
    pred_test.to_csv(metrics_dir / "predicciones_test_sin_texto.csv", index=False)
    # Revisión agregada de errores: no publica texto privado del corpus.
    analysis = {"descripcion": "Características agregadas de FP/FN, sin incluir mensajes",
                "total_falsos_negativos": int(((y_test.to_numpy()==1) & (predictions==0)).sum()),
                "total_falsos_positivos": int(((y_test.to_numpy()==0) & (predictions==1)).sum()),
                "grupos": {}}
    for key, actual, predicted in [("falsos_negativos", 1, 0), ("falsos_positivos", 0, 1),
                                   ("aciertos_phishing", 1, 1), ("aciertos_legitimos", 0, 0)]:
        chosen = X_test[(y_test.to_numpy() == actual) & (predictions == predicted)]
        texts = chosen.tolist()
        analysis["grupos"][key] = {
            "cantidad": len(texts),
            "longitud_media_caracteres": round(sum(map(len,texts)) / len(texts),2) if texts else None,
            "mensajes_con_enlace": sum(bool(LINK_RE.search(txt)) for txt in texts),
            "senales_frecuentes": {str(name): int(n) for name, n in pd.Series([signal for txt in texts for signal in detect_signals(txt)]).value_counts().head(8).items()}
        }
    (metrics_dir / "analisis_errores_sin_texto.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    model_file = model_dir / "modelo_estafas_v1.joblib"
    joblib.dump(final_model, model_file)
    meta_file = model_dir / "metadata_modelo.json"
    meta = {
        "modelo": best_name, "creacion_utc": summary["ejecutado_utc"],
        "hash_dataset": data_info["sha256_archivo_original"],
        "dataset_archivo": csv_path.name,
        "metodo": "TF-IDF con clasificador supervisado", "clases": {"0": "legítimo", "1": "phishing"},
        "f1_cv": summary["comparacion_validacion"][best_name]["f1_cv"],
        "f1_test": summary["test_final"]["f1_phishing"],
        "umbrales_riesgo": summary["umbrales_riesgo"],
        "brier_score_test": summary["test_final"].get("brier_score"),
        "advertencia": "Riesgo orientativo; no verifica el destino de enlaces ni al remitente.",
        "version_sklearn_entrenamiento": sklearn_version,
    }
    meta_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    _plots(y_test, predictions, probabilities, figures_dir)
    rows = ["# Resultados medidos para el informe académico", "", "**Datos reales de una ejecución del programa.**", "",
        f"- Archivo CSV: `{csv_path.name}`", f"- SHA-256: `{data_info['sha256_archivo_original']}`",
        f"- Mensajes tras limpieza: {len(df)}; entrenamiento: {len(train_idx)}; prueba reservada: {len(test_idx)}.",
        f"- Modelo elegido según validación cruzada: **{best_name}**.",
        f"- F1 de phishing en validación cruzada: **{meta['f1_cv']:.4f}**.",
        f"- F1 de phishing en test reservado: **{meta['f1_test']:.4f}**.",
        f"- Recall phishing en test: **{summary['test_final']['recall_phishing']:.4f}**.",
        f"- Precisión phishing en test: **{summary['test_final']['precision_phishing']:.4f}**.",
        f"- Accuracy en test: **{summary['test_final']['accuracy']:.4f}**.",
        f"- ROC-AUC en test: **{summary['test_final'].get('roc_auc', float('nan')):.4f}**.",
        f"- Brier score en test: **{summary['test_final'].get('brier_score', float('nan')):.4f}**.",
        f"- Falsos negativos: **{summary['test_final']['FN']}**; falsos positivos: **{summary['test_final']['FP']}**.",
        "", "## Reglas de interpretación", "", summary["nota_generalizacion"],
        "Los umbrales bajo/medio/alto son provisionales y no una garantía de seguridad.",
        "No usar cifras de pruebas sintéticas como resultados de SpaPhish.", "",
        "## Evidencias", "", "- `reports/metrics/resultados.json`", "- `reports/metrics/comparacion_validacion.csv`",
        "- `reports/figures/matriz_confusion.png`", "- `reports/figures/curva_roc.png`",
        "- `reports/figures/curva_precision_recall.png`", "- `reports/metrics/analisis_errores_sin_texto.json`", "",
    ]
    (report_dir / "RESUMEN_REAL_PARA_INFORME.md").write_text("\n".join(rows), encoding="utf-8")
    print("\nMODELO ELEGIDO POR VALIDACIÓN:", best_name)
    print("\n", summary["classification_report_test"])
    print("Modelo guardado en", model_file)
    print("Métricas y figuras guardadas en", report_dir)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Entrena tres clasificadores sobre SpaPhish")
    parser.add_argument("--input", help="Ruta al CSV. Si se omite, usa el único CSV en data/raw")
    parser.add_argument("--rapido", action="store_true", help="CV 3-fold y menos parámetros, para una prueba rápida")
    args = parser.parse_args()
    train(args.input, quick=args.rapido)


if __name__ == "__main__":
    main()
