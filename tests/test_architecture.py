"""Verifica que se cumplan los principios de la constitución."""

import ast
import re
from pathlib import Path

from hokoridub.messages import MESSAGES

PACKAGE = Path(__file__).resolve().parents[1] / "hokoridub"

PURE_MODULES = (
    "messages.py",
    "errors.py",
    "text.py",
    "notes.py",
    "models.py",
    "storage.py",
    "catalog.py",
    "matching.py",
)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            prefix = "." * node.level
            names.add(prefix + node.module.split(".")[0])
    return names


def test_principio3_la_logica_no_conoce_la_interfaz():
    forbidden = {"cli", "argparse", "sys"}
    for name in ("models.py", "catalog.py", "matching.py", "notes.py", "text.py"):
        assert not (_imports(PACKAGE / name) & forbidden), name


def test_principio5_persistencia_aislada():
    with_files = {"storage.py"}
    tokens = ("read_text(", "write_text(", "os.replace(", "tempfile.mkstemp(", "open(")
    for path in PACKAGE.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for token in tokens:
            if path.name in with_files:
                continue
            assert token not in source, f"{path.name} usa {token}"


def test_principio5_json_solo_en_storage():
    for path in PACKAGE.glob("*.py"):
        if path.name == "storage.py":
            continue
        assert "json" not in _imports(path), path.name


def test_principio3_solo_la_cli_imprime():
    for path in PACKAGE.glob("*.py"):
        if path.name in {"cli.py", "__main__.py"}:
            continue
        assert "print(" not in path.read_text(encoding="utf-8"), path.name


def test_principio6_todas_las_claves_de_mensaje_existen():
    for path in PACKAGE.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        for key in re.findall(r'msg\("([a-z_]+)"', source):
            assert key in MESSAGES, f"{path.name} usa la clave inexistente {key}"


def test_principio1_solo_biblioteca_estandar_en_el_paquete():
    standard = {
        "__future__",
        "argparse",
        "dataclasses",
        "datetime",
        "json",
        "os",
        "re",
        "sys",
        "tempfile",
        "unicodedata",
        "uuid",
        "pathlib",
        "typing",
        "collections",
    }
    for path in PACKAGE.glob("*.py"):
        external = {
            name
            for name in _imports(path)
            if not name.startswith(".") and name not in standard
        }
        assert external == set(), f"{path.name} importa {external}"


def test_principio2_la_logica_cita_requisitos():
    for name in ("catalog.py", "matching.py"):
        source = (PACKAGE / name).read_text(encoding="utf-8")
        assert "RF-" in source, name


def test_principio4_existen_pruebas_por_requisito():
    tests = Path(__file__).resolve().parent
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in tests.glob("test_*.py")
    ).lower()
    for number in range(1, 21):
        pattern = re.compile(rf"rf[-_]?{number:02d}")
        assert pattern.search(source), f"Falta trazabilidad de RF-{number:02d}"
