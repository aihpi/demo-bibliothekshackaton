"""Checks that the learning-path modules, their exported flows, guides and sample data fit together.

They run without Langflow: building the flows needs a running instance (scripts/lernpfad_bauen.py --testen).
"""

import json
import re
from pathlib import Path

import pytest
from lernpfad_bauen import module

WURZEL = Path(__file__).resolve().parent.parent
ANLEITUNGEN = WURZEL / "anleitungen" / "lernpfad"
MODULE = module()
DATEIEN = [m.DATEI for m in MODULE]


def _flow(datei: str) -> dict:
    return json.loads((WURZEL / "flows" / f"{datei}.json").read_text(encoding="utf-8"))


def _notizen(flow: dict) -> str:
    return "\n".join(k["data"]["node"]["description"] for k in flow["data"]["nodes"] if k["type"] == "noteNode")


def test_every_module_declares_what_the_builder_needs():
    for m in MODULE:
        assert callable(m.bauen), m.__name__
        assert isinstance(m.TEST, dict), m.__name__
        assert re.fullmatch(r"L\d+_[a-z0-9_]+", m.DATEI), m.DATEI
        assert m.__name__.rsplit(".", 1)[1] == m.DATEI.lower(), "Modulname und DATEI passen nicht zusammen"


@pytest.mark.parametrize("datei", DATEIEN)
def test_flow_is_exported_and_has_a_guide(datei):
    assert (WURZEL / "flows" / f"{datei}.json").is_file(), "Flow nicht exportiert: lernpfad_bauen.py ausführen"
    assert (ANLEITUNGEN / f"{datei}.md").is_file()


@pytest.mark.parametrize("datei", DATEIEN)
def test_exported_flow_is_consistent(datei):
    flow = _flow(datei)
    assert flow["name"].startswith(datei.split("_", 1)[0] + " ")
    ids = {k["id"] for k in flow["data"]["nodes"]}
    for kante in flow["data"]["edges"]:
        assert kante["source"] in ids and kante["target"] in ids, kante["id"]
    assert _notizen(flow), "Jeder Lernpfad-Flow erklärt sich mit einer Notiz auf der Arbeitsfläche"


def test_overview_links_every_guide():
    uebersicht = (ANLEITUNGEN / "README.md").read_text(encoding="utf-8")
    for datei in DATEIEN:
        assert f"({datei}.md)" in uebersicht, datei


@pytest.mark.parametrize("anleitung", sorted(ANLEITUNGEN.glob("*.md")), ids=lambda p: p.name)
def test_relative_links_in_guides_resolve(anleitung):
    text = anleitung.read_text(encoding="utf-8")
    for ziel in re.findall(r"\]\((?!https?://|#|mailto:)([^)#\s]+)", text):
        assert (anleitung.parent / ziel).exists(), f"{anleitung.name}: {ziel}"


def _erwaehnte_daten(text: str) -> set[str]:
    return set(re.findall(r"daten/lernpfad/[\w./-]+\.\w+", text))


@pytest.mark.parametrize("datei", DATEIEN)
def test_sample_files_named_in_guide_notes_and_test_exist(datei):
    m = next(m for m in MODULE if m.DATEI == datei)
    erwaehnt = _erwaehnte_daten((ANLEITUNGEN / f"{datei}.md").read_text(encoding="utf-8"))
    erwaehnt |= _erwaehnte_daten(_notizen(_flow(datei)))
    erwaehnt |= {p for pfade in m.TEST.get("dateien", {}).values() for p in pfade}
    for pfad in erwaehnt:
        assert (WURZEL / pfad).is_file(), pfad
