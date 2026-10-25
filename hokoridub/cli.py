"""Interfaz de línea de comandos en español (RF-01 a RF-18)."""

from __future__ import annotations

import argparse
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import catalog as service
from .catalog import VOICE_ORDERS, CHARACTER_ORDERS
from .errors import ConfirmationError, NotFoundError, StorageError, ValidationError
from .matching import affinity_level, compatible_voices
from .messages import (
    ARCHIVED_SUFFIX,
    EMPTY_CHARACTERS,
    EMPTY_RECORDINGS,
    EMPTY_VOICES,
    ERROR_PREFIX,
    HEADERS_CHARACTERS,
    HEADERS_COMPATIBLES,
    HEADERS_PORTFOLIO,
    HEADERS_RECORDINGS,
    HEADERS_VOICES,
    LABELS,
    NO_COMPATIBLES,
    NO_MATCH_CHARACTERS,
    NO_MATCH_RECORDINGS,
    NO_MATCH_VOICES,
    NO_STAGE_NAME,
    msg,
)
from .models import (
    CHARACTER_KINDS,
    DURATION_MAX,
    DURATION_MIN,
    RATING_MAX,
    RATING_MIN,
    RECORDING_KINDS,
    REGISTERS,
    STATUSES,
    TIMBRES,
    Catalog,
    VoiceProfile,
    VoiceRequirements,
)
from .notes import format_range, note_to_midi
from .storage import load_catalog, save_catalog

DEFAULT_DATA_FILE = "catalogo.json"
DATA_ENV_VAR = "HOKORIDUB_ARCHIVO"


class _Parser(argparse.ArgumentParser):
    """Parser con mensajes de error en español."""

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, f"{ERROR_PREFIX} Argumentos inválidos: {message}\n")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_id() -> str:
    return str(uuid.uuid4())


# --- Conversión de argumentos ------------------------------------------------------


def _split_list(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [part.strip() for part in value.split(",") if part.strip()]


def _parse_int(value: str | None, key: str, low: int, high: int) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as error:
        raise ValidationError(msg(key, low=low, high=high)) from error


def _parse_age(value: str) -> tuple[int, int]:
    parts = value.split("-")
    try:
        if len(parts) != 2:
            raise ValueError
        return int(parts[0]), int(parts[1])
    except (TypeError, ValueError) as error:
        raise ValidationError(msg("age_range", low=5, high=90)) from error


def _parse_extension(value: str) -> tuple[int, int]:
    parts = value.split("-")
    if len(parts) != 2:
        raise ValidationError(msg("midi_range", low="C2", high="C7"))
    return note_to_midi(parts[0]), note_to_midi(parts[1])


def _profile_from_args(args: argparse.Namespace) -> VoiceProfile:
    age_min, age_max = _parse_age(args.edad)
    midi_min, midi_max = _parse_extension(args.extension)
    return VoiceProfile(
        register=args.registro,
        midi_min=midi_min,
        midi_max=midi_max,
        timbres=tuple(_split_list(args.timbres) or []),
        age_min=age_min,
        age_max=age_max,
        accents=tuple(_split_list(args.acentos) or []),
    )


def _requirements_from_args(args: argparse.Namespace) -> VoiceRequirements:
    age_min, age_max = _parse_age(args.edad)
    return VoiceRequirements(
        register=args.registro,
        timbres=tuple(_split_list(args.timbres) or []),
        age_min=age_min,
        age_max=age_max,
        difficulty=args.dificultad if args.dificultad is not None else 3,
    )


# --- Formato de salida -------------------------------------------------------------


def _render_table(headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> str:
    text_rows = [tuple(str(cell) for cell in row) for row in rows]
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in text_rows))
        for index in range(len(headers))
    ]
    header_line = "  ".join(
        header.ljust(width) for header, width in zip(headers, widths)
    )
    separator = "  ".join("-" * width for width in widths)
    body = [
        "  ".join(cell.ljust(width) for cell, width in zip(row, widths))
        for row in text_rows
    ]
    return "\n".join([header_line, separator, *body])


def _field(key: str, value: object) -> str:
    return f"{LABELS[key]}: {value}"


