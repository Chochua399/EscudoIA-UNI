"""Gráficos y resúmenes EDA a partir de los datos locales reales."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src.config import EDA, ensure_dirs
from src.data.make_dataset import identify_file, load_spaphish, read_csv
from src.features.build_features import LINK_RE, SIGNAL_RULES, detect_signals
from sklearn.feature_extraction.text import CountVectorizer


def make_eda(input_path=None, out_dir=None):
    ensure_dirs()
    path = identify_file(input_path)
    df, audit = load_spaphish(path)
    raw_df = read_csv(path)
    output = Path(out_dir) if out_dir else EDA
    output.mkdir(parents=True, exist_ok=True)
    df = df.assign(caracteres=df["text"].str.len(), palabras=df["text"].str.split().str.len())
    counts = df["label"].value_counts().reindex([0, 1], fill_value=0)
    fig, ax = plt.subplots(figsize=(7.4, 4.3))
    bars = ax.bar(["Legítimos (0)", "Phishing (1)"], counts, color=["#2563eb", "#d97706"])
    ax.bar_label(bars, padding=5)
    ax.set_ylabel("Número de mensajes")
    ax.set_title("Distribución de clases del archivo analizado")
    fig.tight_layout()
    fig.savefig(output / "01_distribucion_clases.png", dpi=165)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.4))
    bins = np.linspace(0, np.percentile(df["palabras"], 98) + 1, 26)
    for label, title, color in [(0, "Legítimos", "#2563eb"), (1, "Phishing", "#d97706")]:
        ax.hist(df.loc[df.label == label, "palabras"], bins=bins, alpha=.62, label=title, color=color)
    ax.set_title("Distribución de longitud (palabras) por clase")
    ax.set_xlabel("Palabras por mensaje")
    ax.set_ylabel("Registros")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "02_longitud_palabras.png", dpi=165)
    plt.close(fig)

    label_signals = {}
    for name, pattern in SIGNAL_RULES.items():
        label_signals[name] = [int(df.loc[df.label == k, "text"].str.contains(pattern, case=False, regex=True).sum()) for k in (0, 1)]
    label_signals["Presencia de enlaces"] = [int(df.loc[df.label == k, "text"].str.contains(LINK_RE, regex=True).sum()) for k in (0, 1)]
    pd.DataFrame(label_signals, index=["legitimos_0", "phishing_1"]).T.to_csv(output / "señales_por_clase.csv", encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(9, 5))
    names = list(label_signals)
    y = np.arange(len(names))
    ax.barh(y - 0.19, [label_signals[k][0] / max(counts[0], 1) * 100 for k in names], 0.36, color="#2563eb", label="Legítimos")
    ax.barh(y + 0.19, [label_signals[k][1] / max(counts[1], 1) * 100 for k in names], 0.36, color="#d97706", label="Phishing")
    ax.set_yticks(y, names)
    ax.invert_yaxis()
    ax.set_xlabel("Porcentaje de mensajes de la clase")
    ax.set_title("Señales descriptivas (no equivalen a fraude)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(output / "03_indicadores_por_clase.png", dpi=165)
    plt.close(fig)

    # Análisis adicional requerido por la guía: boxplot, valores faltantes,
    # número de URLs y términos frecuentes. SOLO exploración descriptiva.
    fig, ax = plt.subplots(figsize=(8.3, 4.4))
    ax.boxplot([df.loc[df.label == i, "palabras"].to_numpy() for i in (0, 1)],
               tick_labels=["Legítimos", "Phishing"], showfliers=False)
    ax.set_title("Distribución de longitud (sin valores atípicos dibujados)")
    ax.set_ylabel("Palabras por mensaje")
    fig.tight_layout()
    fig.savefig(output / "04_boxplot_longitud.png", dpi=165)
    plt.close(fig)

    missing = raw_df.isna().mean().sort_values(ascending=False).head(15) * 100
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.barh(missing.index[::-1], missing.values[::-1], color="#1b6478")
    ax.set_xlabel("% de valores ausentes en el archivo original")
    ax.set_title("Calidad de datos — primeras 15 variables")
    fig.tight_layout()
    fig.savefig(output / "05_valores_ausentes.png", dpi=165)
    plt.close(fig)
    raw_df.isna().sum().rename("nulos").to_csv(output / "nulos_por_variable.csv", encoding="utf-8-sig")

    df["url_texto"] = df["text"].map(lambda t: len(LINK_RE.findall(t)))
    fig, ax = plt.subplots(figsize=(8.2, 4.7))
    by_class = [df.loc[df.label == j, "url_texto"].clip(upper=5).to_numpy() for j in (0,1)]
    ax.hist(by_class, bins=np.arange(-0.5, 6.5, 1), alpha=.65, label=["Legítimos", "Phishing"],
            color=["#2563eb", "#d97706"])
    ax.set_xticks(range(6), ["0","1","2","3","4","5+"])
    ax.set_xlabel("Indicadores de URL detectados en el texto (5 o más agrupados)")
    ax.set_ylabel("Mensajes")
    ax.set_title("Número de enlaces: indicador descriptivo, no prueba de fraude")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "06_enlaces_por_clase.png", dpi=165)
    plt.close(fig)

    top_rows = []
    for label, class_name in [(0,"Legítimo"),(1,"Phishing")]:
        texts = df.loc[df.label == label, "text"].astype(str).tolist()
        try:
            cv = CountVectorizer(ngram_range=(1,2), max_features=1800, strip_accents="unicode")
            X = cv.fit_transform(texts)
            counts = np.asarray(X.sum(axis=0)).ravel()
            for pos in np.argsort(counts)[::-1][:15]:
                top_rows.append({"clase":class_name,"termino":cv.get_feature_names_out()[pos],
                                 "frecuencia":int(counts[pos])})
        except ValueError:
            continue
    pd.DataFrame(top_rows, columns=["clase","termino","frecuencia"]).to_csv(
        output / "top_terminos_por_clase.csv", index=False, encoding="utf-8-sig")
    if top_rows:
        fig, ax = plt.subplots(figsize=(9.5, 6))
        data_top = [r for r in top_rows if r["clase"] == "Phishing"][:12]
        ax.barh([r["termino"] for r in data_top][::-1],
                [r["frecuencia"] for r in data_top][::-1], color="#d97706")
        ax.set_title("Términos más comunes en phishing (EDA, no modelo final)")
        ax.set_xlabel("Frecuencia")
        fig.tight_layout()
        fig.savefig(output / "07_terminos_phishing.png", dpi=165)
        plt.close(fig)

    result = {
        **audit,
        "valores_ausentes_originales_por_variable": {str(k): int(v) for k,v in raw_df.isna().sum().items()},
        "media_senales_url_en_texto_por_clase": {str(k):round(float(v),3) for k,v in df.groupby("label")["url_texto"].mean().items()},
        "longitud_caracteres_por_clase": df.groupby("label")["caracteres"].describe().round(2).to_dict(orient="index"),
        "longitud_palabras_por_clase": df.groupby("label")["palabras"].describe().round(2).to_dict(orient="index"),
        "figuras": ["01_distribucion_clases.png", "02_longitud_palabras.png", "03_indicadores_por_clase.png",
                    "04_boxplot_longitud.png", "05_valores_ausentes.png", "06_enlaces_por_clase.png", "07_terminos_phishing.png"],
        "nota": "Los gráficos describen los datos efectivamente disponibles, no la validez del modelo.",
    }
    (output / "eda_resumen.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("EDA generado en", output)
    return result


def main():
    p = argparse.ArgumentParser(description="Análisis exploratorio del dataset SpaPhish")
    p.add_argument("--input", help="CSV oficial")
    args = p.parse_args()
    make_eda(args.input)


if __name__ == "__main__":
    main()
