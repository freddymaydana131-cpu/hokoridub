"""RF-19 y RF-20: persistencia JSON versionada y escritura atómica."""

import json

import pytest

from hokoridub.errors import StorageError
from hokoridub.models import Catalog
from hokoridub.storage import (
    SCHEMA_VERSION,
    catalog_to_dict,
    load_catalog,
    save_catalog,
)

from tests.factories import make_catalog, make_character, make_recording, make_voice

from hokoridub import storage


def test_rf20_archivo_inexistente_devuelve_catalogo_vacio(tmp_path):
    assert load_catalog(tmp_path / "no-existe.json") == Catalog()


def test_rf19_ida_y_vuelta(tmp_path):
    catalog = make_catalog(
        voices=(make_voice(recordings=(make_recording(),)),),
        characters=(make_character(),),
    )
    path = tmp_path / "datos" / "catalogo.json"
    save_catalog(catalog, path)
    assert path.exists()
    loaded = load_catalog(path)
    assert loaded == catalog


def test_rf19_json_versionado(tmp_path):
    path = tmp_path / "catalogo.json"
    save_catalog(make_catalog(), path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == {"schema_version": SCHEMA_VERSION, "voices": [], "characters": []}


def test_rf19_serializacion_completa():
    catalog = make_catalog(
        voices=(make_voice(recordings=(make_recording(),)),),
        characters=(make_character(),),
    )
    data = catalog_to_dict(catalog)
    assert data["voices"][0]["profile"]["register"] == "mezzosoprano"
    assert data["voices"][0]["recordings"][0]["rating"] == 5
    assert data["characters"][0]["requirements"]["difficulty"] == 3


def test_rf20_json_invalido(tmp_path):
    path = tmp_path / "catalogo.json"
    path.write_text("{ no es json", encoding="utf-8")
    with pytest.raises(StorageError, match="JSON válido"):
        load_catalog(path)


def test_rf20_version_incompatible(tmp_path):
    path = tmp_path / "catalogo.json"
    path.write_text(
        json.dumps({"schema_version": 99, "voices": [], "characters": []}),
        encoding="utf-8",
    )
    with pytest.raises(StorageError, match="versión"):
        load_catalog(path)


def test_rf20_estructura_invalida(tmp_path):
    path = tmp_path / "catalogo.json"
    path.write_text(
        json.dumps({"schema_version": SCHEMA_VERSION, "voices": {}, "characters": []}),
        encoding="utf-8",
    )
    with pytest.raises(StorageError, match="estructura"):
        load_catalog(path)


def test_rf20_identificadores_repetidos(tmp_path):
    voice = make_voice()
    path = tmp_path / "catalogo.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "voices": [catalog_to_dict(make_catalog(voices=(voice,)))["voices"][0]] * 2,
                "characters": [],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(StorageError, match="repetidos"):
        load_catalog(path)


def test_rf20_referencia_a_personaje_inexistente(tmp_path):
    voice = make_voice(recordings=(make_recording(character_id="c-404"),))
    path = tmp_path / "catalogo.json"
    save_catalog(make_catalog(voices=(voice,)), path)
    with pytest.raises(StorageError, match="referencias"):
        load_catalog(path)


def test_rf19_escritura_atomica_conserva_el_original(tmp_path, monkeypatch):
    path = tmp_path / "catalogo.json"
    save_catalog(make_catalog(voices=(make_voice(),)), path)
    original = path.read_text(encoding="utf-8")

    def fail(*_args, **_kwargs):
        raise OSError("fallo simulado")

    monkeypatch.setattr(storage.os, "replace", fail)
    with pytest.raises(StorageError, match="No se pudo guardar"):
        save_catalog(make_catalog(), path)

    assert path.read_text(encoding="utf-8") == original
    leftovers = [item.name for item in tmp_path.iterdir() if item.name.endswith(".tmp")]
    assert leftovers == []


def test_rf19_crea_directorios_padre(tmp_path):
    path = tmp_path / "a" / "b" / "catalogo.json"
    save_catalog(make_catalog(), path)
    assert path.exists()