def _voice_rows(voices: list) -> list[tuple[object, ...]]:
    return [
        (
            voice.id,
            voice.name,
            voice.profile.register,
            f"{voice.profile.age_min}–{voice.profile.age_max}",
            voice.status,
            len(voice.recordings),
            service.last_activity(voice),
        )
        for voice in voices
    ]


def _character_rows(characters: list) -> list[tuple[object, ...]]:
    return [
        (
            character.id,
            character.name,
            character.work,
            character.kind,
            character.requirements.register or "—",
            f"{character.requirements.age_min}–{character.requirements.age_max}",
            character.requirements.difficulty,
        )
        for character in characters
    ]


def _recording_rows(rows: list) -> list[tuple[object, ...]]:
    return [
        (
            recording.id,
            voice.name,
            _character_name(character),
            recording.kind,
            recording.recorded_at,
            recording.rating if recording.rating is not None else "—",
        )
        for recording, voice, character in rows
    ]


def _character_name(character) -> str:
    if character is None:
        return "—"
    suffix = ARCHIVED_SUFFIX if character.archived_at is not None else ""
    return f"{character.name}{suffix}"


# --- Comandos de voz ---------------------------------------------------------------


def _handle_voice(args: argparse.Namespace, catalog: Catalog, now: str) -> tuple[str, bool]:
    if args.action == "agregar":
        voice = service.add_voice(
            catalog,
            name=args.nombre,
            profile=_profile_from_args(args),
            languages=_split_list(args.idiomas) or [],
            new_id=_new_id(),
            now=now,
            stage_name=args.artistico,
            contact=args.contacto,
            notes=args.notas,
            status=args.estado,
        )
        return f"Voz creada: {voice.id}", True

    if args.action == "listar":
        state, voices = service.voice_view(
            catalog,
            text=args.buscar or "",
            register=args.registro,
            timbre=args.timbre,
            status=args.estado,
            language=args.idioma,
            order=args.orden,
        )
        if state == service.STATE_EMPTY:
            return EMPTY_VOICES, False
        if state == service.STATE_NO_MATCHES:
            return NO_MATCH_VOICES, False
        return _render_table(HEADERS_VOICES, _voice_rows(voices)), False

    if args.action == "ver":
        voice = service.require_active_voice(catalog, args.id)
        lines = [
            _field("id", voice.id),
            _field("name", voice.name),
            _field("stage_name", voice.stage_name or NO_STAGE_NAME),
            _field("contact", voice.contact or NO_STAGE_NAME),
            _field("register", voice.profile.register),
            _field("extension", format_range(voice.profile.midi_min, voice.profile.midi_max)),
            _field("timbres", ", ".join(voice.profile.timbres) or NO_STAGE_NAME),
            _field("age", f"{voice.profile.age_min}–{voice.profile.age_max}"),
            _field("languages", ", ".join(voice.languages)),
            _field("accents", ", ".join(voice.profile.accents) or NO_STAGE_NAME),
            _field("status", voice.status),
            _field("created_at", voice.created_at),
            _field("last_activity", service.last_activity(voice)),
            _field("notes", voice.notes or NO_STAGE_NAME),
        ]
        rows = service.portfolio(catalog, voice)
        lines.append("")
        lines.append(f"{LABELS['portfolio']} ({len(rows)}):")
        if rows:
            portfolio_rows = [
                (
                    recording.id,
                    _character_name(character),
                    recording.kind,
                    recording.recorded_at,
                    recording.rating if recording.rating is not None else "—",
                )
                for recording, character in rows
            ]
            lines.append(_render_table(HEADERS_PORTFOLIO, portfolio_rows))
        else:
            lines.append(EMPTY_RECORDINGS)
        return "\n".join(lines), False

    # editar
    changes: dict = {}
    if args.nombre is not None:
        changes["name"] = args.nombre
    if args.artistico is not None:
        changes["stage_name"] = args.artistico
    if args.contacto is not None:
        changes["contact"] = args.contacto
    if args.notas is not None:
        changes["notes"] = args.notas
    if args.estado is not None:
        changes["status"] = args.estado
    if args.idiomas is not None:
        changes["languages"] = _split_list(args.idiomas) or []
    if args.registro is not None:
        changes["register"] = args.registro
    if args.extension is not None:
        midi_min, midi_max = _parse_extension(args.extension)
        changes["midi_min"] = midi_min
        changes["midi_max"] = midi_max
    if args.edad is not None:
        age_min, age_max = _parse_age(args.edad)
        changes["age_min"] = age_min
        changes["age_max"] = age_max
    if args.timbres is not None:
        changes["timbres"] = tuple(_split_list(args.timbres) or [])
    if args.acentos is not None:
        changes["accents"] = tuple(_split_list(args.acentos) or [])
    voice = service.edit_voice(catalog, args.id, changes=changes, now=now)
    return f"Voz actualizada: {voice.id}", True


