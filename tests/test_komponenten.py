"""Checks on the library blocks that work without Langflow installed, by reading their source."""

import ast
from pathlib import Path

import pytest

KOMPONENTEN = Path(__file__).resolve().parent.parent / "komponenten" / "bibliothek"

# The blocks that call Crossref, OpenAlex or Unpaywall, which all treat requests with a contact address better
MIT_KONTAKT = ["referenzen_pruefen.py", "quellen_anreichern.py", "openalex_suche.py", "volltexte_holen.py"]


def _baum(datei: str) -> ast.Module:
    return ast.parse((KOMPONENTEN / datei).read_text(encoding="utf-8"))


def _schluesselwoerter(aufruf: ast.Call) -> dict:
    return {k.arg: ast.literal_eval(k.value) for k in aufruf.keywords if isinstance(k.value, ast.Constant)}


@pytest.mark.parametrize("datei", MIT_KONTAKT)
def test_contact_email_comes_from_the_groups_global_variable(datei):
    felder = [
        _schluesselwoerter(knoten)
        for knoten in ast.walk(_baum(datei))
        if isinstance(knoten, ast.Call) and getattr(knoten.func, "id", None) == "SecretStrInput"
    ]
    feld = next(f for f in felder if f.get("name") == "kontakt_email")
    assert feld["value"] == "KONTAKT_EMAIL"
    assert feld["load_from_db"] is True
    assert feld["required"] is False


@pytest.mark.parametrize("datei", MIT_KONTAKT)
def test_only_the_helper_reads_the_environment(datei):
    """Reading KONTAKT_EMAIL straight from the environment elsewhere would ignore the group's variable."""
    for funktion in ast.walk(_baum(datei)):
        if not isinstance(funktion, ast.FunctionDef | ast.AsyncFunctionDef) or funktion.name == "_kontakt":
            continue
        for knoten in ast.walk(funktion):
            if isinstance(knoten, ast.Constant) and knoten.value == "KONTAKT_EMAIL":
                pytest.fail(f"{datei}: {funktion.name} liest KONTAKT_EMAIL direkt")
