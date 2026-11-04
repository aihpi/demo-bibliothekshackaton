"""L9 Agenten: ein Agent, der nur Standard-Bausteine als Werkzeuge hat, dazu ein ganzer Flow als Werkzeug."""

from flows_bauen import KI_MODELL, Flow

DATEI = "L9_agenten"

# Wikimedia und andere Websites lehnen Anfragen ohne erkennbaren Absender ab.
USER_AGENT = "Bibliothekshackathon/1.0 (https://github.com/aihpi/demo-bibliothekshackaton)"
# Run Flow findet den Ziel-Flow über den Namen. Eine gespeicherte Flow-ID gälte nur auf diesem Rechner:
# Auf der gehosteten Instanz hat jede Gruppe Kopien mit eigenen IDs.
ZIEL_FLOW = "01 Referenz-Checker"

ANWEISUNGEN = (
    "Du bist ein Recherche-Assistent einer wissenschaftlichen Bibliothek.\n\n"
    "Deine Werkzeuge:\n"
    "- Websuche: im Web suchen (Modus Web), in Nachrichten (Modus News) oder einen RSS-Feed lesen "
    "(Modus RSS, dann ist die Suchanfrage die Adresse des Feeds).\n"
    "- Webseite holen: den Text einer Webseite, deren Adresse du kennst.\n"
    "- Taschenrechner: rechnen. Rechne nie im Kopf, sondern immer mit dem Taschenrechner.\n"
    "- Datum: das heutige Datum. Nimm die Zeitzone Europe/Berlin.\n"
    "- Referenz-Checker: prüft Literaturangaben mit der Datenbank Crossref.\n\n"
    "Regeln:\n"
    "- Nutze die Werkzeuge, statt aus dem Gedächtnis zu antworten. Erfinde nichts.\n"
    "- Nenne zu jeder Information die Quelle mit Link.\n"
    "- Antworte auf Deutsch, knapp und übersichtlich."
)

TEST = {
    "eingabe": "Was ist der neueste Beitrag im Bibliotheksportal (RSS-Feed https://bibliotheksportal.de/feed/) "
               "und vor wie vielen Tagen ist er erschienen?",
    # Agenten brauchen ein Modell, das Werkzeuge bedienen kann; der Laptop-Standard ist lokal.
    "werte": {"KIModell-agent": {"quelle": "Cluster (LiteLLM)"}},
}


def bauen(lf) -> Flow:
    f = Flow(lf, DATEI, "L9 Agenten",
             "Lernpfad 9: Ein Agent entscheidet selbst, welche Werkzeuge er nutzt: Websuche, Webseite, "
             "Taschenrechner, Datum und ein ganzer Flow als Werkzeug.", "Bot")
    f.notiz(
        "# 🤖 L9 Agenten\n\n"
        "In L1 bis L8 legt ihr den Weg der Daten fest. Ein **Agent** entscheidet ihn selbst: Er liest die "
        "Frage, wählt ein **Werkzeug**, liest das Ergebnis und entscheidet, was als Nächstes kommt.\n\n"
        "**Werkzeuge** (links, alle im **Tool Mode** 🛠):\n"
        "1. **Web Search** – Websuche, News, RSS\n"
        "2. **URL** – eine Webseite lesen\n"
        "3. **Calculator** – rechnen\n"
        "4. **Current Date** – das heutige Datum\n"
        "5. **Run Flow** – der ganze Flow *01 Referenz-Checker* als ein Werkzeug\n\n"
        "## ▶ So startet ihr\n"
        "1. Kopie anlegen (*Duplicate*).\n"
        "2. Im **KI-Modell** die Quelle **Cluster** wählen: Kleine lokale Modelle scheitern an Werkzeugen.\n"
        "3. Im **Playground** fragen, z. B. *Was ist der neueste Beitrag im RSS-Feed "
        "https://bibliotheksportal.de/feed/ und vor wie vielen Tagen ist er erschienen?*\n"
        "4. Über der Antwort die Schritte aufklappen: Welches Werkzeug, mit welcher Eingabe?\n\n"
        "Anleitung mit Übungen: `anleitungen/lernpfad/L9_agenten.md`",
        -620, -420, breite=520)

    suche = f.baustein("UnifiedWebSearch", 0, -380, "werkzeug", {"hl": "de", "gl": "DE", "ceid": "DE:de"},
                       titel="Websuche (Web Search)", werkzeug=True)
    seite = f.baustein("URLComponent", 0, 80, "werkzeug", {"headers": [{"key": "User-Agent", "value": USER_AGENT}]},
                       titel="Webseite holen (URL)", werkzeug=True)
    rechner = f.baustein("CalculatorComponent", 0, 520, "werkzeug", titel="Taschenrechner (Calculator)", werkzeug=True)
    datum = f.baustein("CurrentDate", 0, 820, "werkzeug", {"timezone": "Europe/Berlin"},
                       titel="Datum (Current Date)", werkzeug=True)
    referenzen = f.baustein("RunFlow", 0, 1120, "referenzen", {"flow_name_selected": ZIEL_FLOW},
                            titel="Referenz-Checker (Run Flow)", werkzeug=True)
    modell = f.baustein(KI_MODELL, 460, -420, "agent")
    eingabe = f.baustein("ChatInput", 460, 520, "frage")
    agent = f.baustein("Agent", 920, 0, "recherche", {
        "system_prompt": ANWEISUNGEN,
        # Eigene Bausteine statt der eingebauten Werkzeuge, damit man sie sieht und einstellen kann
        "add_current_date_tool": False,
        "add_calculator_tool": False,
    }, titel="Recherche-Agent")
    ausgabe = f.baustein("ChatOutput", 1380, 120, "antwort", titel="Antwort")
    for werkzeug in (suche, seite, rechner, datum, referenzen):
        f.verbinden(werkzeug, "component_as_tool", agent, "tools")
    f.verbinden(modell, "model_output", agent, "model")
    f.verbinden(eingabe, "message", agent, "input_value")
    f.verbinden(agent, "response", ausgabe, "input_value")
    return f
