"""Conversión entre notas musicales y valores MIDI (D3 del plan)."""

import re

from .errors import ValidationError
from .messages import msg

MIDI_MIN = 36  # C2
MIDI_MAX = 96  # C7

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
_BASE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_PATTERN = re.compile(r"^([A-Ga-g])([#b]?)(-?\d+)$")


def note_to_midi(text: str) -> int:
    """Convierte una nota como C4, F#3 o Bb5 a su valor MIDI."""
    match = _PATTERN.match((text or "").strip())
    if not match:
        raise ValidationError(msg("midi_range", low="C2", high="C7"))
    letter, accidental, octave_text = match.groups()
    midi = 12 * (int(octave_text) + 1) + _BASE[letter.upper()]
    if accidental == "#":
        midi += 1
    elif accidental == "b":
        midi -= 1
    if not MIDI_MIN <= midi <= MIDI_MAX:
        raise ValidationError(msg("midi_range", low="C2", high="C7"))
    return midi


def midi_to_note(midi: int) -> str:
    """Convierte un valor MIDI a su nota con sostenidos (C4 = 60)."""
    if not MIDI_MIN <= midi <= MIDI_MAX:
        raise ValidationError(msg("midi_range", low="C2", high="C7"))
    octave, index = divmod(midi, 12)
    return f"{NOTE_NAMES[index]}{octave - 1}"


def format_range(midi_min: int, midi_max: int) -> str:
    """Devuelve la extensión legible, por ejemplo «C3–C5»."""
    return f"{midi_to_note(midi_min)}–{midi_to_note(midi_max)}"
