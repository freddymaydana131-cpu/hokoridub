"""RF-12: normalización de texto para búsquedas."""

from hokoridub.text import contains, normalize


def test_rf12_normaliza_mayusculas_y_tildes():
    assert normalize("  Amélie  ") == "amelie"
    assert normalize("GARCÍA MÁRQUEZ") == "garcia marquez"


def test_rf12_trata_la_ene_como_n():
    assert normalize("Ñandú") == "nandu"


def test_rf12_colapsa_espacios_internos():
    assert normalize("  voz   de   niña ") == "voz de nina"


def test_rf12_texto_vacio():
    assert normalize("") == ""
    assert normalize(None) == ""


def test_rf12_contains_ignora_tildes():
    assert contains("García", "garcia")
    assert not contains("García", "perez")
