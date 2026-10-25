"""Cálculo de afinidad entre voces y personajes (RF-16, RF-17)."""

from __future__ import annotations

from dataclasses import replace

from .text import normalize

from .errors import NotFoundError, ValidationError
from .messages import msg
from .models import Catalog, Character, Voice

AGE_POINTS = 40
REGISTER_POINTS = 30
TIMBRE_POINTS = 30

LEVEL_HIGH = 80
LEVEL_MEDIUM = 50


def _age_score(voice: Voice, character: Character) -> int:
    """Solapamiento de edades aparentes, proporcional a la unión (RN-05)."""
    voice_low, voice_high = voice.profile.age_min, voice.profile.age_max
    character_low, character_high = character.requirements.age_min, character.requirements.age_max
    overlap = max(0, min(voice_high, character_high) - max(voice_low, character_low) + 1)
    union = max(voice_high, character_high) - min(voice_low, character_low) + 1
    if union <= 0:
        return 0
    return overlap * AGE_POINTS // union


def affinity(voice: Voice, character: Character) -> int:
    """Puntaje entero de 0 a 100 entre una voz y un personaje (RF-16)."""
    score = _age_score(voice, character)

    required_register = character.requirements.register
    if required_register is None or required_register == voice.profile.register:
        score += REGISTER_POINTS

    required_timbres = set(character.requirements.timbres)
    if required_timbres:
        covered = len(required_timbres & set(voice.profile.timbres))
        score += covered * TIMBRE_POINTS // len(required_timbres)
    else:
        score += TIMBRE_POINTS

    return min(100, max(0, score))


def affinity_level(score: int) -> str:
    """Etiqueta cualitativa de la afinidad: alta, media o baja."""
    if score >= LEVEL_HIGH:
        return "alta"
    if score >= LEVEL_MEDIUM:
        return "media"
    return "baja"


def compatible_voices(
    catalog: Catalog,
    character_id: str,
    *,
    min_affinity: int = 0,
    limit: int | None = None,
) -> list[tuple[Voice, int]]:
    """Voces activas ordenadas por afinidad descendente con un personaje activo (RF-17).

    El desempate es alfabético por nombre normalizado y luego por id, para que
    el resultado sea determinista.
    """
    if not isinstance(min_affinity, int) or isinstance(min_affinity, bool) or not 0 <= min_affinity <= 100:
        raise ValidationError(msg("affinity_range", low=0, high=100))
    if limit is not None and (
        not isinstance(limit, int) or isinstance(limit, bool) or limit < 1
    ):
        raise ValidationError(msg("limit_range"))

    character = catalog.character(character_id)
    if character is None or character.archived_at is not None:
        raise NotFoundError(msg("character_not_found"))

    scored = [
        (voice, affinity(voice, character))
        for voice in catalog.voices
        if voice.archived_at is None
    ]
    scored = [(voice, score) for voice, score in scored if score >= min_affinity]
    scored.sort(key=lambda item: (-item[1], normalize(item[0].name), item[0].id))
    if limit is not None:
        scored = scored[:limit]
    return scored


def with_updates(voice: Voice, **changes: object) -> Voice:
    """Atajo de pruebas: aplica cambios inmutables a una voz."""
    return replace(voice, **changes)
