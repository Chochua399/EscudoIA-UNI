from pathlib import Path
import pandas as pd
import pytest
from src.data.make_dataset import normalize_text,load_spaphish
from src.features.build_features import detect_signals
from src.models.predict_model import analyze_message

class DummyModel:
    def predict(self, inputs):return [1]
    def predict_proba(self, inputs):return [[0.15,0.85]]

def test_normalize_preserves_url_and_numbers():
    assert normalize_text('  Hola   https://sitio.example  123  ') == 'Hola https://sitio.example 123'

def test_signals_do_not_open_links():
    result=detect_signals('¡Urgente! Verifique su contraseña en https://invalido.example')
    assert 'Urgencia o presión' in result
    assert any('enlace' in x for x in result)

def test_prediction_fake_model():
    result=analyze_message('Su cuenta será suspendida mañana. Confirme sus datos.',model=DummyModel())
    assert result['etiqueta']==1 and result['riesgo'].startswith('Alto')

def test_short_input_rejected():
    with pytest.raises(ValueError):analyze_message('Hola',model=DummyModel())

def test_import_clean_and_dedupe(tmp_path: Path):
    file=tmp_path/'toy.csv'
    pd.DataFrame({'subject':['A','A','B','C'],'body':['estafa uno','estafa uno','mensaje normal','texto distinto'],
                  'Label':[1,1,0,0]}).to_csv(file,sep=';',index=False)
    df,meta=load_spaphish(file)
    assert len(df)==3 and meta['duplicados_descartados']==1
