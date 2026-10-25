"""RF-19 y RF-20: el catálogo de ejemplo carga, se guarda y alimenta el ranking."""

from pathlib import Path

from hokoridub import matching, storage

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "catalogo.json"


def test_sample_catalog_loads_with_expected_content():
    catalog = storage.load_catalog(SAMPLE)

    assert [voice.id for voice in catalog.voices] == ["v-0001", "v-0002", "v-0003", "v-0004"]
    assert [character.id for character in catalog.characters] == ["c-0001", "c-0002", "c-0003"]
    assert sum(len(voice.recordings) for voice in catalog.voices) == 5
    assert catalog.voice("v-0001").recordings[0].id == "r-0001"
    assert catalog.character("c-0002").requirements.register == "tenor"


def test_sample_catalog_preserves_archived_history(tmp_path):
    catalog = storage.load_catalog(SAMPLE)
    target = tmp_path / "catalogo.json"

    storage.save_catalog(catalog, target)
    reloaded = storage.load_catalog(target)

    archived = reloaded.voice("v-0004")
    assert archived.archived_at == "2026-10-01T10:00:00Z"
    assert [recording.id for recording in archived.recordings] == ["r-0005"]


def test_sample_catalog_ranks_kai_first():
    catalog = storage.load_catalog(SAMPLE)

    rows = matching.compatible_voices(catalog, "c-0002")

    assert rows[0][0].id == "v-0002"
    assert rows[0][1] == 80
    assert matching.affinity_level(rows[0][1]) == "alta"
    assert matching.compatible_voices(catalog, "c-0002", min_affinity=80) == rows[:1]
    assert "v-0004" not in [voice.id for voice, _ in rows]
