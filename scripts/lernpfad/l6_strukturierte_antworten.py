"""L6 Strukturierte Antworten: aus freiem Text und Tabellen mit KI Daten machen, auf vier Wegen nebeneinander."""

from flows_bauen import KI_MODELL, Flow

DATEI = "L6_strukturierte_antworten"

SCHEMA = [
    {
        "name": "autor",
        "description": "Autor:in oder Herausgeber:in, Nachname, Vorname",
        "type": "str",
        "multiple": "False",
    },
    {"name": "titel", "description": "Titel des Buchs ohne Anführungszeichen", "type": "str", "multiple": "False"},
    {"name": "jahr", "description": "Erscheinungsjahr als Zahl; 0, wenn es fehlt", "type": "int", "multiple": "False"},
    {"name": "verlag", "description": "Verlag; leer, wenn er fehlt", "type": "str", "multiple": "False"},
    {"name": "isbn", "description": "ISBN; leer, wenn sie fehlt", "type": "str", "multiple": "False"},
    {"name": "wer", "description": "Name der Person, die das Buch vorschlägt", "type": "str", "multiple": "False"},
]

PROMPT_CSV = (
    "ANSCHAFFUNGSVORSCHLÄGE:\n{mails}\n\n---\n"
    "Oben stehen E-Mails mit Anschaffungsvorschlägen an eine Bibliothek. Ziehe jedes vorgeschlagene Buch heraus.\n"
    "Antworte nur mit einer CSV-Tabelle, ohne Erklärung und ohne ```. Trennzeichen ist das Komma; Werte mit Komma "
    "stehen in Anführungszeichen.\n"
    "Die erste Zeile ist genau diese Kopfzeile:\n"
    "autor,titel,jahr,verlag,isbn,wer\n"
    "Eine Zeile pro Buch. Fehlt eine Angabe, bleibt das Feld leer. Erfinde nichts."
)

TEST = {
    "dateien": {
        "File-mails": ["daten/lernpfad/anschaffungsvorschlaege.txt"],
        "File-liste": ["daten/lernpfad/neuerwerbungen.csv"],
    },
    "werte": {"KIModell-text": {"quelle": "Cluster (LiteLLM)"}, "KIModell-bausteine": {"quelle": "Cluster (LiteLLM)"}},
}