def _handle_voice_archive(args: argparse.Namespace, catalog: Catalog, now: str) -> tuple[str, bool]:
    voice = service.archive_voice(catalog, args.id, confirmed=args.confirmar, now=now)
    return f"Voz archivada: {voice.id}", True


# --- Comandos de personaje ---------------------------------------------------------


def _handle_character(args: argparse.Namespace, catalog: Catalog, now: str) -> tuple[str, bool]:
    if args.action == "agregar":
        character = service.add_character(
            catalog,
            name=args.nombre,
            work=args.obra,
            kind=args.tipo,
            description=args.descripcion,
            requirements=_requirements_from_args(args),
            new_id=_new_id(),
            now=now,
        )
        return f"Personaje creado: {character.id}", True

    if args.action == "listar":
        state, characters = service.character_view(
            catalog,
            text=args.buscar or "",
            kind=args.tipo,
            register=args.registro,
            order=args.orden,
        )
        if state == service.STATE_EMPTY:
            return EMPTY_CHARACTERS, False
        if state == service.STATE_NO_MATCHES:
            return NO_MATCH_CHARACTERS, False
        return _render_table(HEADERS_CHARACTERS, _character_rows(characters)), False

    if args.action == "ver":
        character = service.require_active_character(catalog, args.id)
        lines = [
            _field("id", character.id),
            _field("name", character.name),
            _field("work", character.work),
            _field("kind", character.kind),
            _field("description", character.description),
            _field("register", character.requirements.register or "—"),
            _field("timbres", ", ".join(character.requirements.timbres) or NO_STAGE_NAME),
            _field(
                "age",
                f"{character.requirements.age_min}–{character.requirements.age_max}",
            ),
            _field("difficulty", character.requirements.difficulty),
            _field("created_at", character.created_at),
            _field("last_activity", character.updated_at),
            _field("portfolio", service.character_recording_count(catalog, character.id)),
        ]
        return "\n".join(lines), False

    # editar
    changes: dict = {}
    if args.nombre is not None:
        changes["name"] = args.nombre
    if args.obra is not None:
        changes["work"] = args.obra
    if args.tipo is not None:
        changes["kind"] = args.tipo
    if args.descripcion is not None:
        changes["description"] = args.descripcion
    if args.registro is not None:
        changes["register"] = None if args.registro == "ninguno" else args.registro
    if args.timbres is not None:
        changes["timbres"] = tuple(_split_list(args.timbres) or [])
    if args.edad is not None:
        age_min, age_max = _parse_age(args.edad)
        changes["age_min"] = age_min
        changes["age_max"] = age_max
    if args.dificultad is not None:
        changes["difficulty"] = args.dificultad
    character = service.edit_character(catalog, args.id, changes=changes, now=now)
    return f"Personaje actualizado: {character.id}", True


def _handle_character_archive(
    args: argparse.Namespace, catalog: Catalog, now: str
) -> tuple[str, bool]:
    character = service.archive_character(
        catalog, args.id, confirmed=args.confirmar, now=now
    )
    return f"Personaje archivado: {character.id}", True


# --- Comandos de prueba ------------------------------------------------------------


def _recording_changes(args: argparse.Namespace) -> dict:
    changes: dict = {}
    if getattr(args, "tipo", None) is not None:
        changes["kind"] = args.tipo
    if getattr(args, "enlace", None) is not None:
        changes["link"] = args.enlace
    if getattr(args, "duracion", None) is not None:
        changes["duration_seconds"] = _parse_int(
            args.duracion, "duration_range", DURATION_MIN, DURATION_MAX
        )
    if getattr(args, "valoracion", None) is not None:
        changes["rating"] = _parse_int(args.valoracion, "rating_range", RATING_MIN, RATING_MAX)
    if getattr(args, "comentario", None) is not None:
        changes["comment"] = args.comentario
    return changes


