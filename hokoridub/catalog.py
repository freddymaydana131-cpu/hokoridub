"""Reglas puras del catálogo: altas, edición, archivado y consultas (RF-01 a RF-18)."""

from __future__ import annotations

from dataclasses import replace

from .errors import ConfirmationError, NotFoundError, ValidationError
from .messages import msg
from .models import (
    Catalog,
    Character,
    Recording,
    Voice,
    VoiceProfile,
    VoiceRequirements,
)
from .text import normalize

VOICE_ORDERS = ("nombre", "edad", "actividad")
CHARACTER_ORDERS = ("nombre", "actividad", "dificultad")

STATE_OK = "ok"
STATE_EMPTY = "empty"
STATE_NO_MATCHES = "no_matches"

_PROFILE_FIELDS = ("register", "midi_min", "midi_max", "timbres", "age_min", "age_max", "accents")
_REQUIREMENT_FIELDS = ("register", "timbres", "age_min", "age_max", "difficulty")


# --- Búsqueda de entidades activas -------------------------------------------------


def require_active_voice(catalog: Catalog, voice_id: str) -> Voice:
    """Devuelve la voz si existe y no está archivada (RF-18)."""
    voice = catalog.voice(voice_id)
    if voice is None or voice.archived_at is not None:
        raise NotFoundError(msg("voice_not_found"))
    return voice


def require_active_character(catalog: Catalog, character_id: str) -> Character:
    """Devuelve el personaje si existe y no está archivado (RF-18)."""
    character = catalog.character(character_id)
    if character is None or character.archived_at is not None:
        raise NotFoundError(msg("character_not_found"))
    return character


def active_voices(catalog: Catalog) -> list[Voice]:
    """Voces visibles en el catálogo (RF-01, RF-18)."""
    return [voice for voice in catalog.voices if voice.archived_at is None]


def active_characters(catalog: Catalog) -> list[Character]:
    """Personajes visibles en el catálogo (RF-18)."""
    return [character for character in catalog.characters if character.archived_at is None]


# --- Altas y edición ---------------------------------------------------------------


def _ensure_unique_voice_id(catalog: Catalog, voice_id: str) -> None:
    if any(voice.id == voice_id for voice in catalog.voices):
        raise ValidationError(msg("id_duplicate", id=voice_id))


def _ensure_unique_character_id(catalog: Catalog, character_id: str) -> None:
    if any(character.id == character_id for character in catalog.characters):
        raise ValidationError(msg("id_duplicate", id=character_id))


def _ensure_unique_recording_id(catalog: Catalog, recording_id: str) -> None:
    for voice in catalog.voices:
        if any(recording.id == recording_id for recording in voice.recordings):
            raise ValidationError(msg("id_duplicate", id=recording_id))


def add_voice(
    catalog: Catalog,
    *,
    name: str,
    profile: VoiceProfile,
    languages: tuple[str, ...] | list[str],
    new_id: str,
    now: str,
    stage_name: str | None = None,
    contact: str | None = None,
    notes: str | None = None,
    status: str = "activa",
) -> Voice:
    """Alta de una voz con perfil vocal (RF-01, RF-02)."""
    _ensure_unique_voice_id(catalog, new_id)
    voice = Voice(
        id=new_id,
        name=name,
        profile=profile,
        languages=tuple(languages),
        stage_name=stage_name,
        contact=contact,
        notes=notes,
        status=status,
        created_at=now,
        updated_at=now,
    )
    catalog.voices.append(voice)
    return voice


def edit_voice(catalog: Catalog, voice_id: str, *, changes: dict, now: str) -> Voice:
    """Edición del perfil o los datos de una voz activa (RF-03)."""
    voice = require_active_voice(catalog, voice_id)
    profile = voice.profile
    if any(field in changes for field in _PROFILE_FIELDS):
        profile = replace(
            voice.profile,
            **{field: changes[field] for field in _PROFILE_FIELDS if field in changes},
        )
    updated = replace(
        voice,
        name=changes.get("name", voice.name),
        stage_name=changes["stage_name"] if "stage_name" in changes else voice.stage_name,
        contact=changes["contact"] if "contact" in changes else voice.contact,
        notes=changes["notes"] if "notes" in changes else voice.notes,
        status=changes.get("status", voice.status),
        languages=tuple(changes["languages"]) if "languages" in changes else voice.languages,
        profile=profile,
        updated_at=now,
    )
    catalog.voices = [updated if item.id == voice_id else item for item in catalog.voices]
    return updated


def archive_voice(catalog: Catalog, voice_id: str, *, confirmed: bool, now: str) -> Voice:
    """Archivado lógico de una voz; conserva sus pruebas (RF-18, RN-02)."""
    voice = require_active_voice(catalog, voice_id)
    if not confirmed:
        raise ConfirmationError(msg("confirmation_required"))
    archived = replace(voice, archived_at=now, updated_at=now)
    catalog.voices = [archived if item.id == voice_id else item for item in catalog.voices]
    return archived


