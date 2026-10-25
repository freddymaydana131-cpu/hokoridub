"""Persistencia en un único archivo JSON versionado (RF-19, RF-20)."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .errors import StorageError, ValidationError
from .messages import msg
from .models import Catalog, Character, Recording, Voice, VoiceProfile, VoiceRequirements

SCHEMA_VERSION = 1


def _voice_to_dict(voice: Voice) -> dict:
    return {
        "id": voice.id,
        "name": voice.name,
        "stage_name": voice.stage_name,
        "contact": voice.contact,
        "languages": list(voice.languages),
        "profile": {
            "register": voice.profile.register,
            "midi_min": voice.profile.midi_min,
            "midi_max": voice.profile.midi_max,
            "timbres": list(voice.profile.timbres),
            "age_min": voice.profile.age_min,
            "age_max": voice.profile.age_max,
            "accents": list(voice.profile.accents),
        },
        "notes": voice.notes,
        "status": voice.status,
        "created_at": voice.created_at,
        "updated_at": voice.updated_at,
        "archived_at": voice.archived_at,
        "recordings": [_recording_to_dict(item) for item in voice.recordings],
    }


def _recording_to_dict(recording: Recording) -> dict:
    return {
        "id": recording.id,
        "character_id": recording.character_id,
        "kind": recording.kind,
        "recorded_at": recording.recorded_at,
        "link": recording.link,
        "duration_seconds": recording.duration_seconds,
        "rating": recording.rating,
        "comment": recording.comment,
        "created_at": recording.created_at,
        "updated_at": recording.updated_at,
    }


def _character_to_dict(character: Character) -> dict:
    return {
        "id": character.id,
        "name": character.name,
        "work": character.work,
        "kind": character.kind,
        "description": character.description,
        "requirements": {
            "register": character.requirements.register,
            "timbres": list(character.requirements.timbres),
            "age_min": character.requirements.age_min,
            "age_max": character.requirements.age_max,
            "difficulty": character.requirements.difficulty,
        },
        "created_at": character.created_at,
        "updated_at": character.updated_at,
        "archived_at": character.archived_at,
    }


def _recording_from_dict(data: dict) -> Recording:
    return Recording(
        id=data["id"],
        character_id=data["character_id"],
        kind=data["kind"],
        recorded_at=data["recorded_at"],
        link=data.get("link"),
        duration_seconds=data.get("duration_seconds"),
        rating=data.get("rating"),
        comment=data.get("comment"),
        created_at=data["created_at"],
        updated_at=data["updated_at"],
    )


def _voice_from_dict(data: dict) -> Voice:
    profile_data = data["profile"]
    profile = VoiceProfile(
        register=profile_data["register"],
        midi_min=profile_data["midi_min"],
        midi_max=profile_data["midi_max"],
        timbres=tuple(profile_data.get("timbres", [])),
        age_min=profile_data["age_min"],
        age_max=profile_data["age_max"],
        accents=tuple(profile_data.get("accents", [])),
    )
    return Voice(
        id=data["id"],
        name=data["name"],
        stage_name=data.get("stage_name"),
        contact=data.get("contact"),
        languages=tuple(data["languages"]),
        profile=profile,
        notes=data.get("notes"),
        status=data.get("status", "activa"),
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        archived_at=data.get("archived_at"),
        recordings=tuple(_recording_from_dict(item) for item in data.get("recordings", [])),
    )


def _character_from_dict(data: dict) -> Character:
    requirements_data = data["requirements"]
    requirements = VoiceRequirements(
        register=requirements_data.get("register"),
        timbres=tuple(requirements_data.get("timbres", [])),
        age_min=requirements_data["age_min"],
        age_max=requirements_data["age_max"],
        difficulty=requirements_data.get("difficulty", 3),
    )
    return Character(
        id=data["id"],
        name=data["name"],
        work=data["work"],
        kind=data["kind"],
        description=data["description"],
        requirements=requirements,
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        archived_at=data.get("archived_at"),
    )


def _validate_references(catalog: Catalog) -> None:
    character_ids = {character.id for character in catalog.characters}
    for voice in catalog.voices:
        for recording in voice.recordings:
            if recording.character_id not in character_ids:
                raise StorageError(msg("storage_reference"))


def _validate_unique_ids(catalog: Catalog) -> None:
    voice_ids = [voice.id for voice in catalog.voices]
    character_ids = [character.id for character in catalog.characters]
    recording_ids = [
        recording.id for voice in catalog.voices for recording in voice.recordings
    ]
    for values in (voice_ids, character_ids, recording_ids):
        if len(values) != len(set(values)):
            raise StorageError(msg("storage_duplicate"))


def load_catalog(path: str | os.PathLike[str]) -> Catalog:
    """Carga el catálogo; si el archivo no existe, devuelve uno vacío (RF-20)."""
    file_path = Path(path)
    if not file_path.exists():
        return Catalog()

    try:
        raw = file_path.read_text(encoding="utf-8")
    except OSError as error:
        raise StorageError(msg("storage_unreadable", detail=str(error))) from error

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise StorageError(msg("storage_invalid_json")) from error

    if not isinstance(data, dict):
        raise StorageError(msg("storage_structure"))
    version = data.get("schema_version")
    if isinstance(version, bool) or version != SCHEMA_VERSION:
        raise StorageError(msg("storage_schema", expected=SCHEMA_VERSION))
    if not isinstance(data.get("voices"), list) or not isinstance(data.get("characters"), list):
        raise StorageError(msg("storage_structure"))

    try:
        catalog = Catalog(
            voices=[_voice_from_dict(item) for item in data["voices"]],
            characters=[_character_from_dict(item) for item in data["characters"]],
        )
    except (KeyError, TypeError, AttributeError, ValidationError) as error:
        raise StorageError(f"{msg('storage_structure')} {error}") from error

    _validate_unique_ids(catalog)
    _validate_references(catalog)
    return catalog


def catalog_to_dict(catalog: Catalog) -> dict:
    """Representación JSON del catálogo completo (RF-19)."""
    return {
        "schema_version": SCHEMA_VERSION,
        "voices": [_voice_to_dict(voice) for voice in catalog.voices],
        "characters": [_character_to_dict(character) for character in catalog.characters],
    }


def _atomic_write(file_path: Path, content: str) -> None:
    """Escritura atómica: temporal en el mismo directorio, fsync y os.replace (RF-19)."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        dir=str(file_path.parent), prefix=f".{file_path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, file_path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def save_catalog(catalog: Catalog, path: str | os.PathLike[str]) -> None:
    """Guarda todo el catálogo de forma atómica (RF-19)."""
    file_path = Path(path)
    content = json.dumps(catalog_to_dict(catalog), ensure_ascii=False, indent=2) + "\n"
    try:
        _atomic_write(file_path, content)
    except OSError as error:
        raise StorageError(msg("storage_write", detail=str(error))) from error
