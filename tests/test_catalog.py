"""RF-01 a RF-18: reglas del catálogo."""

import pytest

from hokoridub import catalog as service
from hokoridub.catalog import (
    STATE_EMPTY,
    STATE_NO_MATCHES,
    STATE_OK,
)
from hokoridub.errors import ConfirmationError, NotFoundError, ValidationError

from tests.factories import (
    NOW,
    make_catalog,
    make_character,
    make_profile,
    make_recording,
    make_voice,
)

LATER = "2026-10-26T12:00:00Z"


def test_rf01_alta_de_voz():
    catalog = make_catalog()
    voice = service.add_voice(
        catalog,
        name="Ana Torres",
        profile=make_profile(),
        languages=["es", "en"],
        new_id="v-1",
        now=NOW,
        stage_name="Vale",
    )
    assert voice.id == "v-1"
    assert catalog.voices == [voice]
    assert voice.created_at == NOW


def test_rf01_id_de_voz_repetido():
    catalog = make_catalog(voices=(make_voice(),))
    with pytest.raises(ValidationError, match="identificador"):
        service.add_voice(
            catalog,
            name="Otra",
            profile=make_profile(),
            languages=["es"],
            new_id="v-1",
            now=NOW,
        )


def test_rf03_edicion_de_voz():
    catalog = make_catalog(voices=(make_voice(),))
    updated = service.edit_voice(
        catalog,
        "v-1",
        changes={"name": "Ana María", "age_min": 20, "age_max": 40, "notes": "Nueva nota"},
        now=LATER,
    )
    assert updated.name == "Ana María"
    assert updated.profile.age_min == 20
    assert updated.profile.age_max == 40
    assert updated.updated_at == LATER
    assert updated.created_at == NOW
    assert catalog.voices[0] == updated


def test_rf03_no_se_edita_una_voz_archivada():
    catalog = make_catalog(voices=(make_voice(archived_at=NOW),))
    with pytest.raises(NotFoundError):
        service.edit_voice(catalog, "v-1", changes={"name": "X"}, now=LATER)


def test_rf03_edicion_de_perfil_completo():
    catalog = make_catalog(voices=(make_voice(),))
    updated = service.edit_voice(
        catalog,
        "v-1",
        changes={"register": "contralto", "timbres": ("nasal",)},
        now=LATER,
    )
    assert updated.profile.register == "contralto"
    assert updated.profile.timbres == ("nasal",)


def test_rf18_archivar_exige_confirmacion():
    catalog = make_catalog(voices=(make_voice(),))
    with pytest.raises(ConfirmationError):
        service.archive_voice(catalog, "v-1", confirmed=False, now=NOW)
    assert catalog.voices[0].archived_at is None


def test_rf18_archivar_oculta_y_conserva_pruebas():
    recording = make_recording()
    catalog = make_catalog(
        voices=(make_voice(recordings=(recording,)),), characters=(make_character(),)
    )
    archived = service.archive_voice(catalog, "v-1", confirmed=True, now=LATER)
    assert archived.archived_at == LATER
    assert archived.recordings == (recording,)
    assert service.active_voices(catalog) == []
    with pytest.raises(NotFoundError):
        service.require_active_voice(catalog, "v-1")


def test_rf18_archivar_voz_inexistente():
    with pytest.raises(NotFoundError):
        service.archive_voice(make_catalog(), "v-404", confirmed=True, now=NOW)


def test_rf04_alta_de_personaje():
    catalog = make_catalog()
    character = service.add_character(
        catalog,
        name="Maya",
        work="Serie X",
        kind="animacion",
        description="Niña curiosa.",
        requirements=make_character().requirements,
        new_id="c-1",
        now=NOW,
    )
    assert character.id == "c-1"
    assert catalog.characters == [character]


def test_rf06_edicion_de_personaje():
    catalog = make_catalog(characters=(make_character(),))
    updated = service.edit_character(
        catalog,
        "c-1",
        changes={"name": "Maya 2", "difficulty": 5, "register": None},
        now=LATER,
    )
    assert updated.name == "Maya 2"
    assert updated.requirements.difficulty == 5
    assert updated.requirements.register is None


def test_rf18_archivar_personaje_oculta_sin_borrar_pruebas():
    recording = make_recording()
    catalog = make_catalog(
        voices=(make_voice(recordings=(recording,)),), characters=(make_character(),)
    )
    service.archive_character(catalog, "c-1", confirmed=True, now=LATER)
    assert service.active_characters(catalog) == []
    assert catalog.voices[0].recordings == (recording,)
    assert catalog.character("c-1") is not None


