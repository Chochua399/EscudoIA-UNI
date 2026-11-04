"""Pruebas complementarias: compatibilidad estructural y trazabilidad."""
from pathlib import Path
import json
import pandas as pd
import pytest

from src.data.make_dataset import read_csv, load_spaphish, normalize_text
from src.features.build_features import signal_summary
from src.models.train_model import model_candidates, metrics_for


def test_reader_csv_with_bom_commas_and_expected_label(tmp_path):
    f = tmp_path / 'corpus.csv'
    f.write_text('\ufeffsubject,body,Label\n"Saludo","En clase aprendemos español",000\n'
                 '"Alerta","Confirmar la contraseña urgentemente",001\n', encoding='utf-8')
    df = read_csv(f)
    assert {'subject','body','label'}.issubset(df.columns)
    processed, audit = load_spaphish(f)
    assert processed['label'].tolist() == [0,1]
    assert audit['filas_preparadas'] == 2


def test_metrics_confusion_error_orders():
    result = metrics_for([0,0,1,1],[0,1,0,1],[0.2,0.8,0.4,0.9])
    assert result['TN'] == 1 and result['FP'] == 1
    assert result['FN'] == 1 and result['TP'] == 1
    assert result['f1_phishing'] == pytest.approx(.5)
    assert 'roc_auc' in result


def test_hyperparameter_search_covers_theory():
    models = model_candidates(quick=False)
    assert set(models) == {'Naive Bayes Multinomial','Regresión Logística','SVM lineal'}
    for pipeline, params in models.values():
        assert 'tfidf' in pipeline.named_steps
        assert set(params['tfidf__ngram_range']) == {(1,1),(1,2)}
        assert len(params['tfidf__max_df']) > 1
        assert len(params['tfidf__sublinear_tf']) == 2


def test_cleaning_preserves_phishing_evidence():
    text = normalize_text('  SU  CUENTA  tiene C$ 150    https://sitio.example/abc  ')
    result = signal_summary(text)
    assert result['contiene_enlace'] is True
    assert '150' in text and 'C$' in text


def test_project_directories_and_manual_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root/'data/raw').is_dir()
    assert (root/'models').is_dir()
    assert (root/'README.md').is_file()
