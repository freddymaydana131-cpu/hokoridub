"""RF-01 a RF-18 a través de la interfaz de línea de comandos."""

import pytest

from hokoridub.cli import main
from hokoridub.messages import EMPTY_VOICES

VOICE_ARGS = (
    "voz",
    "agregar",
    "--nombre",
    "Ana Torres",
    "--registro",
    "mezzosoprano",
    "--extension",
    "C3-C5",
    "--edad",
    "18-35",
)

CHARACTER_ARGS = (
    "personaje",
    "agregar",
    "--nombre",
    "Maya",
    "--obra",
    "Serie X",
    "--tipo",
    "animacion",
    "--descripcion",
    "Niña curiosa de voz brillante.",
    "--edad",
    "10-15",
)


def run(path, *args: str) -> int:
    return main(["--datos", str(path), *args])


def _created_id(capsys) -> str:
    return capsys.readouterr().out.strip().rsplit(": ", 1)[-1]


def _prepare_voice(path, capsys) -> str:
    assert run(path, *VOICE_ARGS) == 0
    return _created_id(capsys)


def _prepare_character(path, capsys) -> str:
    assert run(path, *CHARACTER_ARGS) == 0
    return _created_id(capsys)


def test_cli_flujo_completo(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    voice_id = _prepare_voice(path, capsys)
    character_id = _prepare_character(path, capsys)

    assert run(
        path,
        "prueba",
        "agregar",
        "--voz",
        voice_id,
        "--personaje",
        character_id,
        "--tipo",
        "demo",
        "--valoracion",
        "5",
        "--duracion",
        "45",
    ) == 0
    assert "Prueba registrada" in capsys.readouterr().out

    assert run(path, "voz", "listar") == 0
    assert "Ana Torres" in capsys.readouterr().out

    assert run(path, "voz", "ver", voice_id) == 0
    detalle = capsys.readouterr().out
    assert "Maya" in detalle
    assert "demo" in detalle

    assert run(path, "compatibles", character_id) == 0
    assert "media" in capsys.readouterr().out


def test_cli_archivar_voz(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    voice_id = _prepare_voice(path, capsys)

    assert run(path, "voz", "archivar", voice_id) == 2
    assert "confirmar" in capsys.readouterr().err

    assert run(path, "voz", "archivar", voice_id, "--confirmar") == 0
    assert "Voz archivada" in capsys.readouterr().out

    assert run(path, "voz", "listar") == 0
    assert capsys.readouterr().out.strip() == EMPTY_VOICES

    assert run(path, "voz", "ver", voice_id) == 2
    assert "no está disponible" in capsys.readouterr().err


def test_cli_validacion_no_escribe_el_archivo(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    assert run(
        path,
        "voz",
        "agregar",
        "--nombre",
        "Ana",
        "--registro",
        "mezzosoprano",
        "--extension",
        "C3-C5",
        "--edad",
        "30-18",
    ) == 2
    assert "edad mínima" in capsys.readouterr().err
    assert not path.exists()


def test_cli_archivo_corrupto(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    path.write_text("{ roto", encoding="utf-8")
    assert run(path, "voz", "listar") == 1
    assert "JSON válido" in capsys.readouterr().err
    assert path.read_text(encoding="utf-8") == "{ roto"


def test_cli_listar_vacio_no_crea_archivo(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    assert run(path, "voz", "listar") == 0
    assert capsys.readouterr().out.strip() == EMPTY_VOICES
    assert not path.exists()


def test_cli_busqueda_sin_tildes(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    assert run(
        path,
        "voz",
        "agregar",
        "--nombre",
        "Amélie Dupont",
        "--registro",
        "soprano",
        "--extension",
        "C4-C6",
        "--edad",
        "20-30",
    ) == 0
    capsys.readouterr()

    assert run(path, "voz", "listar", "--buscar", "amelie") == 0
    assert "Amélie Dupont" in capsys.readouterr().out


def test_cli_editar_voz(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    voice_id = _prepare_voice(path, capsys)

    assert run(path, "voz", "editar", voice_id, "--nombre", "Ana María", "--estado", "egresada") == 0
    capsys.readouterr()

    assert run(path, "voz", "ver", voice_id) == 0
    detalle = capsys.readouterr().out
    assert "Ana María" in detalle
    assert "egresada" in detalle


def test_cli_editar_prueba(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    voice_id = _prepare_voice(path, capsys)
    character_id = _prepare_character(path, capsys)

    assert run(
        path,
        "prueba",
        "agregar",
        "--voz",
        voice_id,
        "--personaje",
        character_id,
        "--tipo",
        "demo",
        "--valoracion",
        "3",
    ) == 0
    recording_id = _created_id(capsys)

    assert run(
        path,
        "prueba",
        "editar",
        "--voz",
        voice_id,
        "--id",
        recording_id,
        "--valoracion",
        "5",
    ) == 0
    capsys.readouterr()

    assert run(path, "prueba", "listar", "--voz", voice_id) == 0
    assert "5" in capsys.readouterr().out


def test_cli_compatibles_personaje_archivado(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    _prepare_voice(path, capsys)
    character_id = _prepare_character(path, capsys)

    assert run(path, "personaje", "archivar", character_id, "--confirmar") == 0
    capsys.readouterr()

    assert run(path, "compatibles", character_id) == 2
    assert "personaje no está disponible" in capsys.readouterr().err


def test_cli_compatibles_limite_invalido(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    _prepare_voice(path, capsys)
    character_id = _prepare_character(path, capsys)

    assert run(path, "compatibles", character_id, "--limite", "0") == 2
    assert "límite" in capsys.readouterr().err


def test_cli_variable_de_entorno(tmp_path, capsys, monkeypatch):
    env_path = tmp_path / "env.json"
    monkeypatch.setenv("HOKORIDUB_ARCHIVO", str(env_path))
    monkeypatch.chdir(tmp_path)

    assert main(list(VOICE_ARGS)) == 0
    assert env_path.exists()


def test_cli_datos_gana_a_la_variable_de_entorno(tmp_path, capsys, monkeypatch):
    env_path = tmp_path / "env.json"
    explicit = tmp_path / "explicito.json"
    monkeypatch.setenv("HOKORIDUB_ARCHIVO", str(env_path))

    assert run(explicit, *VOICE_ARGS) == 0
    assert explicit.exists()
    assert not env_path.exists()


def test_cli_argumentos_incompletos(tmp_path):
    with pytest.raises(SystemExit) as error:
        run(tmp_path / "catalogo.json", "voz", "agregar")
    assert error.value.code == 2


def test_cli_personaje_ver(tmp_path, capsys):
    """RF-15: detalle de un personaje con descripción y requisitos."""
    path = tmp_path / "catalogo.json"
    character_id = _prepare_character(path, capsys)
    assert run(path, "personaje", "ver", character_id) == 0
    detalle = capsys.readouterr().out
    assert "Maya" in detalle
    assert "Dificultad: 3" in detalle


def test_cli_personaje_editar(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    character_id = _prepare_character(path, capsys)
    assert run(path, "personaje", "editar", character_id, "--dificultad", "5") == 0
    capsys.readouterr()
    assert run(path, "personaje", "ver", character_id) == 0
    assert "Dificultad: 5" in capsys.readouterr().out


def test_cli_prueba_sobre_voz_archivada(tmp_path, capsys):
    path = tmp_path / "catalogo.json"
    voice_id = _prepare_voice(path, capsys)
    character_id = _prepare_character(path, capsys)
    assert run(path, "voz", "archivar", voice_id, "--confirmar") == 0
    capsys.readouterr()

    assert run(
        path,
        "prueba",
        "agregar",
        "--voz",
        voice_id,
        "--personaje",
        character_id,
        "--tipo",
        "demo",
    ) == 2
    assert "voz no está disponible" in capsys.readouterr().err