def test_rf07_alta_de_prueba():
    catalog = make_catalog(
        voices=(make_voice(),), characters=(make_character(),)
    )
    recording = service.add_recording(
        catalog,
        voice_id="v-1",
        character_id="c-1",
        kind="demo",
        new_id="r-1",
        now=NOW,
        rating=5,
    )
    assert recording.id == "r-1"
    assert catalog.voices[0].recordings == (recording,)
    assert catalog.voices[0].updated_at == NOW


def test_rn03_no_se_registran_pruebas_sobre_voz_archivada():
    catalog = make_catalog(
        voices=(make_voice(archived_at=NOW),), characters=(make_character(),)
    )
    with pytest.raises(NotFoundError):
        service.add_recording(
            catalog,
            voice_id="v-1",
            character_id="c-1",
            kind="demo",
            new_id="r-1",
            now=NOW,
        )


def test_rn03_no_se_registran_pruebas_sobre_personaje_archivado():
    catalog = make_catalog(
        voices=(make_voice(),), characters=(make_character(archived_at=NOW),)
    )
    with pytest.raises(NotFoundError):
        service.add_recording(
            catalog,
            voice_id="v-1",
            character_id="c-1",
            kind="demo",
            new_id="r-1",
            now=NOW,
        )


def test_rf07_id_de_prueba_repetido():
    recording = make_recording("r-1")
    catalog = make_catalog(
        voices=(make_voice(recordings=(recording,)),), characters=(make_character(),)
    )
    with pytest.raises(ValidationError, match="identificador"):
        service.add_recording(
            catalog,
            voice_id="v-1",
            character_id="c-1",
            kind="demo",
            new_id="r-1",
            now=NOW,
        )


def test_rf07_datos_invalidos_no_modifican_el_catalogo():
    catalog = make_catalog(voices=(make_voice(),), characters=(make_character(),))
    with pytest.raises(ValidationError):
        service.add_recording(
            catalog,
            voice_id="v-1",
            character_id="c-1",
            kind="demo",
            new_id="r-1",
            now=NOW,
            rating=9,
        )
    assert catalog.voices[0].recordings == ()


def test_rf09_edicion_de_prueba_conserva_creacion():
    recording = make_recording()
    catalog = make_catalog(
        voices=(make_voice(recordings=(recording,)),), characters=(make_character(),)
    )
    updated = service.edit_recording(
        catalog, voice_id="v-1", recording_id="r-1", changes={"rating": 2}, now=LATER
    )
    assert updated.rating == 2
    assert updated.created_at == NOW
    assert updated.updated_at == LATER


def test_rf09_prueba_inexistente():
    catalog = make_catalog(voices=(make_voice(),), characters=(make_character(),))
    with pytest.raises(NotFoundError):
        service.edit_recording(
            catalog, voice_id="v-1", recording_id="r-404", changes={"rating": 2}, now=LATER
        )


def test_rf10_portafolio_ordenado():
    older = make_recording("r-1", recorded_at="2026-10-01T10:00:00Z")
    newer = make_recording("r-2", recorded_at="2026-10-20T10:00:00Z")
    voice = make_voice(recordings=(older, newer))
    catalog = make_catalog(voices=(voice,), characters=(make_character(),))
    rows = service.portfolio(catalog, voice)
    assert [recording.id for recording, _ in rows] == ["r-2", "r-1"]
    assert rows[0][1].name == "Maya"


def test_rf14_ultima_actividad_incluye_pruebas():
    recording = make_recording(recorded_at="2026-11-01T10:00:00Z")
    voice = make_voice(recordings=(recording,))
    assert service.last_activity(voice) == "2026-11-01T10:00:00Z"


def test_rf11_vista_vacia():
    assert service.voice_view(make_catalog()) == (STATE_EMPTY, [])


def test_rf11_vista_sin_coincidencias():
    catalog = make_catalog(voices=(make_voice(),))
    assert service.voice_view(catalog, text="zzz") == (STATE_NO_MATCHES, [])


def test_rf11_archivadas_no_aparecen():
    catalog = make_catalog(voices=(make_voice(archived_at=NOW),))
    assert service.voice_view(catalog) == (STATE_EMPTY, [])


def test_rf12_busqueda_sin_tildes():
    catalog = make_catalog(voices=(make_voice(name="Amélie Dupont"),))
    state, voices = service.voice_view(catalog, text="amelie")
    assert state == STATE_OK
    assert voices[0].name == "Amélie Dupont"


