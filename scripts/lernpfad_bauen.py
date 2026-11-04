"""Baut die Lernpfad-Flows (L1, L2, …) über die Langflow-API und speichert sie in flows/.

Für Betreuende und Entwickler:innen. Langflow muss laufen (docker compose up -d). Dann:

    uv run --with httpx scripts/lernpfad_bauen.py            # alle Lernpfad-Flows bauen und exportieren
    uv run --with httpx scripts/lernpfad_bauen.py --testen   # zusätzlich jeden Flow einmal ausführen
    uv run --with httpx scripts/lernpfad_bauen.py --nur L3   # nur einen Flow

Jeder Flow steht in einem eigenen Modul unter scripts/lernpfad/ mit
    DATEI: str          Dateiname ohne Endung, z. B. "L1_daten_importieren"
    bauen(lf) -> Flow   baut den Flow (mit Flow(lf, DATEI, …))
    TEST: dict          was der Testlauf eingibt, siehe testen()
Der Flow landet in flows/<DATEI>.json, die Anleitung dazu liegt in anleitungen/lernpfad/<DATEI>.md.
"""

import argparse
import copy
import importlib
import json
import time
import uuid
from pathlib import Path

from flows_bauen import LANGFLOW, WURZEL, ZIEL, Flow, Langflow, speichern

MODULE = Path(__file__).resolve().parent / "lernpfad"


def module() -> list:
    return [importlib.import_module(f"lernpfad.{datei.stem}") for datei in sorted(MODULE.glob("l[0-9]*.py"))]


def hochladen(lf: Langflow, pfad: Path) -> str:
    antwort = lf.http.post("/api/v2/files", files={"file": (pfad.name, pfad.read_bytes())})
    antwort.raise_for_status()
    return antwort.json()["path"]


def bauen_wie_im_editor(lf: Langflow, flow: Flow, daten: dict, eingabe: str | None, ziel: str | None) -> dict:
    """Baut den Flow über denselben Weg wie der Editor und gibt {Knoten-ID: Ausgaben} zurück.

    Mit Eingabe wie der Playground: Hat der Flow einen Chat Input, laufen nur die Bausteine, die von ihm abhängen,
    und das, was sie brauchen. Mit Ziel wie der ▶-Knopf an einem Baustein: dieser Baustein und alles davor.
    """
    body = {"data": daten, "inputs": {"input_value": eingabe, "session": f"test-{uuid.uuid4()}"}}
    if eingabe is None:
        del body["inputs"]
    antwort = lf.http.post(
        f"/api/v1/build/{flow.id}/flow", json=body, params={"stop_component_id": ziel} if ziel else {}
    )
    antwort.raise_for_status()
    gebaut = {}
    with lf.http.stream("GET", f"/api/v1/build/{antwort.json()['job_id']}/events") as ereignisse:
        for zeile in ereignisse.iter_lines():
            if not zeile.strip():
                continue
            ereignis = json.loads(zeile)
            if ereignis["event"] == "end_vertex":
                b = ereignis["data"]["build_data"]
                if not b["valid"]:
                    raise RuntimeError(f"{b['id']}: {json.dumps(b.get('data'), ensure_ascii=False)[:1500]}")
                gebaut[b["id"]] = (b.get("data") or {}).get("outputs") or {}
            elif ereignis["event"] == "error":
                raise RuntimeError(json.dumps(ereignis["data"], ensure_ascii=False)[:1500])
            elif ereignis["event"] == "end":
                break
    return gebaut


def testen(lf: Langflow, flow: Flow, test: dict) -> bool:
    """Führt den Flow aus, wie Teilnehmende es tun, und zeigt jeden Chat Output.

    test["eingabe"]   Text für den Playground. Fehlt sie, läuft der Flow ohne Chat-Eingabe.
    test["ziele"]     Knoten-IDs, die zusätzlich einzeln mit ▶ gebaut werden, z. B. Zweige ohne Chat Input
    test["dateien"]   {Knoten-ID: [Pfade unter daten/]}: wird hochgeladen und in Read File eingesetzt
    test["werte"]     {Knoten-ID: {Feld: Wert}}: wird vor dem Lauf eingesetzt
    test["leer_ok"]   Knoten-IDs von Chat Outputs, die leer bleiben dürfen (z. B. der nicht gewählte Weg einer Weiche)
    test["ohne"]      Begründung, warum der Flow nicht automatisch getestet wird
    """
    if "ohne" in test:
        print(f"  (nicht ausgeführt: {test['ohne']})")
        return True
    daten = copy.deepcopy(flow.als_json()["data"])
    knoten = {k["id"]: k["data"]["node"]["template"] for k in daten["nodes"] if k["type"] == "genericNode"}
    for knoten_id, pfade in test.get("dateien", {}).items():
        hochgeladen = [hochladen(lf, WURZEL / p) for p in pfade]
        knoten[knoten_id]["path"]["value"] = hochgeladen
        knoten[knoten_id]["path"]["file_path"] = hochgeladen
    for knoten_id, werte in test.get("werte", {}).items():
        for feld, wert in werte.items():
            knoten[knoten_id][feld]["value"] = wert
    ausgaben = [k["id"] for k in daten["nodes"] if k["data"].get("type") == "ChatOutput"]
    gebaut = {}
    start = time.time()
    try:
        for ziel in [None, *test.get("ziele", [])]:
            gebaut |= bauen_wie_im_editor(lf, flow, daten, test.get("eingabe"), ziel)
    except RuntimeError as fehler:
        print(f"  ✘ Test fehlgeschlagen nach {time.time() - start:.0f} s: {fehler}")
        return False
    ok = True
    for knoten_id in ausgaben:
        text = str(((gebaut.get(knoten_id) or {}).get("message") or {}).get("message") or "").strip()
        darf_leer = knoten_id in test.get("leer_ok", ())
        fehlt = not text and not darf_leer
        ok &= not fehlt
        print(f"  {'✘' if fehlt else '──'} {knoten_id}:" + "".join(f"\n  │ {z}" for z in text.splitlines()[:12]))
    print(f"  ({time.time() - start:.0f} s, {len(gebaut)} Bausteine gelaufen)")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--testen", action="store_true", help="jeden Flow nach dem Bauen einmal ausführen")
    parser.add_argument("--nur", help="nur Flows, deren Name diesen Text enthält, z. B. 'L3'")
    parser.add_argument("--url", default=LANGFLOW)
    args = parser.parse_args()

    lf = Langflow(args.url)
    ZIEL.mkdir(exist_ok=True)
    fehler = []
    for modul in module():
        flow = modul.bauen(lf)
        if args.nur and args.nur not in flow.name:
            continue
        speichern(lf, flow)
        if args.testen and not testen(lf, flow, modul.TEST):
            fehler.append(flow.name)
    if fehler:
        raise SystemExit("Fehlgeschlagen: " + ", ".join(fehler))


if __name__ == "__main__":
    main()
