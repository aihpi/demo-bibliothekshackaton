"""L4 Ergebnisse ausgeben: eine Tabelle als Zitierliste, Markdown, HTML, Text und Excel-Datei ausgeben, ohne KI."""

from flows_bauen import Flow

DATEI = "L4_ergebnisse_ausgeben"

TEST = {
    "dateien": {"File-datei": ["daten/lernpfad/neuerwerbungen.csv"]},
}

# Ohne Platzhalter in Stilangaben: Das Prompt Template hielte geschweifte Klammern für Platzhalter.
HTML_SEITE = (
    "<h2>Neuerwerbungen</h2>\n"
    "<p>Diese Titel hat die Bibliothek neu bestellt oder eingestellt.</p>\n"
    "<table>\n"
    "  <thead>\n"
    "    <tr><th>Titel</th><th>Autor:in</th><th>Jahr</th><th>Status</th></tr>\n"
    "  </thead>\n"
    "  <tbody>\n{zeilen}\n  </tbody>\n"
    "</table>"
)


def bauen(lf) -> Flow:
    f = Flow(
        lf,
        DATEI,
        "L4 Ergebnisse ausgeben",
        "Lernpfad 4: eine Tabelle als Zitierliste, Markdown-Liste, HTML-Seite, Text und Excel-Datei ausgeben, ohne KI.",
        "FileOutput",
    )
    f.notiz(
        "# 📤 L4 Ergebnisse ausgeben\n\n"
        "Am Ende eines Flows steht ein Ergebnis, das Menschen weiterverwenden: eine Literaturliste, ein "
        "Stück HTML für die Webseite, eine Excel-Datei. Hier wird **eine Tabelle** auf sechs Wegen "
        "ausgegeben. Keine KI.\n\n"
        "**Links:** die Neuerwerbungen lesen, die Lücke im Jahr füllen, eine Tabelle daraus machen.\n\n"
        "**Rechts, von oben nach unten:**\n"
        "1. **Chat Output** – die Tabelle, wie sie ist\n"
        "2. **Parser** – eine Zitierliste\n"
        "3. **Parser** – eine Markdown-Liste\n"
        "4. **Parser** + **Prompt Template** – eine HTML-Seite\n"
        "5. **Parser** (Stringify) – alles als Text\n"
        "6. **Write File** – eine Excel-Datei\n\n"
        "## ▶ So startet ihr\n"
        "1. Kopie anlegen (*Duplicate*).\n"
        "2. In **Read File** die Datei `daten/lernpfad/neuerwerbungen.csv` hochladen.\n"
        "3. **Playground** öffnen und irgendetwas abschicken.\n\n"
        "Die Excel-Datei findet ihr danach in der Übersicht von Langflow unter **My Files**.\n\n"
        "Anleitung mit Übungen: `anleitungen/lernpfad/L4_ergebnisse_ausgeben.md`",
        -620,
        -200,
        breite=480,
    )

    datei = f.baustein("File", 0, 0, "datei", titel="Neuerwerbungen lesen (Read File)")
    luecken = f.baustein(
        "Operations",
        420,
        0,
        "luecken",
        {"search_pattern": ",,", "replacement_text": ",o. J.,"},
        titel="Leere Felder füllen",
        auswahl={"input_type": "Text", "operation": [{"name": "Text Replace"}]},
    )
    tabelle = f.baustein(
        "TypeConverterComponent",
        840,
        0,
        "tabelle",
        {"auto_parse": True},
        titel="Als Tabelle",
        auswahl={"output_type": "Table"},
    )
    f.verbinden(datei, "message", luecken, "text_input")
    f.verbinden(luecken, "message_output", tabelle, "input_data")

    x_parser, x_ausgabe = 1300, 2180
    y = -420
    aus_tabelle = f.baustein("ChatOutput", x_ausgabe, y, "tabelle", {"sender_name": "Tabelle"}, titel="Die Tabelle")
    f.verbinden(tabelle, "dataframe_output", aus_tabelle, "input_value")

    y += 400
    zitate = f.baustein(
        "ParserComponent",
        x_parser,
        y,
        "zitate",
        {"pattern": "{autor} ({jahr}). {titel}. {verlag}."},
        titel="Zitierliste",
    )
    aus_zitate = f.baustein("ChatOutput", x_ausgabe, y, "zitate", {"sender_name": "Zitierliste"}, titel="Zitierliste")
    f.verbinden(tabelle, "dataframe_output", zitate, "input_data")
    f.verbinden(zitate, "parsed_text", aus_zitate, "input_value")

    y += 400
    liste = f.baustein(
        "ParserComponent",
        x_parser,
        y,
        "liste",
        {"pattern": "- **{titel}** von {autor} ({fach}, {status})"},
        titel="Markdown-Liste",
    )
    aus_liste = f.baustein(
        "ChatOutput", x_ausgabe, y, "liste", {"sender_name": "Markdown-Liste"}, titel="Markdown-Liste"
    )
    f.verbinden(tabelle, "dataframe_output", liste, "input_data")
    f.verbinden(liste, "parsed_text", aus_liste, "input_value")

    y += 400
    zeilen = f.baustein(
        "ParserComponent",
        x_parser,
        y,
        "html",
        {"pattern": "    <tr><td>{titel}</td><td>{autor}</td><td>{jahr}</td><td>{status}</td></tr>"},
        titel="HTML-Tabellenzeilen",
    )
    seite = f.baustein("Prompt Template", 1740, y, "seite", {"template": HTML_SEITE}, titel="HTML-Seite (ohne KI)")
    aus_seite = f.baustein("ChatOutput", x_ausgabe, y, "html", {"sender_name": "HTML"}, titel="HTML für die Webseite")
    f.verbinden(tabelle, "dataframe_output", zeilen, "input_data")
    f.verbinden(zeilen, "parsed_text", seite, "zeilen")
    f.verbinden(seite, "prompt", aus_seite, "input_value")

    y += 460
    text = f.baustein(
        "ParserComponent",
        x_parser,
        y,
        "text",
        {"mode": "Stringify"},
        titel="Alles als Text (Stringify)",
        auswahl={"mode": "Stringify"},
    )
    aus_text = f.baustein("ChatOutput", x_ausgabe, y, "text", {"sender_name": "Text"}, titel="Alles als Text")
    f.verbinden(tabelle, "dataframe_output", text, "input_data")
    f.verbinden(text, "parsed_text", aus_text, "input_value")

    y += 400
    speichern = f.baustein(
        "SaveToFile",
        x_parser,
        y,
        "excel",
        {"file_name": "neuerwerbungen_aufbereitet", "local_format": "excel"},
        titel="Als Excel speichern (Write File)",
    )
    aus_datei = f.baustein("ChatOutput", x_ausgabe, y, "datei", {"sender_name": "Write File"}, titel="Gespeichert")
    f.verbinden(tabelle, "dataframe_output", speichern, "input")
    f.verbinden(speichern, "message", aus_datei, "input_value")
    return f