def bauen(lf) -> Flow:
    f = Flow(
        lf,
        DATEI,
        "L6 Strukturierte Antworten",
        "Lernpfad 6: Aus freiem Text und Tabellen mit KI Daten machen. Prompt mit CSV, Structured Output, "
        "Batch Run und Smart Transform im Vergleich.",
        "Braces",
    )
    f.notiz(
        "# 🧱 L6 Strukturierte Antworten\n\n"
        "Ein Sprachmodell antwortet mit Text. Für Tabellen, Filter und Dateien braucht ihr aber **Daten**. "
        "Hier entstehen sie auf vier Wegen:\n\n"
        "**A** Prompt verlangt CSV → **KI-Modell** → **Type Convert** macht eine Tabelle daraus\n"
        "**B** **Structured Output** füllt feste Felder (Output Schema)\n"
        "**C** **Batch Run** fragt das Modell einmal pro Tabellenzeile\n"
        "**D** **Smart Transform** formt eine Tabelle nach einer Anweisung in eigenen Worten um\n\n"
        "A und B lesen dieselben E-Mails, C und D dieselbe Liste: Vergleicht die Ergebnisse!\n\n"
        "## ▶ So startet ihr\n"
        "1. Kopie anlegen (*Duplicate*).\n"
        "2. In **E-Mails (Read File)** `daten/lernpfad/anschaffungsvorschlaege.txt` hochladen, "
        "in **Liste (Read File)** `daten/lernpfad/neuerwerbungen.csv`.\n"
        "3. **Playground** öffnen und irgendetwas abschicken.\n\n"
        "⚠️ B, C und D brauchen ein großes Modell: Stellt die **Quelle** in beiden KI-Modellen auf *Cluster*.\n\n"
        "Anleitung mit Übungen: `anleitungen/lernpfad/L6_strukturierte_antworten.md`",
        -200,
        -260,
        breite=520,
    )

    mails = f.baustein("File", 420, 0, "mails", titel="E-Mails (Read File)")
    # Weg A: das Modell schreibt CSV-Text, Type Convert macht daraus eine Tabelle
    prompt = f.baustein("Prompt Template", 860, -420, "csv", {"template": PROMPT_CSV}, titel="A: Prompt verlangt CSV")
    text_modell = f.baustein(KI_MODELL, 1300, -480, "text", {"temperature": 0.0}, titel="A: KI-Modell")
    roh = f.baustein(
        "ChatOutput", 1740, -700, "roh", {"sender_name": "A: Antwort des Modells"}, titel="A: Antwort des Modells"
    )
    umwandeln = f.baustein(
        "TypeConverterComponent",
        1740,
        -360,
        "csv",
        {"output_type": "Table", "auto_parse": True},
        titel="A: Text → Tabelle (Type Convert)",
    )
    aus_a = f.baustein("ChatOutput", 2180, -360, "a", {"sender_name": "A: Prompt + Type Convert"}, titel="A: Tabelle")
    f.verbinden(mails, "message", prompt, "mails")
    f.verbinden(prompt, "prompt", text_modell, "input_value")
    f.verbinden(text_modell, "text_output", roh, "input_value")
    f.verbinden(text_modell, "text_output", umwandeln, "input_data")
    f.verbinden(umwandeln, "dataframe_output", aus_a, "input_value")

    # Ein KI-Modell liefert das Modell für B, C und D
    modell = f.baustein(KI_MODELL, 860, 480, "bausteine", {"temperature": 0.0}, titel="KI-Modell (für B, C, D)")

    # Weg B: Structured Output mit festem Schema
    struktur = f.baustein(
        "StructuredOutput",
        1300,
        80,
        "vorschlaege",
        {"output_schema": SCHEMA, "schema_name": "Anschaffungsvorschlag"},
        titel="B: Structured Output",
    )
    aus_b = f.baustein("ChatOutput", 1740, 120, "b", {"sender_name": "B: Structured Output"}, titel="B: Tabelle")
    f.verbinden(mails, "message", struktur, "input_value")
    f.verbinden(modell, "model_output", struktur, "model")
    f.verbinden(struktur, "dataframe_output", aus_b, "input_value")

    # Weg C und D arbeiten auf einer Tabelle
    liste = f.baustein("File", 420, 1000, "liste", titel="Liste (Read File)")
    tabelle = f.baustein(
        "TypeConverterComponent",
        860,
        1000,
        "liste",
        {"output_type": "Table", "auto_parse": True},
        titel="Liste als Tabelle (Type Convert)",
    )
    f.verbinden(liste, "message", tabelle, "input_data")

    stapel = f.baustein(
        "BatchRunComponent",
        1300,
        700,
        "fachgruppe",
        {
            "system_message": (
                "Ordne das Buch genau einer dieser Fachgruppen zu: Geisteswissenschaften, "
                "Sozialwissenschaften, Recht, Informatik, Bibliothek und Information. "
                "Antworte nur mit dem Namen der Fachgruppe."
            ),
            "column_name": "titel",
            "output_column_name": "fachgruppe",
        },
        titel="C: Batch Run",
    )
    aus_c = f.baustein("ChatOutput", 1740, 760, "c", {"sender_name": "C: Batch Run"}, titel="C: Tabelle")
    f.verbinden(tabelle, "dataframe_output", stapel, "df")
    f.verbinden(modell, "model_output", stapel, "model")
    f.verbinden(stapel, "batch_results", aus_c, "input_value")

    umformen = f.baustein(
        "Smart Transform",
        1300,
        1240,
        "auswahl",
        {
            "filter_instruction": (
                "Behalte nur Bücher mit dem Status 'verfügbar' ab dem Jahr 2022 und nur die Spalten "
                "titel, jahr und preis_eur. Sortiere nach preis_eur, das teuerste zuerst."
            )
        },
        titel="D: Smart Transform",
    )
    aus_d = f.baustein("ChatOutput", 1740, 1300, "d", {"sender_name": "D: Smart Transform"}, titel="D: Tabelle")
    f.verbinden(tabelle, "dataframe_output", umformen, "data")
    f.verbinden(modell, "model_output", umformen, "model")
    f.verbinden(umformen, "dataframe_output", aus_d, "input_value")
    return f
