"""Entidades del catálogo y validaciones (RF-02, RF-05, RF-08)."""

from __future__ import annotations

from dataclasses import dataclass, field

from .errors import ValidationError
from .messages import msg
from .notes import MIDI_MAX, MIDI_MIN
from .text import normalize

REGISTERS = ("soprano", "mezzosoprano", "contralto", "tenor", "baritono", "bajo")
TIMBRES = ("dulce", "nasal", "rasposo", "metalico", "calido", "brillante", "opaco", "infantil")
STATUSES = ("activa", "en_pausa", "egresada")
CHARACTER_KINDS = ("animacion", "videojuego", "audiolibro", "doblaje")
RECORDING_KINDS = ("demo", "audicion", "practica")

AGE_MIN, AGE_MAX = 5, 90
NAME_LIMIT, STAGE_NAME_LIMIT, CONTACT_LIMIT, NOTES_LIMIT = 120, 120, 120, 500
CHARACTER_NAME_LIMIT, WORK_LIMIT, DESCRIPTION_LIMIT = 150, 150, 1000
LINK_LIMIT, COMMENT_LIMIT = 500, 500
MAX_TIMBRES, MAX_LANGUAGES, MAX_ACCENTS = 3, 5, 5
DURATION_MIN, DURATION_MAX = 1, 3600
RATING_MIN, RATING_MAX = 1, 5
DIFFICULTY_MIN, DIFFICULTY_MAX = 1, 5


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _required_text(value: object, required_key: str, limit_key: str, limit: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(msg(required_key))
    cleaned = value.strip()
    if len(cleaned) > limit:
        raise ValidationError(msg(limit_key, limit=limit))
    return cleaned


def _optional_text(value: object, limit_key: str, limit: int) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError(msg(limit_key, limit=limit))
    cleaned = value.strip()
    if not cleaned:
        return None
    if len(cleaned) > limit:
        raise ValidationError(msg(limit_key, limit=limit))
    return cleaned


def _int_in_range(value: object, low: int, high: int, key: str) -> int:
    if not _is_int(value) or not low <= value <= high:
        raise ValidationError(msg(key, low=low, high=high))
    return value


def _enum(value: object, options: tuple[str, ...], key: str) -> str:
    if not isinstance(value, str) or value not in options:
        raise ValidationError(msg(key, value=value, options=", ".join(options)))
    return value


def _unique_list(
    values: object,
    *,
    max_items: int,
    max_key: str,
    item_min: int,
    item_max: int,
    invalid_key: str,
    duplicate_key: str,
) -> tuple[str, ...]:
    if values is None:
        values = ()
    if not isinstance(values, (list, tuple)):
        raise ValidationError(msg(invalid_key, value=values))
    if len(values) > max_items:
        raise ValidationError(msg(max_key, limit=max_items))
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in values:
        if not isinstance(raw, str):
            raise ValidationError(msg(invalid_key, value=raw))
        item = raw.strip()
        if not item_min <= len(item) <= item_max:
            raise ValidationError(msg(invalid_key, value=raw))
        marker = normalize(item)
        if marker in seen:
            raise ValidationError(msg(duplicate_key, value=item))
        seen.add(marker)
        cleaned.append(item)
    return tuple(cleaned)


def _timbres(value: object) -> tuple[str, ...]:
    if value is None:
        value = ()
    if not isinstance(value, (list, tuple)):
        raise ValidationError(msg("timbre_invalid", value=value, options=", ".join(TIMBRES)))
    if len(value) > MAX_TIMBRES:
        raise ValidationError(msg("timbres_too_many", limit=MAX_TIMBRES))
    cleaned: list[str] = []
    for raw in value:
        if raw not in TIMBRES:
            raise ValidationError(msg("timbre_invalid", value=raw, options=", ".join(TIMBRES)))
        if raw in cleaned:
            raise ValidationError(msg("timbre_duplicate", value=raw))
        cleaned.append(raw)
    return tuple(cleaned)


def _age_range(age_min: object, age_max: object) -> tuple[int, int]:
    low = _int_in_range(age_min, AGE_MIN, AGE_MAX, "age_range")
    high = _int_in_range(age_max, AGE_MIN, AGE_MAX, "age_range")
    if low > high:
        raise ValidationError(msg("age_order"))
    return low, high


@dataclass(frozen=True)
class VoiceProfile:
    """Perfil vocal de una persona (RF-02)."""

    register: str
    midi_min: int
    midi_max: int
    timbres: tuple[str, ...] = ()
    age_min: int = 18
    age_max: int = 60
    accents: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _enum(self.register, REGISTERS, "register_invalid")
        low = _int_in_range(self.midi_min, MIDI_MIN, MIDI_MAX, "midi_range")
        high = _int_in_range(self.midi_max, MIDI_MIN, MIDI_MAX, "midi_range")
        if low >= high:
            raise ValidationError(msg("extension_order"))
        object.__setattr__(self, "timbres", _timbres(self.timbres))
        low_age, high_age = _age_range(self.age_min, self.age_max)
        object.__setattr__(self, "age_min", low_age)
        object.__setattr__(self, "age_max", high_age)
        object.__setattr__(
            self,
            "accents",
            _unique_list(
                self.accents,
                max_items=MAX_ACCENTS,
                max_key="accents_too_many",
                item_min=1,
                item_max=40,
                invalid_key="accent_invalid",
                duplicate_key="accent_duplicate",
            ),
        )


@dataclass(frozen=True)
class Recording:
    """Prueba de voz vinculada a un personaje (RF-07, RF-08)."""

    id: str
    character_id: str
    kind: str
    recorded_at: str
    link: str | None = None
    duration_seconds: int | None = None
    rating: int | None = None
    comment: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _required_text(self.id, "id_required", "id_required", 200))
        object.__setattr__(
            self,
            "character_id",
            _required_text(self.character_id, "id_required", "id_required", 200),
        )
        _enum(self.kind, RECORDING_KINDS, "recording_kind_invalid")
        object.__setattr__(
            self,
            "recorded_at",
            _required_text(self.recorded_at, "recorded_at_required", "recorded_at_required", 40),
        )
        link = _optional_text(self.link, "link_too_long", LINK_LIMIT)
        if link is not None and not link.startswith(("http://", "https://")):
            raise ValidationError(msg("link_invalid"))
        object.__setattr__(self, "link", link)
        if self.duration_seconds is not None:
            _int_in_range(self.duration_seconds, DURATION_MIN, DURATION_MAX, "duration_range")
        if self.rating is not None:
            _int_in_range(self.rating, RATING_MIN, RATING_MAX, "rating_range")
        object.__setattr__(self, "comment", _optional_text(self.comment, "comment_too_long", COMMENT_LIMIT))
        object.__setattr__(
            self, "created_at", _required_text(self.created_at, "recorded_at_required", "recorded_at_required", 40)
        )
        object.__setattr__(
            self, "updated_at", _required_text(self.updated_at, "recorded_at_required", "recorded_at_required", 40)
        )


