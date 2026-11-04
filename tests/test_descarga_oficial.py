"""Pruebas puramente locales; jamás contactan el servidor Mendeley."""
from src.data.download_official import find_csv_entry
import pytest


def test_archivo_oficial_se_identifica_en_una_lista():
    data = [{"filename": "README.txt", "id": "other"},
            {"filename": "Spaphish dataset - DiB.csv", "id": "c27e1120-88d9-4ee8-a739-a1"}]
    found = find_csv_entry(data)
    assert found["filename"].endswith(".csv")
    assert found["id"].startswith("c27e")


def test_archivo_oficial_se_identifica_dentro_del_campo_files():
    found = find_csv_entry({"files": [{"name": "SpaPhish_v5.csv", "uuid": "abcd"}]})
    assert found["id"] == "abcd"


def test_lista_sin_csv_lanza_error():
    with pytest.raises(FileNotFoundError):
        find_csv_entry([{"filename": "README.txt", "id": "xyz"}])
