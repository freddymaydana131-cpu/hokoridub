"""Constructores de datos válidos para las pruebas."""

from hokoridub.models import (
    Catalog,
    Character,
    Recording,
    Voice,
    VoiceProfile,
    VoiceRequirements,
)

NOW = "2026-10-25T10:00:00Z"


def make_profile(
    *,
    register: str = "mezzosoprano",
    midi_min: int = 55,
    midi_max: int = 79,
    timbres: tuple[str, ...] = ("dulce", "calido"),
    age_min: int = 18,
    age_max: int = 35,
    accents: tuple[str, ...] = ("neutro",),
) -> VoiceProfile:
    return VoiceProfile(
        register=register,
        midi_min=midi_min,
        midi_max=midi_max,
        timbres=timbres,
        age_min=age_min,
        age_max=age_max,
        accents=accents,
    )


def make_voice(
    voice_id: str = "v-1",
    name: str = "Ana Torres",
    *,
    stage_name: str | None = None,
    contact: str | None = None,
    languages: tuple[str, ...] = ("es", "en"),
    profile: VoiceProfile | None = None,
    notes: str | None = None,
    status: str = "activa",
    created_at: str = NOW,
    updated_at: str = NOW,
    archived_at: str | None = None,
    recordings: tuple[Recording, ...] = (),
) -> Voice:
    return Voice(
        id=voice_id,
        name=name,
        stage_name=stage_name,
        contact=contact,
        languages=languages,
        profile=profile or make_profile(),
        notes=notes,
        status=status,
        created_at=created_at,
        updated_at=updated_at,
        archived_at=archived_at,
        recordings=recordings,
    )


def make_character(
    character_id: str = "c-1",
    name: str = "Maya",
    *,
    work: str = "Serie X",
    kind: str = "animacion",
    description: str = "Niña curiosa de voz brillante.",
    register: str | None = "mezzosoprano",
    timbres: tuple[str, ...] = ("dulce", "calido"),
    age_min: int = 18,
    age_max: int = 35,
    difficulty: int = 3,
    created_at: str = NOW,
    updated_at: str = NOW,
    archived_at: str | None = None,
) -> Character:
    return Character(
        id=character_id,
        name=name,
        work=work,
        kind=kind,
        description=description,
        requirements=VoiceRequirements(
            register=register,
            timbres=timbres,
            age_min=age_min,
            age_max=age_max,
            difficulty=difficulty,
        ),
        created_at=created_at,
        updated_at=updated_at,
        archived_at=archived_at,
    )


def make_recording(
    recording_id: str = "r-1",
    character_id: str = "c-1",
    *,
    kind: str = "demo",
    recorded_at: str = NOW,
    link: str | None = "https://example.com/demo.mp3",
    duration_seconds: int | None = 45,
    rating: int | None = 5,
    comment: str | None = "Prueba inicial.",
    created_at: str = NOW,
    updated_at: str = NOW,
) -> Recording:
    return Recording(
        id=recording_id,
        character_id=character_id,
        kind=kind,
        recorded_at=recorded_at,
        link=link,
        duration_seconds=duration_seconds,
        rating=rating,
        comment=comment,
        created_at=created_at,
        updated_at=updated_at,
    )


def make_catalog(
    voices: tuple[Voice, ...] = (),
    characters: tuple[Character, ...] = (),
) -> Catalog:
    return Catalog(voices=list(voices), characters=list(characters))