@dataclass(frozen=True)
class Voice:
    """Persona del catálogo con su perfil vocal y su portafolio."""

    id: str
    name: str
    profile: VoiceProfile
    languages: tuple[str, ...]
    stage_name: str | None = None
    contact: str | None = None
    notes: str | None = None
    status: str = "activa"
    created_at: str = ""
    updated_at: str = ""
    archived_at: str | None = None
    recordings: tuple[Recording, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _required_text(self.id, "id_required", "id_required", 200))
        object.__setattr__(
            self, "name", _required_text(self.name, "voice_name_required", "voice_name_too_long", NAME_LIMIT)
        )
        object.__setattr__(
            self, "stage_name", _optional_text(self.stage_name, "stage_name_too_long", STAGE_NAME_LIMIT)
        )
        object.__setattr__(self, "contact", _optional_text(self.contact, "contact_too_long", CONTACT_LIMIT))
        object.__setattr__(self, "notes", _optional_text(self.notes, "notes_too_long", NOTES_LIMIT))
        object.__setattr__(
            self,
            "languages",
            _unique_list(
                self.languages,
                max_items=MAX_LANGUAGES,
                max_key="languages_too_many",
                item_min=2,
                item_max=20,
                invalid_key="language_invalid",
                duplicate_key="language_duplicate",
            ),
        )
        if not self.languages:
            raise ValidationError(msg("languages_required"))
        _enum(self.status, STATUSES, "status_invalid")
        if not isinstance(self.profile, VoiceProfile):
            raise ValidationError(msg("register_invalid", value=self.profile, options=", ".join(REGISTERS)))
        object.__setattr__(
            self, "created_at", _required_text(self.created_at, "recorded_at_required", "recorded_at_required", 40)
        )
        object.__setattr__(
            self, "updated_at", _required_text(self.updated_at, "recorded_at_required", "recorded_at_required", 40)
        )
        object.__setattr__(self, "recordings", tuple(self.recordings))