def add_character(
    catalog: Catalog,
    *,
    name: str,
    work: str,
    kind: str,
    description: str,
    requirements: VoiceRequirements,
    new_id: str,
    now: str,
) -> Character:
    """Alta de un personaje con descripción y requisitos de voz (RF-04, RF-05)."""
    _ensure_unique_character_id(catalog, new_id)
    character = Character(
        id=new_id,
        name=name,
        work=work,
        kind=kind,
        description=description,
        requirements=requirements,
        created_at=now,
        updated_at=now,
    )
    catalog.characters.append(character)
    return character


def edit_character(catalog: Catalog, character_id: str, *, changes: dict, now: str) -> Character:
    """Edición de un personaje activo (RF-06)."""
    character = require_active_character(catalog, character_id)
    requirements = character.requirements
    if any(field in changes for field in _REQUIREMENT_FIELDS):
        requirements = replace(
            character.requirements,
            **{field: changes[field] for field in _REQUIREMENT_FIELDS if field in changes},
        )
    updated = replace(
        character,
        name=changes.get("name", character.name),
        work=changes.get("work", character.work),
        kind=changes.get("kind", character.kind),
        description=changes.get("description", character.description),
        requirements=requirements,
        updated_at=now,
    )
    catalog.characters = [updated if item.id == character_id else item for item in catalog.characters]
    return updated


def archive_character(catalog: Catalog, character_id: str, *, confirmed: bool, now: str) -> Character:
    """Archivado lógico de un personaje; conserva las pruebas históricas (RF-18, RN-02)."""
    character = require_active_character(catalog, character_id)
    if not confirmed:
        raise ConfirmationError(msg("confirmation_required"))
    archived = replace(character, archived_at=now, updated_at=now)
    catalog.characters = [archived if item.id == character_id else item for item in catalog.characters]
    return archived


# --- Pruebas -----------------------------------------------------------------------


def add_recording(
    catalog: Catalog,
    *,
    voice_id: str,
    character_id: str,
    kind: str,
    new_id: str,
    now: str,
    link: str | None = None,
    duration_seconds: int | None = None,
    rating: int | None = None,
    comment: str | None = None,
    recorded_at: str | None = None,
) -> Recording:
    """Registra una prueba de una voz activa sobre un personaje activo (RF-07, RN-03)."""
    voice = require_active_voice(catalog, voice_id)
    require_active_character(catalog, character_id)
    _ensure_unique_recording_id(catalog, new_id)
    recording = Recording(
        id=new_id,
        character_id=character_id,
        kind=kind,
        recorded_at=recorded_at or now,
        link=link,
        duration_seconds=duration_seconds,
        rating=rating,
        comment=comment,
        created_at=now,
        updated_at=now,
    )
    updated = replace(voice, recordings=voice.recordings + (recording,), updated_at=now)
    catalog.voices = [updated if item.id == voice_id else item for item in catalog.voices]
    return recording


def find_recording(voice: Voice, recording_id: str) -> Recording:
    """Busca una prueba dentro del portafolio de una voz."""
    recording = next((item for item in voice.recordings if item.id == recording_id), None)
    if recording is None:
        raise NotFoundError(msg("recording_not_found"))
    return recording


def edit_recording(
    catalog: Catalog,
    *,
    voice_id: str,
    recording_id: str,
    changes: dict,
    now: str,
) -> Recording:
    """Edita una prueba conservando su fecha de creación (RF-09)."""
    voice = require_active_voice(catalog, voice_id)
    current = find_recording(voice, recording_id)
    updated_recording = replace(
        current,
        kind=changes.get("kind", current.kind),
        link=changes["link"] if "link" in changes else current.link,
        duration_seconds=(
            changes["duration_seconds"] if "duration_seconds" in changes else current.duration_seconds
        ),
        rating=changes["rating"] if "rating" in changes else current.rating,
        comment=changes["comment"] if "comment" in changes else current.comment,
        updated_at=now,
    )
    recordings = tuple(
        updated_recording if item.id == recording_id else item for item in voice.recordings
    )
    updated_voice = replace(voice, recordings=recordings, updated_at=now)
    catalog.voices = [updated_voice if item.id == voice_id else item for item in catalog.voices]
    return updated_recording


# --- Consultas ---------------------------------------------------------------------


def last_activity(voice: Voice) -> str:
    """Fecha más reciente de la voz o de sus pruebas (RF-14)."""
    dates = [voice.created_at, voice.updated_at]
    for recording in voice.recordings:
        dates.extend([recording.recorded_at, recording.created_at, recording.updated_at])
    return max(dates)


def _sorted_by_name(voices: list[Voice]) -> list[Voice]:
    return sorted(voices, key=lambda voice: (normalize(voice.name), voice.id))