def test_rf12_busqueda_por_nombre_artistico():
    catalog = make_catalog(voices=(make_voice(stage_name="Vale"),))
    _, voices = service.voice_view(catalog, text="vale")
    assert len(voices) == 1


def test_rf12_busqueda_por_notas_de_voz():
    catalog = make_catalog(voices=(make_voice(notes="Especializada en animación."),))
    _, voices = service.voice_view(catalog, text="animacion")
    assert len(voices) == 1


def test_rf13_filtros_de_voces():
    voice = make_voice(
        "v-2",
        profile=make_profile(register="contralto", timbres=("nasal",), age_min=40, age_max=50),
        languages=("en",),
    )
    catalog = make_catalog(voices=(make_voice(languages=("es",)), voice))
    _, voices = service.voice_view(catalog, register="contralto")
    assert [item.id for item in voices] == ["v-2"]
    _, voices = service.voice_view(catalog, timbre="nasal")
    assert [item.id for item in voices] == ["v-2"]
    _, voices = service.voice_view(catalog, language="EN")
    assert [item.id for item in voices] == ["v-2"]
    _, voices = service.voice_view(catalog, status="activa")
    assert len(voices) == 2


def test_rf14_orden_por_edad():
    older = make_voice("v-1", "Zoe", profile=make_profile(age_min=40, age_max=50))
    younger = make_voice("v-2", "Ana", profile=make_profile(age_min=20, age_max=30))
    catalog = make_catalog(voices=(older, younger))
    _, voices = service.voice_view(catalog, order="edad")
    assert [voice.id for voice in voices] == ["v-2", "v-1"]


def test_rf14_orden_por_actividad():
    old = make_voice(
        "v-1", "Ana", created_at="2025-01-01T00:00:00Z", updated_at="2026-01-01T00:00:00Z"
    )
    new = make_voice(
        "v-2", "Beto", created_at="2025-01-01T00:00:00Z", updated_at="2026-05-01T00:00:00Z"
    )
    catalog = make_catalog(voices=(old, new))
    _, voices = service.voice_view(catalog, order="actividad")
    assert [voice.id for voice in voices] == ["v-2", "v-1"]


def test_rf14_orden_invalido():
    with pytest.raises(ValidationError):
        service.voice_view(make_catalog(voices=(make_voice(),)), order="precio")


def test_rf11_vista_de_personajes():
    catalog = make_catalog(characters=(make_character(name="Maya", work="Serie X"),))
    state, characters = service.character_view(catalog, text="serie")
    assert state == STATE_OK
    assert characters[0].id == "c-1"
    assert service.character_view(catalog, text="zzz") == (STATE_NO_MATCHES, [])
    assert service.character_view(make_catalog()) == (STATE_EMPTY, [])


def test_rf12_busqueda_por_descripcion_de_personaje():
    catalog = make_catalog(
        characters=(make_character(description="Niña que habla con los árboles."),)
    )
    _, characters = service.character_view(catalog, text="arboles")
    assert [character.id for character in characters] == ["c-1"]


def test_rf13_filtros_de_personajes():
    first = make_character("c-1", "Maya", kind="animacion")
    second = make_character("c-2", "Kai", kind="videojuego", register="bajo")
    catalog = make_catalog(characters=(first, second))
    _, characters = service.character_view(catalog, kind="videojuego")
    assert [item.id for item in characters] == ["c-2"]
    _, characters = service.character_view(catalog, register="mezzosoprano")
    assert [item.id for item in characters] == ["c-1"]


def test_rf07_listado_de_pruebas_con_filtros():
    one = make_recording("r-1")
    two = make_recording("r-2", kind="audicion")
    catalog = make_catalog(
        voices=(make_voice(recordings=(one, two)),), characters=(make_character(),)
    )
    assert len(service.recording_rows(catalog)) == 2
    assert len(service.recording_rows(catalog, kind="audicion")) == 1
    assert len(service.recording_rows(catalog, character_id="c-1")) == 2
    assert service.recording_rows(catalog, voice_id="v-404") == []


def test_rf07_pruebas_de_voz_archivada_no_se_listan():
    catalog = make_catalog(
        voices=(make_voice(archived_at=NOW, recordings=(make_recording(),)),),
        characters=(make_character(),),
    )
    assert service.recording_rows(catalog) == []


def test_rf10_conteo_de_pruebas_por_personaje():
    catalog = make_catalog(
        voices=(make_voice(recordings=(make_recording(),)),),
        characters=(make_character(),),
    )
    assert service.character_recording_count(catalog, "c-1") == 1
    assert service.character_recording_count(catalog, "c-404") == 0
