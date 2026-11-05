"""Checks the exported flows in flows/ without a running Langflow."""

import json
import re
from pathlib import Path

import pytest
from test_lernpfad import BAUSTEIN

WURZEL = Path(__file__).resolve().parent.parent
FLOWS = sorted((WURZEL / "flows").glob("*.json"))


def _bibliothek() -> dict[str, str]:
    """Node type of each library block -> the display name its class declares."""
    namen = {}
    for datei in (WURZEL / "komponenten" / "bibliothek").glob("*.py"):
        text = datei.read_text(encoding="utf-8")
        for klasse, name in re.findall(
            r'^class (\w+)\(.*?^    display_name = "([^"]+)"', text, re.MULTILINE | re.DOTALL
        ):
            namen[f"ext:bibliothek:{klasse}@extra"] = name
    return namen


STANDARD = BAUSTEIN | _bibliothek()


@pytest.mark.parametrize("flow", FLOWS, ids=lambda p: p.stem)
def test_blocks_keep_their_standard_names(flow):
    # Participants later build on their own and need to recognise blocks by the names the sidebar shows.
    for knoten in json.loads(flow.read_text(encoding="utf-8"))["data"]["nodes"]:
        if knoten["type"] != "genericNode":
            continue
        typ, name = knoten["data"]["type"], knoten["data"]["node"]["display_name"]
        assert typ in STANDARD, f"neuer Bausteintyp {typ}: in BAUSTEIN (test_lernpfad.py) eintragen"
        assert name == STANDARD[typ], f"{flow.stem}: {typ} heißt {name!r} statt {STANDARD[typ]!r}"
