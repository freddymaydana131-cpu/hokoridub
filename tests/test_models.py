"""RF-02, RF-05 y RF-08: validación de entidades."""

import pytest

from hokoridub.errors import ValidationError
from hokoridub.models import VoiceProfile, VoiceRequirements

from tests.factories import make_character, make_recording, make_voice


def test_voz_valida():
    voice = make_voice(stage_name="Vale", contact="vale@example.com", notes="Notas")
    assert voice.name == "Ana Torres"
    assert voice.profile.register == "mezzosoprano"
    assert voice.languages == ("es", "en")


def test_rf02_nombre_obligatorio():
    with pytest.raises(ValidationError, match="nombre de la voz es obligatorio"):
        make_voice(name="   ")


def test_rf02_nombre_demasiado_largo():
    with pytest.raises(ValidationError, match="120 caracteres"):
        make_voice(name="a" * 121)


def test_rf02_registro_invalido():
    with pytest.raises(ValidationError, match="registro"):
        make_voice(profile=_profile(register="baritono_falso"))


def _profile(**overrides):
    data = dict(
        register="mezzosoprano",
        midi_min=55,
        midi_max=79,
        timbres=("dulce",),
        age_min=18,
        age_max=35,
        accents=(),
    )
    data.update(overrides)
    return VoiceProfile(**data)


def test_rf02_extension_invertida():
    with pytest.raises(ValidationError, match="nota mínima"):
        _profile(midi_min=70, midi_max=60)


def test_rf02_extension_fuera_de_rango():
    with pytest.raises(ValidationError, match="extensión"):
        _profile(midi_min=20, midi_max=70)


def test_rf02_timbre_invalido():
    with pytest.raises(ValidationError, match="timbre"):
        _profile(timbres=("ronco",))


def test_rf02_timbre_repetido():
    with pytest.raises(ValidationError, match="repetido"):
        _profile(timbres=("dulce", "dulce"))


def test_rf02_demasiados_timbres():
    with pytest.raises(ValidationError, match="más de 3"):
        _profile(timbres=("dulce", "nasal", "calido", "opaco"))


def test_rf02_edad_invertida():
    with pytest.raises(ValidationError, match="edad mínima"):
        _profile(age_min=40, age_max=30)


def test_rf02_edad_fuera_de_rango():
    with pytest.raises(ValidationError, match="edad"):
        _profile(age_min=1, age_max=30)


def test_rf02_idiomas_obligatorios():
    with pytest.raises(ValidationError, match="al menos un idioma"):
        make_voice(languages=())


def test_rf02_idioma_repetido():
    with pytest.raises(ValidationError, match="repetido"):
        make_voice(languages=("es", "ES"))


def test_rf02_estado_invalido():
    with pytest.raises(ValidationError, match="estado"):
        make_voice(status="desconocido")


def test_rf05_personaje_valido():
    character = make_character()
    assert character.requirements.register == "mezzosoprano"
    assert character.requirements.difficulty == 3


def test_rf05_nombre_personaje_obligatorio():
    with pytest.raises(ValidationError, match="nombre del personaje"):
        make_character(name="")


def test_rf05_descripcion_obligatoria():
    with pytest.raises(ValidationError, match="descripción es obligatoria"):
        make_character(description=" ")


def test_rf05_descripcion_demasiado_larga():
    with pytest.raises(ValidationError, match="1000"):
        make_character(description="x" * 1001)


def test_rf05_dificultad_fuera_de_rango():
    with pytest.raises(ValidationError, match="dificultad"):
        make_character(difficulty=6)


def test_rf05_timbres_de_personaje_validos():
    with pytest.raises(ValidationError, match="timbre"):
        make_character(timbres=("ronco",))


def test_rf08_valoracion_fuera_de_rango():
    with pytest.raises(ValidationError, match="valoración"):
        make_recording(rating=6)


def test_rf08_duracion_fuera_de_rango():
    with pytest.raises(ValidationError, match="duración"):
        make_recording(duration_seconds=0)


def test_rf08_enlace_invalido():
    with pytest.raises(ValidationError, match="http"):
        make_recording(link="ftp://example.com/a.mp3")


def test_rf08_comentario_demasiado_largo():
    with pytest.raises(ValidationError, match="comentario"):
        make_recording(comment="x" * 501)


def test_rf08_tipo_de_prueba_invalido():
    with pytest.raises(ValidationError, match="tipo de prueba"):
        make_recording(kind="ensayo")


def test_requisitos_validos_sin_registro():
    requirements = VoiceRequirements(age_min=20, age_max=30)
    assert requirements.register is None
    assert requirements.difficulty == 3