def _handle_recording(args: argparse.Namespace, catalog: Catalog, now: str) -> tuple[str, bool]:
    if args.action == "agregar":
        recording = service.add_recording(
            catalog,
            voice_id=args.voz,
            character_id=args.personaje,
            kind=args.tipo,
            new_id=_new_id(),
            now=now,
            link=args.enlace,
            duration_seconds=_parse_int(
                args.duracion, "duration_range", DURATION_MIN, DURATION_MAX
            ),
            rating=_parse_int(args.valoracion, "rating_range", RATING_MIN, RATING_MAX),
            comment=args.comentario,
        )
        return f"Prueba registrada: {recording.id}", True

    if args.action == "editar":
        recording = service.edit_recording(
            catalog,
            voice_id=args.voz,
            recording_id=args.id,
            changes=_recording_changes(args),
            now=now,
        )
        return f"Prueba actualizada: {recording.id}", True

    rows = service.recording_rows(
        catalog,
        voice_id=args.voz,
        character_id=args.personaje,
        kind=args.tipo,
    )
    if not rows:
        return NO_MATCH_RECORDINGS, False
    return _render_table(HEADERS_RECORDINGS, _recording_rows(rows)), False


# --- Compatibilidad ----------------------------------------------------------------


def _handle_compatibles(args: argparse.Namespace, catalog: Catalog, now: str) -> tuple[str, bool]:
    limit = _parse_int(args.limite, "limit_range", 1, 1000)
    pairs = compatible_voices(
        catalog,
        args.personaje,
        min_affinity=args.min_afinidad,
        limit=limit,
    )
    if not pairs:
        return NO_COMPATIBLES, False
    rows = [
        (
            score,
            affinity_level(score),
            voice.name,
            voice.profile.register,
            f"{voice.profile.age_min}–{voice.profile.age_max}",
        )
        for voice, score in pairs
    ]
    return _render_table(HEADERS_COMPATIBLES, rows), False


