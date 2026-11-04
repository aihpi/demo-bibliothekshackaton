"""L3 Tabellen und JSON: eine Antwort von OpenAlex und eine CSV-Liste werden zu sauberen Tabellen, ohne KI."""

from flows_bauen import Flow

DATEI = "L3_tabellen_und_json"

JQ_TREFFER = (".result.results | map({titel: .display_name, jahr: .publication_year, "
              'doi: (.doi // "keine DOI"), zitiert: .cited_by_count, frei_zugaenglich: .open_access.is_oa})')

TEST = {
    "dateien": {
        "File-neuerwerbungen": ["daten/lernpfad/neuerwerbungen.csv"],
        "File-fachreferate": ["daten/lernpfad/fachreferate.csv"],
    },
}


def _operation(eingabe: str, operation: str) -> dict:
    return {"input_type": eingabe, "operation": [{"name": operation}]}


def bauen(lf) -> Flow:
    f = Flow(lf, DATEI, "L3 Tabellen und JSON",
             "Lernpfad 3: Die Antwort eines Webdienstes (JSON) und eine CSV-Liste in saubere Tabellen verwandeln: "
             "Felder auswählen, filtern, sortieren, Doppelte entfernen, zwei Tabellen verbinden. Ohne KI.", "Table")
    f.notiz(
        "# 🧮 L3 Tabellen und JSON\n\n"
        "Daten kommen selten so an, wie ihr sie braucht. Hier werden sie in Form gebracht, ohne KI.\n\n"
        "**Oben: ein Webdienst.** *Dynamic Create Data* baut die Suchparameter, *API Request* fragt OpenAlex, "
        "*Data Operations* greift die Treffer heraus (Path Selection) oder baut sie um (JQ), *Type Convert* "
        "macht eine Tabelle daraus.\n\n"
        "**Unten: eine Liste.** Die Neuerwerbungen (CSV) werden zur Tabelle, dann aufgeräumt: Fach "
        "vereinheitlichen, Doppelte entfernen, Fachreferat ergänzen (Merge), sortieren, Spalten auswählen, "
        "filtern. *Parser* macht aus der Tabelle eine Liste.\n\n"
        "## ▶ So startet ihr\n"
        "1. Kopie anlegen (*Duplicate*).\n"
        "2. In **Neuerwerbungen** `daten/lernpfad/neuerwerbungen.csv` hochladen, in **Fachreferate** "
        "`daten/lernpfad/fachreferate.csv`.\n"
        "3. **Playground** öffnen und irgendetwas abschicken.\n"
        "4. Oder jeden Baustein mit **▶** einzeln ausführen und rechts am Ausgang nachsehen.\n\n"
        "Anleitung mit Übungen: `anleitungen/lernpfad/L3_tabellen_und_json.md`",
        -200, -200, breite=520)

    # Oben: Webdienst -> JSON -> Tabelle
    parameter = f.baustein("DynamicCreateData", 420, 0, "suchparameter", {
        "dynamic_search": "academic libraries open access",
        "dynamic_per-page": "5",
        "dynamic_select": "display_name,publication_year,doi,cited_by_count,open_access",
    }, titel="Suchparameter (Dynamic Create Data)",
        auswahl={"form_fields": [{"field_name": n, "field_type": "Text"} for n in ("search", "per-page", "select")]})
    api = f.baustein("APIRequest", 860, 0, "openalex", {"url_input": "https://api.openalex.org/works"},
                     titel="OpenAlex fragen (API Request)")
    pfad = f.baustein("Operations", 1300, -160, "pfad", {"selected_key": ".result.results"},
                      titel="Treffer herausgreifen (Path Selection)", auswahl=_operation("JSON", "Path Selection"))
    roh = f.baustein("TypeConverterComponent", 1740, -160, "roh", {"output_type": "Table"},
                     titel="Als Tabelle (Type Convert)", auswahl={"output_type": "Table"})
    aus_roh = f.baustein("ChatOutput", 2180, -120, "roh", {"sender_name": "OpenAlex"},
                         titel="Treffer, wie OpenAlex sie liefert")
    jq = f.baustein("Operations", 1300, 320, "jq", {"query": JQ_TREFFER},
                    titel="Felder auswählen und umbenennen (JQ)", auswahl=_operation("JSON", "JQ Expression"))
    sauber = f.baustein("TypeConverterComponent", 1740, 320, "sauber", {"output_type": "Table"},
                        titel="Als Tabelle (Type Convert)", auswahl={"output_type": "Table"})
    aus_sauber = f.baustein("ChatOutput", 2180, 360, "sauber", {"sender_name": "OpenAlex"},
                            titel="Treffer, aufgeräumt")
    f.verbinden(parameter, "form_data", api, "query_params")
    f.verbinden(api, "data", pfad, "data")
    f.verbinden(pfad, "data_output", roh, "input_data")
    f.verbinden(roh, "dataframe_output", aus_roh, "input_value")
    f.verbinden(api, "data", jq, "data")
    f.verbinden(jq, "data_output", sauber, "input_data")
    f.verbinden(sauber, "dataframe_output", aus_sauber, "input_value")

    # Unten: CSV-Liste aufräumen und mit einer zweiten Tabelle verbinden
    y = 1000
    neu = f.baustein("File", 420, y, "neuerwerbungen", titel="Neuerwerbungen (Read File)")
    neu_tabelle = f.baustein("TypeConverterComponent", 860, y, "neuerwerbungen",
                             {"output_type": "Table", "auto_parse": True},
                             titel="CSV als Tabelle (Type Convert)", auswahl={"output_type": "Table"})
    fach = f.baustein("Operations", 1300, y, "fach",
                      {"column_name": "fach", "replace_value": "informatik", "replacement_value": "Informatik"},
                      titel="Fach vereinheitlichen (Replace Value)", auswahl=_operation("Table", "Replace Value"))
    doppelt = f.baustein("Operations", 1740, y, "doppelt", {"column_name": "isbn"},
                         titel="Doppelte entfernen (Drop Duplicates)", auswahl=_operation("Table", "Drop Duplicates"))
    referate = f.baustein("File", 1300, y + 560, "fachreferate", titel="Fachreferate (Read File)")
    referate_tabelle = f.baustein("TypeConverterComponent", 1740, y + 560, "fachreferate",
                                  {"output_type": "Table", "auto_parse": True},
                                  titel="CSV als Tabelle (Type Convert)", auswahl={"output_type": "Table"})
    verbinden = f.baustein("Operations", 2180, y, "merge", {"merge_on_column": "fach", "merge_how": "left"},
                           titel="Fachreferat ergänzen (Merge)", auswahl=_operation("Table", "Merge"))
    sortiert = f.baustein("Operations", 2620, y, "sortieren", {"column_name": "fach", "ascending": True},
                          titel="Nach Fach sortieren (Sort)", auswahl=_operation("Table", "Sort"))
    spalten = f.baustein("Operations", 3060, y - 200, "spalten", {
        "columns_to_select": ["titel", "autor", "jahr", "fach", "fachreferat", "standort", "status"]},
        titel="Spalten auswählen (Select Columns)", auswahl=_operation("Table", "Select Columns"))
    aus_liste = f.baustein("ChatOutput", 3500, y - 160, "liste", {"sender_name": "Erwerbung"},
                           titel="Neuerwerbungen, aufgeräumt")
    bestellt = f.baustein("Operations", 3060, y + 360, "bestellt",
                          {"column_name": "status", "filter_operator": "equals", "filter_value": "bestellt"},
                          titel="Nur bestellte (Filter)", auswahl=_operation("Table", "Filter"))
    liste = f.baustein("ParserComponent", 3500, y + 360, "bestellt",
                       {"pattern": "- {titel} ({autor}), Fachreferat: {fachreferat}"}, titel="Als Liste (Parser)")
    aus_bestellt = f.baustein("ChatOutput", 3940, y + 400, "bestellt", {"sender_name": "Erwerbung"},
                              titel="Bestellt: Liste für die Fachreferate")
    f.verbinden(neu, "message", neu_tabelle, "input_data")
    f.verbinden(neu_tabelle, "dataframe_output", fach, "df")
    f.verbinden(fach, "dataframe_output", doppelt, "df")
    f.verbinden(referate, "message", referate_tabelle, "input_data")
    f.verbinden(doppelt, "dataframe_output", verbinden, "left_dataframe")
    f.verbinden(referate_tabelle, "dataframe_output", verbinden, "right_dataframe")
    f.verbinden(verbinden, "dataframe_output", sortiert, "df")
    f.verbinden(sortiert, "dataframe_output", spalten, "df")
    f.verbinden(spalten, "dataframe_output", aus_liste, "input_value")
    f.verbinden(sortiert, "dataframe_output", bestellt, "df")
    f.verbinden(bestellt, "dataframe_output", liste, "input_data")
    f.verbinden(liste, "parsed_text", aus_bestellt, "input_value")
    return f
