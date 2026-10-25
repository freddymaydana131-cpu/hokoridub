"""RF-16 y RF-17: afinidad y ranking de voces compatibles."""

import pytest

from hokoridub.errors import NotFoundError, ValidationError
from hokoridub.matching import affinity, affinity_level, compatible_voices

from tests.factories import make_catalog, make_character, make_profile, make_voice


def test_rf16_afinidad_perfecta():
    voice = make_voice()
    character = make_character()
    assert affinity(voice, character) == 100


def test_rf16_registro_opcional_no_resta():
    character = make_character(register=None)
    assert affinity(make_voice(), character) == 100


def test_rf16_registro_distinto_resta_treinta():
    character = make_character(register="bajo")
    assert affinity(make_voice(), character) == 70


def test_rf16_timbre_parcial():
    character = make_character(timbres=("dulce", "nasal"))
    assert affinity(make_voice(), character) == 85


def test_rf16_sin_timbres_requeridos():
    character = make_character(timbres=())
    assert affinity(make_voice(), character) == 100


def test_rf16_edad_sin_solape():
    character = make_character(register=None, timbres=(), age_min=60, age_max=70)
    assert affinity(make_voice(), character) == 60


def test_rf16_edad_parcial():
    character = make_character(register=None, timbres=(), age_min=30, age_max=50)
    # Solape 30-35 = 6; unión 18-50 = 33 -> 6*40//33 = 7
    assert affinity(make_voice(), character) == 30 + 30 + 7


def test_rf16_siempre_entre_cero_y_cien():
    character = make_character(
        register="bajo", timbres=("nasal", "rasposo"), age_min=80, age_max=90
    )
    score = affinity(make_voice(), character)
    assert 0 <= score <= 100


@pytest.mark.parametrize(
    ("score", "level"),
    [(100, "alta"), (80, "alta"), (79, "media"), (50, "media"), (49, "baja"), (0, "baja")],
)
def test_rf17_niveles(score, level):
    assert affinity_level(score) == level


def _pair_catalog():
    perfect = make_voice("v-1", "Ana")
    medium = make_voice(
        "v-2", "Beto", profile=make_profile(register="baritono", timbres=("nasal",))
    )
    archived = make_voice("v-3", "Carla", archived_at="2026-10-24T10:00:00Z")
    character = make_character()
    return make_catalog(voices=(perfect, medium, archived), characters=(character,))


def test_rf17_ordena_por_afinidad_y_excluye_archivadas():
    pairs = compatible_voices(_pair_catalog(), "c-1")
    assert [voice.id for voice, _ in pairs] == ["v-1", "v-2"]
    assert pairs[0][1] == 100
    assert pairs[1][1] == 40


def test_rf17_desempate_alfabetico():
    first = make_voice("v-1", "Zoe")
    second = make_voice("v-2", "Ana")
    catalog = make_catalog(voices=(first, second), characters=(make_character(),))
    pairs = compatible_voices(catalog, "c-1")
    assert [voice.name for voice, _ in pairs] == ["Ana", "Zoe"]


def test_rf17_filtro_y_limite():
    catalog = _pair_catalog()
    assert len(compatible_voices(catalog, "c-1", min_affinity=60)) == 1
    assert len(compatible_voices(catalog, "c-1", limit=1)) == 1


def test_rf17_personaje_inexistente():
    with pytest.raises(NotFoundError):
        compatible_voices(make_catalog(), "c-404")


def test_rf17_personaje_archivado():
    character = make_character(archived_at="2026-10-24T10:00:00Z")
    catalog = make_catalog(voices=(make_voice(),), characters=(character,))
    with pytest.raises(NotFoundError):
        compatible_voices(catalog, "c-1")


def test_rf17_afinidad_minima_invalida():
    with pytest.raises(ValidationError):
        compatible_voices(_pair_catalog(), "c-1", min_affinity=101)


def test_rf17_limite_invalido():
    with pytest.raises(ValidationError):
        compatible_voices(_pair_catalog(), "c-1", limit=0)