@dataclass(frozen=True)
class VoiceRequirements:
    """Requisitos vocales que debe cumplir quien interprete a un personaje (RF-05)."""

    age_min: int
    age_max: int
    register: str | None = None
    timbres: tuple[str, ...] = ()
    difficulty: int = 3

    def __post_init__(self) -> None:
        if self.register is not None:
            _enum(self.register, REGISTERS, "register_invalid")
        object.__setattr__(self, "timbres", _timbres(self.timbres))
        low, high = _age_range(self.age_min, self.age_max)
        object.__setattr__(self, "age_min", low)
        object.__setattr__(self, "age_max", high)
        _int_in_range(self.difficulty, DIFFICULTY_MIN, DIFFICULTY_MAX, "difficulty_range")


@dataclass(frozen=True)
class Character:
    """Personaje con la descripción y los requisitos de su voz (RF-04, RF-05)."""

    id: str
    name: str
    work: str
    kind: str
    description: str
    requirements: VoiceRequirements
    created_at: str = ""
    updated_at: str = ""
    archived_at: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _required_text(self.id, "id_required", "id_required", 200))
        object.__setattr__(
            self,
            "name",
            _required_text(self.name, "character_name_required", "character_name_too_long", CHARACTER_NAME_LIMIT),
        )
        object.__setattr__(self, "work", _required_text(self.work, "work_required", "work_too_long", WORK_LIMIT))
        _enum(self.kind, CHARACTER_KINDS, "kind_invalid")
        object.__setattr__(
            self,
            "description",
            _required_text(
                self.description, "description_required", "description_too_long", DESCRIPTION_LIMIT
            ),
        )
        if not isinstance(self.requirements, VoiceRequirements):
            raise ValidationError(msg("difficulty_range", low=DIFFICULTY_MIN, high=DIFFICULTY_MAX))
        object.__setattr__(
            self, "created_at", _required_text(self.created_at, "recorded_at_required", "recorded_at_required", 40)
        )
        object.__setattr__(
            self, "updated_at", _required_text(self.updated_at, "recorded_at_required", "recorded_at_required", 40)
        )


@dataclass
class Catalog:
    """Contenedor mutable del catálogo completo."""

    voices: list[Voice] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)

    def voice(self, voice_id: str) -> Voice | None:
        return next((v for v in self.voices if v.id == voice_id), None)

    def character(self, character_id: str) -> Character | None:
        return next((c for c in self.characters if c.id == character_id), None)

    def recording(self, recording_id: str) -> Recording | None:
        for voice in self.voices:
            for recording in voice.recordings:
                if recording.id == recording_id:
                    return recording
        return None
