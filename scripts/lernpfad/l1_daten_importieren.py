"""L1 Daten importieren: dieselbe Art von Bibliotheksdaten auf fünf Wegen holen, jeder mit eigenem Chat Output."""

from flows_bauen import Flow

DATEI = "L1_daten_importieren"

# Wikimedia lehnt Anfragen ohne erkennbaren Absender ab; ein Name mit Webadresse reicht.
USER_AGENT = "Bibliothekshackathon/1.0 (https://github.com/aihpi/demo-bibliothekshackaton)"
OPENALEX_URL = ("https://api.openalex.org/works?search=academic%20libraries%20open%20access"
                "&per-page=3&select=display_name,publication_year,doi")

TEST = {
    "dateien": {"File-datei": ["daten/lernpfad/neuerwerbungen.csv"]},
}


def bauen(lf) -> Flow:
    f = Flow(lf, DATEI, "L1 Daten importieren",
             "Lernpfad 1: Daten aus einer Datei, einer Webseite, einem Webdienst, der Websuche und aus "
             "Beispieldaten holen, ohne KI.", "Import")
    f.notiz(
        "# 📥 L1 Daten importieren\n\n"
        "Bevor ein Flow etwas tun kann, braucht er **Daten**. Hier holt jede Zeile sie auf einem anderen Weg "
        "und zeigt sie in einem eigenen **Chat Output**. Keine KI.\n\n"
        "1. **Read File** – eine Datei, die ihr hochladet\n"
        "2. **URL** – den Text einer Webseite\n"
        "3. **API Request** – Daten von einem Webdienst (hier OpenAlex)\n"
        "4. **Web Search** – Treffer aus Websuche, News oder RSS\n"
        "5. **Mock Data** – ausgedachte Testdaten\n\n"
        "## ▶ So startet ihr\n"
        "1. Kopie anlegen (*Duplicate*).\n"
        "2. In **Read File** die Datei `daten/lernpfad/neuerwerbungen.csv` hochladen.\n"
        "3. **Playground** öffnen und irgendetwas abschicken: Alle fünf Ergebnisse erscheinen.\n"
        "4. Oder einen Baustein mit **▶** einzeln ausführen und rechts am Ausgang nachsehen.\n\n"
        "Anleitung mit Übungen: `anleitungen/lernpfad/L1_daten_importieren.md`",
        -160, -160, breite=480)

    y = 0
    datei = f.baustein("File", 520, y, "datei", titel="Datei lesen (Read File)")
    aus_datei = f.baustein("ChatOutput", 960, y + 40, "datei", {"sender_name": "Datei"}, titel="Aus einer Datei")
    f.verbinden(datei, "message", aus_datei, "input_value")

    y += 460
    seite = f.baustein("URLComponent", 520, y, "seite", {
        "urls": ["https://de.wikipedia.org/wiki/Open_Access"],
        "headers": [{"key": "User-Agent", "value": USER_AGENT}],
    }, titel="Webseite holen (URL)")
    aus_seite = f.baustein("ChatOutput", 960, y + 40, "seite", {"sender_name": "Webseite"}, titel="Von einer Webseite")
    f.verbinden(seite, "raw_results", aus_seite, "input_value")

    y += 520
    api = f.baustein("APIRequest", 520, y, "openalex", {"url_input": OPENALEX_URL}, titel="Webdienst fragen (API Request)")
    aus_api = f.baustein("ChatOutput", 960, y + 40, "api", {"sender_name": "Webdienst"}, titel="Von einem Webdienst")
    f.verbinden(api, "data", aus_api, "input_value")

    y += 460
    suche = f.baustein("UnifiedWebSearch", 520, y, "news", {
        "search_mode": "News", "query": "Bibliothek künstliche Intelligenz",
        "hl": "de", "gl": "DE", "ceid": "DE:de", "max_results": 5,
    }, titel="Im Web suchen (Web Search)")
    aus_suche = f.baustein("ChatOutput", 960, y + 40, "suche", {"sender_name": "Websuche"}, titel="Aus der Websuche")
    f.verbinden(suche, "results", aus_suche, "input_value")

    y += 460
    beispiel = f.baustein("MockDataGenerator", 520, y, "beispiel", titel="Testdaten erzeugen (Mock Data)")
    aus_beispiel = f.baustein("ChatOutput", 960, y + 40, "beispiel", {"sender_name": "Testdaten"},
                              titel="Ausgedachte Testdaten")
    f.verbinden(beispiel, "dataframe_output", aus_beispiel, "input_value")
    return f
