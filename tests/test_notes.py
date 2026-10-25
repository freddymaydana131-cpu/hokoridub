"""D3 del plan: conversión de notas musicales a MIDI."""

import pytest

from hokoridub.errors import ValidationError
from hokoridub.notes import format_range, midi_to_note, note_to_midi


def test_notas_basicas():
    assert note_to_midi("C4") == 60
    assert note_to_midi("A4") == 69
    assert note_to_midi("C3") == 48


def test_sostenidos_y_bemoles():
    assert note_to_midi("C#4") == 61
    assert note_to_midi("Db4") == 61
    assert note_to_midi("Bb3") == 58


def test_midi_a_nota():
    assert midi_to_note(60) == "C4"
    assert midi_to_note(61) == "C#4"
    assert midi_to_note(48) == "C3"


def test_formato_de_extension():
    assert format_range(48, 72) == "C3–C5"


@pytest.mark.parametrize("value", ["H4", "", "C", "C4x"])
def test_nota_invalida(value):
    with pytest.raises(ValidationError):
        note_to_midi(value)


@pytest.mark.parametrize("value", ["C1", "C8"])
def test_nota_fuera_de_rango(value):
    with pytest.raises(ValidationError):
        note_to_midi(value)


def test_midi_fuera_de_rango():
    with pytest.raises(ValidationError):
        midi_to_note(20)
