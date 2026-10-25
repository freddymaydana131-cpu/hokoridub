"""Normalización de texto para búsquedas (RF-12)."""

import re
import unicodedata

_SPACES = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Pasa a minúsculas, quita tildes, recorta y colapsa espacios.

    La eñe se trata como «n» porque la tilde forma parte de los diacríticos
    que se eliminan; es una decisión documentada en la spec (RF-12).
    """
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return _SPACES.sub(" ", without_marks.lower()).strip()


def contains(haystack: str, needle: str) -> bool:
    """Indica si `needle` aparece en `haystack` sin distinguir tildes ni mayúsculas."""
    return normalize(needle) in normalize(haystack)
