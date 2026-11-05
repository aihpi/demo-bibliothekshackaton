"""L8 Wiederholen mit Loop: eine DOI-Liste Eintrag für Eintrag bei Crossref nachschlagen und die Ergebnisse sammeln."""

from flows_bauen import WURZEL, Flow

DATEI = "L8_wiederholen_mit_loop"

USER_AGENT = "Bibliothekshackathon/1.0 (https://github.com/aihpi/demo-bibliothekshackaton)"

# Die Suche mit filter=doi antwortet immer mit JSON, auch wenn Crossref die DOI nicht kennt (dann ohne Treffer).
# Die direkte Adresse /works/{doi} antwortet in dem Fall mit Text, an dem Data Operations scheitert.
CROSSREF = (
    "https://api.crossref.org/works?filter=doi:{doi}&rows=1"
    "&select=DOI,title,issued,container-title,is-referenced-by-count,updated-by"
)
JQ_DATENSATZ = (
    '(.source | capture("doi:(?<doi>[^&]+)").doi) as $doi | .result.message.items[0] as $w | '
    'if $w == null then {doi: $doi, jahr: "", titel: "", zeitschrift: "", zitiert: 0, '
    'status: "nicht bei Crossref"} '
    "else {doi: $doi, "
    'jahr: (($w.issued["date-parts"][0][0] // "?") | tostring), '
    'titel: ($w.title[0] // "?"), '
    'zeitschrift: ($w."container-title"[0] // "–"), '
    'zitiert: ($w."is-referenced-by-count" // 0), '
    'status: (if ([$w."updated-by"[]? | select(.type == "retraction")] | length) > 0 '
    'then "ZURÜCKGEZOGEN" else "gefunden" end)} end'
)

TEST = {"eingabe": (WURZEL / "daten/lernpfad/dois.txt").read_text(encoding="utf-8")}


def bauen(lf) -> Flow:
    f = Flow(
        lf,
        DATEI,
        "L8 Wiederholen mit Loop",
        "Lernpfad 8: eine Liste von DOIs Eintrag für Eintrag bei Crossref nachschlagen und die Ergebnisse "
        "als Tabelle sammeln, ohne KI.",
        "Repeat",
    )
    f.notiz(
        "# 🔁 L8 Wiederholen mit Loop\n\n"
        "Eine Liste von DOIs wird **Eintrag für Eintrag** bei **Crossref** nachgeschlagen. Keine KI.\n\n"
        "1. **Split Text** macht aus der eingefügten Liste eine Tabelle: eine Zeile pro DOI.\n"
        "2. **Loop** gibt die Zeilen einzeln an die Schleife (oben):\n"
        "   - **Parser** holt die DOI als Text,\n"
        "   - **Prompt Template** baut daraus die Adresse,\n"
        "   - **API Request** fragt Crossref,\n"
        "   - **Data Operations** liest Titel, Jahr, Zeitschrift, Zitationen und Rückzug aus.\n"
        "   Die gestrichelte Linie führt zurück in die Loop: Dann kommt die nächste DOI dran.\n"
        "3. Wenn alle DOIs durch sind, gibt **Done** alle Ergebnisse auf einmal weiter: an einen **Chat Output** "
        "als Tabelle und über einen zweiten **Parser** als Liste.\n\n"
        "## ▶ So startet ihr\n"
        "1. Kopie anlegen (*Duplicate*).\n"
        "2. **Playground** öffnen und den Inhalt von `daten/lernpfad/dois.txt` einfügen.\n"
        "3. Nach etwa 15 Sekunden erscheinen Tabelle und Liste.\n\n"
        "Anleitung mit Übungen: `anleitungen/lernpfad/L8_wiederholen_mit_loop.md`",
        -160,
        -260,
        breite=480,
    )
    f.notiz(
        "## 🔁 Die Schleife\n"
        "Alles in diesem Bereich läuft **einmal pro DOI**. Die Linie ganz rechts führt zurück an den Ausgang "
        "**Item** der Loop.",
        1640,
        -900,
        breite=1720,
        farbe="amber",
    )
    eingabe = f.baustein("ChatInput", 420, 120, "dois")
    zerlegen = f.baustein(
        "SplitText",
        820,
        60,
        "dois",
        {"separator": "\n", "chunk_size": 1, "chunk_overlap": 0, "clean_output": True},
    )
    schleife = f.baustein("LoopComponent", 1220, 120, "dois")
    doi = f.baustein("ParserComponent", 1660, -560, "doi", {"pattern": "{text}"})
    adresse = f.baustein("Prompt Template", 2080, -600, "adresse", {"template": CROSSREF})
    crossref = f.baustein(
        "APIRequest",
        2500,
        -620,
        "crossref",
        {"headers": [{"key": "User-Agent", "value": USER_AGENT}]},
    )
    datensatz = f.baustein(
        "Operations",
        2920,
        -560,
        "datensatz",
        {"query": JQ_DATENSATZ},
        auswahl={"input_type": "JSON", "operation": [{"name": "JQ Expression", "icon": "terminal"}]},
    )
    tabelle = f.baustein("ChatOutput", 1660, 420, "tabelle")
    f.notiz("**Nach der Schleife**: oben die Tabelle, darunter die Liste", 1220, 600, breite=380, farbe="amber")
    liste = f.baustein(
        "ParserComponent",
        1660,
        780,
        "liste",
        {"pattern": "- {doi}: {titel} ({jahr}), {zeitschrift}. {status}"},
    )
    ausgabe = f.baustein("ChatOutput", 2080, 820, "liste")
    f.verbinden(eingabe, "message", zerlegen, "data_inputs")
    f.verbinden(zerlegen, "dataframe", schleife, "data")
    f.verbinden(schleife, "item", doi, "input_data")
    f.verbinden(doi, "parsed_text", adresse, "doi")
    f.verbinden(adresse, "prompt", crossref, "url_input")
    f.verbinden(crossref, "data", datensatz, "data")
    f.schleife_schliessen(datensatz, "data_output", schleife)
    f.verbinden(schleife, "done", tabelle, "input_value")
    f.verbinden(schleife, "done", liste, "input_data")
    f.verbinden(liste, "parsed_text", ausgabe, "input_value")
    return f