def sort_voices(voices: list[Voice], order: str) -> list[Voice]:
    """Ordena voces por nombre, edad mínima o última actividad (RF-14)."""
    if order not in VOICE_ORDERS:
        raise ValidationError(msg("order_invalid", value=order, options=", ".join(VOICE_ORDERS)))
    ordered = _sorted_by_name(voices)
    if order == "edad":
        ordered.sort(key=lambda voice: (voice.profile.age_min, normalize(voice.name), voice.id))
    elif order == "actividad":
        ordered.sort(key=last_activity, reverse=True)
    return ordered


def sort_characters(characters: list[Character], order: str) -> list[Character]:
    """Ordena personajes por nombre, actividad o dificultad (RF-14)."""
    if order not in CHARACTER_ORDERS:
        raise ValidationError(msg("order_invalid", value=order, options=", ".join(CHARACTER_ORDERS)))
    ordered = sorted(characters, key=lambda character: (normalize(character.name), character.id))
    if order == "actividad":
        ordered.sort(key=lambda character: character.updated_at, reverse=True)
    elif order == "dificultad":
        ordered.sort(
            key=lambda character: (
                -character.requirements.difficulty,
                normalize(character.name),
                character.id,
            )
        )
    return ordered


def voice_view(
    catalog: Catalog,
    *,
    text: str = "",
    register: str | None = None,
    timbre: str | None = None,
    status: str | None = None,
    language: str | None = None,
    order: str = "nombre",
) -> tuple[str, list[Voice]]:
    """Vista del catálogo de voces con búsqueda, filtros y orden (RF-11 a RF-14)."""
    voices = active_voices(catalog)
    if not voices:
        return STATE_EMPTY, []

    query = normalize(text)
    if query:
        voices = [
            voice
            for voice in voices
            if query in normalize(voice.name)
            or (voice.stage_name is not None and query in normalize(voice.stage_name))
            or (voice.notes is not None and query in normalize(voice.notes))
        ]
    if register is not None:
        voices = [voice for voice in voices if voice.profile.register == register]
    if timbre is not None:
        voices = [voice for voice in voices if timbre in voice.profile.timbres]
    if status is not None:
        voices = [voice for voice in voices if voice.status == status]
    if language is not None:
        marker = normalize(language)
        voices = [voice for voice in voices if any(normalize(item) == marker for item in voice.languages)]

    if not voices:
        return STATE_NO_MATCHES, []
    return STATE_OK, sort_voices(voices, order)


def character_view(
    catalog: Catalog,
    *,
    text: str = "",
    kind: str | None = None,
    register: str | None = None,
    order: str = "nombre",
) -> tuple[str, list[Character]]:
    """Vista del catálogo de personajes con búsqueda, filtros y orden (RF-11 a RF-14)."""
    characters = active_characters(catalog)
    if not characters:
        return STATE_EMPTY, []

    query = normalize(text)
    if query:
        characters = [
            character
            for character in characters
            if query in normalize(character.name)
            or query in normalize(character.work)
            or query in normalize(character.description)
        ]
    if kind is not None:
        characters = [character for character in characters if character.kind == kind]
    if register is not None:
        characters = [
            character for character in characters if character.requirements.register == register
        ]

    if not characters:
        return STATE_NO_MATCHES, []
    return STATE_OK, sort_characters(characters, order)


def portfolio(catalog: Catalog, voice: Voice) -> list[tuple[Recording, Character | None]]:
    """Pruebas de una voz de la más reciente a la más antigua (RF-10)."""
    rows = [(recording, catalog.character(recording.character_id)) for recording in voice.recordings]
    rows.sort(key=lambda row: (row[0].recorded_at, row[0].id), reverse=True)
    return rows


def recording_rows(
    catalog: Catalog,
    *,
    voice_id: str | None = None,
    character_id: str | None = None,
    kind: str | None = None,
) -> list[tuple[Recording, Voice, Character | None]]:
    """Listado de pruebas de voces activas, filtrable (RF-07, RF-11)."""
    rows: list[tuple[Recording, Voice, Character | None]] = []
    for voice in active_voices(catalog):
        if voice_id is not None and voice.id != voice_id:
            continue
        for recording in voice.recordings:
            if character_id is not None and recording.character_id != character_id:
                continue
            if kind is not None and recording.kind != kind:
                continue
            rows.append((recording, voice, catalog.character(recording.character_id)))
    rows.sort(key=lambda row: (row[0].recorded_at, row[0].id), reverse=True)
    return rows


def character_recording_count(catalog: Catalog, character_id: str) -> int:
    """Cantidad de pruebas de voces activas que referencian un personaje."""
    return sum(
        1
        for voice in active_voices(catalog)
        for recording in voice.recordings
        if recording.character_id == character_id
    )