# --- Parser ------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="hokoridub",
        description="Catálogo de personajes y voces de Hokori Dub.",
    )
    parser.add_argument(
        "--datos",
        metavar="RUTA",
        help=(
            "Archivo JSON de datos. Si se omite, se usa la variable "
            f"{DATA_ENV_VAR} o ./{DEFAULT_DATA_FILE}."
        ),
    )
    commands = parser.add_subparsers(dest="command", required=True)

    voice = commands.add_parser("voz", help="Gestiona las voces del catálogo.")
    voice_actions = voice.add_subparsers(dest="action", required=True)

    voice_add = voice_actions.add_parser("agregar", help="Registra una voz.")
    _add_voice_fields(voice_add, required=True)
    voice_add.add_argument("--idiomas", default="es", help="Idiomas separados por coma.")
    voice_add.add_argument("--timbres", default="", help="Timbres separados por coma (máximo 3).")
    voice_add.add_argument("--acentos", default="", help="Acentos separados por coma.")
    voice_add.add_argument("--artistico", default=None, help="Nombre artístico.")
    voice_add.add_argument("--contacto", default=None, help="Contacto.")
    voice_add.add_argument("--notas", default=None, help="Notas libres.")
    voice_add.add_argument("--estado", choices=STATUSES, default="activa", help="Estado de la voz.")

    voice_list = voice_actions.add_parser("listar", help="Lista voces activas.")
    voice_list.add_argument("--buscar", default="", help="Texto a buscar en nombre o nombre artístico.")
    voice_list.add_argument("--registro", choices=REGISTERS, default=None, help="Filtra por registro.")
    voice_list.add_argument("--timbre", choices=TIMBRES, default=None, help="Filtra por timbre.")
    voice_list.add_argument("--estado", choices=STATUSES, default=None, help="Filtra por estado.")
    voice_list.add_argument("--idioma", default=None, help="Filtra por idioma.")
    voice_list.add_argument(
        "--orden", choices=VOICE_ORDERS, default="nombre", help="Orden del listado."
    )

    voice_show = voice_actions.add_parser("ver", help="Muestra el detalle de una voz.")
    voice_show.add_argument("id", help="Identificador de la voz.")

    voice_edit = voice_actions.add_parser("editar", help="Edita una voz.")
    voice_edit.add_argument("id", help="Identificador de la voz.")
    _add_voice_fields(voice_edit, required=False)
    voice_edit.add_argument("--idiomas", default=None, help="Idiomas separados por coma.")
    voice_edit.add_argument("--timbres", default=None, help="Timbres separados por coma.")
    voice_edit.add_argument("--acentos", default=None, help="Acentos separados por coma.")
    voice_edit.add_argument("--artistico", default=None, help="Nombre artístico.")
    voice_edit.add_argument("--contacto", default=None, help="Contacto.")
    voice_edit.add_argument("--notas", default=None, help="Notas libres.")
    voice_edit.add_argument("--estado", choices=STATUSES, default=None, help="Estado de la voz.")

    voice_archive = voice_actions.add_parser("archivar", help="Archiva una voz.")
    voice_archive.add_argument("id", help="Identificador de la voz.")
    voice_archive.add_argument("--confirmar", action="store_true", help="Confirma el archivado.")

    character = commands.add_parser("personaje", help="Gestiona los personajes del catálogo.")
    character_actions = character.add_subparsers(dest="action", required=True)

    character_add = character_actions.add_parser("agregar", help="Registra un personaje.")
    _add_character_fields(character_add, required=True)

    character_list = character_actions.add_parser("listar", help="Lista personajes activos.")
    character_list.add_argument("--buscar", default="", help="Texto a buscar en nombre u obra.")
    character_list.add_argument("--tipo", choices=CHARACTER_KINDS, default=None, help="Filtra por tipo.")
    character_list.add_argument("--registro", choices=REGISTERS, default=None, help="Filtra por registro.")
    character_list.add_argument(
        "--orden", choices=CHARACTER_ORDERS, default="nombre", help="Orden del listado."
    )

    character_show = character_actions.add_parser("ver", help="Muestra el detalle de un personaje.")
    character_show.add_argument("id", help="Identificador del personaje.")

    character_edit = character_actions.add_parser("editar", help="Edita un personaje.")
    character_edit.add_argument("id", help="Identificador del personaje.")
    _add_character_fields(character_edit, required=False, allow_none_register=True)

    character_archive = character_actions.add_parser("archivar", help="Archiva un personaje.")
    character_archive.add_argument("id", help="Identificador del personaje.")
    character_archive.add_argument("--confirmar", action="store_true", help="Confirma el archivado.")

    recording = commands.add_parser("prueba", help="Gestiona las pruebas de voz.")
    recording_actions = recording.add_subparsers(dest="action", required=True)

    recording_add = recording_actions.add_parser("agregar", help="Registra una prueba.")
    recording_add.add_argument("--voz", required=True, help="Identificador de la voz.")
    recording_add.add_argument("--personaje", required=True, help="Identificador del personaje.")
    recording_add.add_argument("--tipo", choices=RECORDING_KINDS, required=True, help="Tipo de prueba.")
    recording_add.add_argument("--enlace", default=None, help="Enlace http(s) al audio.")
    recording_add.add_argument("--duracion", default=None, help="Duración en segundos (1–3600).")
    recording_add.add_argument("--valoracion", default=None, help="Valoración entera de 1 a 5.")
    recording_add.add_argument("--comentario", default=None, help="Comentario de la prueba.")

    recording_edit = recording_actions.add_parser("editar", help="Edita una prueba.")
    recording_edit.add_argument("--voz", required=True, help="Identificador de la voz.")
    recording_edit.add_argument("--id", required=True, help="Identificador de la prueba.")
    recording_edit.add_argument("--tipo", choices=RECORDING_KINDS, default=None, help="Tipo de prueba.")
    recording_edit.add_argument("--enlace", default=None, help="Enlace http(s) al audio.")
    recording_edit.add_argument("--duracion", default=None, help="Duración en segundos (1–3600).")
    recording_edit.add_argument("--valoracion", default=None, help="Valoración entera de 1 a 5.")
    recording_edit.add_argument("--comentario", default=None, help="Comentario de la prueba.")

    recording_list = recording_actions.add_parser("listar", help="Lista pruebas registradas.")
    recording_list.add_argument("--voz", default=None, help="Filtra por voz.")
    recording_list.add_argument("--personaje", default=None, help="Filtra por personaje.")
    recording_list.add_argument("--tipo", choices=RECORDING_KINDS, default=None, help="Filtra por tipo.")

    compatible = commands.add_parser(
        "compatibles", help="Ordena las voces por afinidad con un personaje."
    )
    compatible.add_argument("personaje", help="Identificador del personaje.")
    compatible.add_argument("--limite", default=None, help="Cantidad máxima de resultados.")
    compatible.add_argument(
        "--min-afinidad",
        dest="min_afinidad",
        type=int,
        default=0,
        help="Afinidad mínima (0–100).",
    )

    return parser


