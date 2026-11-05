"""L2 Texte aufbereiten: einen Text aus einem PDF säubern, Text zerlegen und aus Text eine Tabelle machen."""

from flows_bauen import Flow

DATEI = "L2_texte_aufbereiten"

# Eine Liste, wie sie aus einer E-Mail oder einem Wiki kopiert wird: Spalten durch | getrennt
ZEITSCHRIFTEN = (
    "Titel | ISSN | Lizenz | Zugang bis\n"
    "Bibliotheksforum | 1234-5678 | Campus | 2027\n"
    "Open Library Review | 2345-6789 | Open Access | unbegrenzt\n"
    "Zeitschrift für Erschließung | 3456-7890 | Campus | 2026\n"
    "Data & Libraries | 4567-8901 | Nationallizenz | unbegrenzt"
)
KOPFZEILE = r"\s*Bibliotheksforum 12 \(2025\) +Seite \d+\s*"
DOI_MUSTER = r"10\.\d{4,9}/[\w./-]*\w"

TEST = {
    "dateien": {
        "File-pdftext": ["daten/lernpfad/text_aus_pdf.txt"],
        "File-ordnung": ["daten/lernpfad/benutzungsordnung.txt"],
    },
}


def _text(name: str) -> dict:
    return {"input_type": "Text", "operation": [{"name": name}]}


def bauen(lf) -> Flow:
    f = Flow(
        lf,
        DATEI,
        "L2 Texte aufbereiten",
        "Lernpfad 2: Text aus einem PDF säubern, Muster herausziehen, Text in Stücke zerlegen und aus "
        "Text eine Tabelle machen, ohne KI.",
        "Scissors",
    )
    f.notiz(
        "# ✂️ L2 Texte aufbereiten\n\n"
        "Text aus PDFs, Webseiten oder Katalogen ist selten sauber. Hier wird er **gesäubert**, "
        "**durchsucht** und **zerlegt**. Keine KI.\n\n"
        "1. **Oben:** ein Text, wie er aus einem PDF kommt. Vier **Data Operations** (Schritt 1 bis 4) "
        "entfernen nacheinander Silbentrennung, Kopfzeilen, Zeilenumbrüche und doppelte Leerzeichen. "
        "Darunter zwei weitere: DOIs herausziehen (*Text Extract*), Wörter zählen (*Word Count*).\n"
        "2. **Mitte:** **Split Text** zerlegt die Benutzungsordnung in Abschnitte. **Type Convert** macht "
        "aus der Tabelle wieder Text.\n"
        "3. **Unten:** **Data Operations** macht aus einer kopierten Liste eine Tabelle.\n\n"
        "## ▶ So startet ihr\n"
        "1. Kopie anlegen (*Duplicate*).\n"
        "2. Im oberen **Read File** die Datei `daten/lernpfad/text_aus_pdf.txt` hochladen, im "
        "**Read File** in der Mitte die Datei `daten/lernpfad/benutzungsordnung.txt`.\n"
        "3. **Playground** öffnen und irgendetwas abschicken.\n"
        "4. Besser noch: jeden Baustein mit **▶** einzeln ausführen und die Ausgabe ansehen.\n\n"
        "Anleitung mit Übungen: `anleitungen/lernpfad/L2_texte_aufbereiten.md`",
        -200,
        -260,
        breite=520,
    )

    # Zeile 1: Text aus einem PDF säubern
    pdf = f.baustein("File", 420, 0, "pdftext")
    # Die vier Data Operations sehen gleich aus; die Anleitung spricht sie über diese Nummern an
    for x, schritt in (
        (860, "**Schritt 1:** Silbentrennung entfernen"),
        (1300, "**Schritt 2:** Kopfzeilen entfernen"),
        (1740, "**Schritt 3:** Zeilen zusammenführen"),
        (2180, "**Schritt 4:** Leerzeichen säubern"),
    ):
        f.notiz(schritt, x, -180, breite=320, farbe="amber")
    trennung = f.baustein(
        "Operations",
        860,
        0,
        "trennung",
        {"search_pattern": "-\\n", "replacement_text": "", "use_regex": True},
        auswahl=_text("Text Replace"),
    )
    kopf = f.baustein(
        "Operations",
        1300,
        0,
        "kopfzeilen",
        {"search_pattern": KOPFZEILE, "replacement_text": "\\n\\n", "use_regex": True},
        auswahl=_text("Text Replace"),
    )
    zeilen = f.baustein(
        "Operations",
        1740,
        0,
        "zeilen",
        {"search_pattern": r"(?<!\n)\n(?!\n)", "replacement_text": " ", "use_regex": True},
        auswahl=_text("Text Replace"),
    )
    sauber = f.baustein(
        "Operations",
        2180,
        0,
        "sauber",
        {"remove_extra_spaces": True, "remove_empty_lines": False},
        auswahl=_text("Text Clean"),
    )
    aus_sauber = f.baustein("ChatOutput", 2620, 40, "sauber", {"sender_name": "Gesäubert"})
    f.verbinden(pdf, "message", trennung, "text_input")
    f.verbinden(trennung, "message_output", kopf, "text_input")
    f.verbinden(kopf, "message_output", zeilen, "text_input")
    f.verbinden(zeilen, "message_output", sauber, "text_input")
    f.verbinden(sauber, "message_output", aus_sauber, "input_value")

    dois = f.baustein(
        "Operations",
        860,
        560,
        "dois",
        {"extract_pattern": DOI_MUSTER, "max_matches": 10},
        auswahl=_text("Text Extract"),
    )
    aus_dois = f.baustein("ChatOutput", 1300, 600, "dois", {"sender_name": "DOIs"})
    zaehlen = f.baustein("Operations", 1740, 560, "zaehlen", auswahl=_text("Word Count"))
    aus_zaehlen = f.baustein("ChatOutput", 2180, 600, "zaehlen", {"sender_name": "Zählung"})
    f.verbinden(pdf, "message", dois, "text_input")
    f.verbinden(dois, "message_output", aus_dois, "input_value")
    f.verbinden(pdf, "message", zaehlen, "text_input")
    f.verbinden(zaehlen, "data_output", aus_zaehlen, "input_value")

    # Zeile 2: Text in Stücke zerlegen
    ordnung = f.baustein("File", 420, 1100, "ordnung")
    stuecke = f.baustein(
        "SplitText",
        860,
        1100,
        "abschnitte",
        {"separator": "\\n\\n", "chunk_size": 1, "chunk_overlap": 0, "clean_output": True},
    )
    aus_tabelle = f.baustein("ChatOutput", 1300, 1060, "abschnitte", {"sender_name": "Abschnitte"})
    als_text = f.baustein("TypeConverterComponent", 1300, 1440, "text", {"output_type": "Message"})
    aus_text = f.baustein("ChatOutput", 1740, 1480, "text", {"sender_name": "Als Text"})
    f.verbinden(ordnung, "message", stuecke, "data_inputs")
    f.verbinden(stuecke, "dataframe", aus_tabelle, "input_value")
    f.verbinden(stuecke, "dataframe", als_text, "input_data")
    f.verbinden(als_text, "message_output", aus_text, "input_value")

    # Zeile 3: aus kopiertem Text eine Tabelle machen
    liste = f.baustein(
        "Operations",
        420,
        1980,
        "liste",
        {"text_input": ZEITSCHRIFTEN, "table_separator": "|"},
        auswahl=_text("Text to DataFrame"),
    )
    aus_liste = f.baustein("ChatOutput", 860, 2020, "liste", {"sender_name": "Tabelle"})
    f.verbinden(liste, "dataframe_output", aus_liste, "input_value")
    return f