def _add_voice_fields(parser: argparse.ArgumentParser, *, required: bool) -> None:
    parser.add_argument("--nombre", required=required, default=None, help="Nombre de la persona.")
    parser.add_argument(
        "--registro",
        choices=REGISTERS,
        required=required,
        default=None,
        help="Registro vocal.",
    )
    parser.add_argument(
        "--extension",
        required=required,
        default=None,
        help="Extensión con notas, por ejemplo C3-C5.",
    )
    parser.add_argument(
        "--edad",
        required=required,
        default=None,
        help="Edad aparente como mínimo-máximo, por ejemplo 18-35.",
    )


def _add_character_fields(
    parser: argparse.ArgumentParser,
    *,
    required: bool,
    allow_none_register: bool = False,
) -> None:
    parser.add_argument("--nombre", required=required, default=None, help="Nombre del personaje.")
    parser.add_argument("--obra", required=required, default=None, help="Obra o franquicia.")
    parser.add_argument(
        "--tipo",
        choices=CHARACTER_KINDS,
        required=required,
        default=None,
        help="Tipo de obra.",
    )
    parser.add_argument(
        "--descripcion", required=required, default=None, help="Descripción del personaje."
    )
    parser.add_argument(
        "--edad",
        required=required,
        default=None,
        help="Edad aparente requerida como mínimo-máximo.",
    )
    register_options = (*REGISTERS, "ninguno") if allow_none_register else REGISTERS
    parser.add_argument(
        "--registro",
        choices=register_options,
        default=None,
        help="Registro requerido (opcional).",
    )
    parser.add_argument("--timbres", default=None, help="Timbres requeridos separados por coma.")
    parser.add_argument("--dificultad", type=int, default=None, help="Dificultad de 1 a 5.")


# --- Punto de entrada --------------------------------------------------------------


def resolve_data_path(explicit: str | None) -> Path:
    """Precedencia: --datos > variable de entorno > ./catalogo.json."""
    return Path(explicit or os.environ.get(DATA_ENV_VAR) or DEFAULT_DATA_FILE)


def _dispatch(args: argparse.Namespace, catalog: Catalog, now: str) -> tuple[str, bool]:
    if args.command == "voz":
        if args.action == "archivar":
            return _handle_voice_archive(args, catalog, now)
        return _handle_voice(args, catalog, now)
    if args.command == "personaje":
        if args.action == "archivar":
            return _handle_character_archive(args, catalog, now)
        return _handle_character(args, catalog, now)
    if args.command == "prueba":
        return _handle_recording(args, catalog, now)
    return _handle_compatibles(args, catalog, now)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    path = resolve_data_path(args.datos)
    now = _now()

    try:
        catalog = load_catalog(path)
    except StorageError as error:
        print(f"{ERROR_PREFIX} {error.message}", file=sys.stderr)
        return 1

    try:
        output, mutated = _dispatch(args, catalog, now)
    except (ValidationError, NotFoundError, ConfirmationError) as error:
        print(f"{ERROR_PREFIX} {error.message}", file=sys.stderr)
        return 2

    if mutated:
        try:
            save_catalog(catalog, path)
        except StorageError as error:
            print(f"{ERROR_PREFIX} {error.message}", file=sys.stderr)
            return 1

    if output:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
