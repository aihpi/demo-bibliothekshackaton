"""L7 Verzweigen und absichern: Auskunftsanfragen prüfen und auf den passenden Weg schicken."""

from flows_bauen import KI_MODELL, Flow

DATEI = "L7_verzweigen_und_absichern"

ROUTEN = [
    {
        "route_category": "Ausleihe",
        "route_description": "Fragen zu Ausleihe, Verlängerung, Vormerkung, Gebühren, Konto und Bibliotheksausweis",
        "output_value": "",
    },
    {
        "route_category": "Recherche",
        "route_description": "Fragen nach Literatur, Fachdatenbanken, Quellen oder Recherchestrategien",
        "output_value": "",
    },
    {
        "route_category": "Technik",
        "route_description": "Probleme mit WLAN, VPN, Druckern, Formularen oder dem Zugang zu E-Medien",
        "output_value": "Diese Anfrage geht an den IT-Service der Bibliothek: it@musterbibliothek.example",
    },
]

TEST = {
    # Eine Recherchefrage: Sie läuft durch Guardrails, Smart Router, Antwortentwurf und Human Input.
    "eingabe": "Ich schreibe meine Bachelorarbeit über Open Access in Bibliotheken. Wie finde ich gute Fachartikel dazu?",
    "werte": {"KIModell-weiche": {"quelle": "Cluster (LiteLLM)"}, "KIModell-entwurf": {"quelle": "Cluster (LiteLLM)"}},
    "leer_ok": [
        # Nicht genommene Wege werden gar nicht ausgeführt.
        "ChatOutput-regel_ja",
        "ChatOutput-gestoppt",
        "ChatOutput-ausleihe",
        "ChatOutput-technik",
        "ChatOutput-sonstiges",
        # Human Input hält nur im Playground (API v2) an. Der Testlauf baut über API v1; dort geben beide
        # Ausgänge eine leere Nachricht weiter, statt zu warten.
        "ChatOutput-freigegeben",
        "ChatOutput-abgelehnt",
    ],
}


def _live(f: Flow, knoten_id: str, feld: str, wert) -> None:
    """Wie eine Eingabe im Editor: erst den Wert setzen, dann den Baustein reagieren lassen (neue Ausgänge)."""
    daten = f._knoten(knoten_id)
    daten["node"]["template"][feld]["value"] = wert
    daten["node"] = f.lf.feld_aendern(daten["node"], feld, wert)


def bauen(lf) -> Flow:
    f = Flow(
        lf,
        DATEI,
        "L7 Verzweigen und absichern",
        "Lernpfad 7: Auskunftsanfragen mit If-Else und Smart Router auf den passenden Weg schicken, mit "
        "Guardrails absichern und einen KI-Antwortentwurf von einem Menschen freigeben lassen.",
        "Split",
    )
    f.notiz(
        "# 🔀 L7 Verzweigen und absichern\n\n"
        "Eine **Auskunftsanfrage** aus dem Playground läuft zwei Wege gleichzeitig:\n\n"
        "**Oben: eine feste Regel.** **If-Else** prüft, ob das Wort *Fernleihe* vorkommt. Immer gleich, ohne KI.\n\n"
        "**Unten: die Auskunfts-Weiche.**\n"
        "1. **Guardrails** hält Anfragen mit E-Mail-Adressen, Passwörtern oder Manipulationsversuchen an.\n"
        "2. **Smart Router** lässt die KI entscheiden: Ausleihe, Recherche, Technik oder Sonstiges.\n"
        "3. Bei *Recherche* schreibt die KI einen Antwortentwurf, und **Human Input** fragt euch: "
        "freigeben oder ablehnen?\n\n"
        "## ▶ So startet ihr\n"
        "1. Kopie anlegen (*Duplicate*).\n"
        "2. **Playground** öffnen und eine Anfrage aus `daten/lernpfad/auskunftsanfragen.txt` abschicken.\n"
        "3. Bei einer Recherchefrage erscheinen Knöpfe zum Freigeben oder Ablehnen.\n\n"
        "Es erscheinen nur die Nachrichten der Wege, die genommen wurden.\n\n"
        "Anleitung mit Übungen: `anleitungen/lernpfad/L7_verzweigen_und_absichern.md`",
        -260,
        -700,
        breite=520,
    )

    anfrage = f.baustein("ChatInput", 400, 200, "anfrage")

    # Oben: die feste Regel
    regel = f.baustein(
        "ConditionalRouter",
        850,
        -560,
        "fernleihe",
        {
            "operator": "contains",
            "match_text": "Fernleihe",
            "true_case_message": "Regel trifft zu: Die Anfrage geht an die Fernleihstelle.",
            "false_case_message": "Regel trifft nicht zu: Die Anfrage geht an die allgemeine Auskunft.",
        },
    )
    f.notiz("**Regel**: Fernleihe?", 850, -700, breite=320, farbe="amber")
    ja = f.baustein("ChatOutput", 1300, -640, "regel_ja", {"sender_name": "Regel (If-Else)"})
    nein = f.baustein("ChatOutput", 1300, -300, "regel_nein", {"sender_name": "Regel (If-Else)"})
    f.verbinden(anfrage, "message", regel, "input_text")
    f.verbinden(regel, "true_result", ja, "input_value")
    f.verbinden(regel, "false_result", nein, "input_value")

    # Unten: Guardrails → Smart Router → Antwortentwurf → Human Input
    pruefen = f.baustein(
        "GuardrailValidatorV2",
        850,
        160,
        "pruefen",
        auswahl={"checking_method": "Rules only"},
    )
    _live(f, pruefen, "enabled_guardrails", ["PII", "Tokens/Passwords", "Jailbreak", "Prompt Injection"])
    gestoppt = f.baustein("ChatOutput", 1300, 760, "gestoppt", {"sender_name": "Guardrails"})
    f.verbinden(anfrage, "message", pruefen, "input_text")
    f.verbinden(pruefen, "failed_result", gestoppt, "input_value")

    weiche_modell = f.baustein(KI_MODELL, 850, 1100, "weiche", {"temperature": 0.0})
    f.notiz("**Modell für die Weiche**", 850, 960, breite=320, farbe="amber")
    weiche = f.baustein("SmartRouter", 1300, 120, "weiche")
    _live(f, weiche, "routes", ROUTEN)
    _live(f, weiche, "enable_else_output", True)
    f.verbinden(pruefen, "pass_result", weiche, "input_text")
    f.verbinden(weiche_modell, "model_output", weiche, "model")

    for ausgang, kurz, absender, y in (
        ("category_1_result", "ausleihe", "Weg: Ausleihe", -200),
        ("category_3_result", "technik", "Weg: Technik", 160),
        ("default_result", "sonstiges", "Weg: Sonstiges", 520),
    ):
        ziel = f.baustein("ChatOutput", 1780, y, kurz, {"sender_name": absender})
        f.verbinden(weiche, ausgang, ziel, "input_value")

    entwurf_prompt = f.baustein(
        "Prompt Template",
        1780,
        900,
        "entwurf",
        {
            "template": (
                "ANFRAGE:\n{anfrage}\n\n---\n"
                "Du arbeitest in der Auskunft einer wissenschaftlichen Bibliothek. Schreibe einen kurzen, freundlichen "
                "Antwortentwurf auf die Anfrage oben, auf Deutsch und per Sie. Beginne mit „Guten Tag,“.\n"
                "Nenne zwei oder drei konkrete erste Schritte, z. B. Katalog, Fachdatenbanken oder eine Rechercheberatung. "
                "Nenne keine bestimmten Titel und erfinde nichts. Höchstens 120 Wörter."
            )
        },
    )
    entwurf_modell = f.baustein(KI_MODELL, 2220, 860, "entwurf")
    f.notiz("**Modell für den Antwortentwurf**", 2220, 720, breite=320, farbe="amber")
    freigabe = f.baustein("HumanInput", 2660, 900, "freigabe")
    _live(f, freigabe, "decisions", ["Freigeben", "Ablehnen"])
    freigegeben = f.baustein("ChatOutput", 3100, 780, "freigegeben", {"sender_name": "Freigegeben"})
    abgelehnt = f.baustein("ChatOutput", 3100, 1140, "abgelehnt", {"sender_name": "Abgelehnt"})
    f.verbinden(weiche, "category_2_result", entwurf_prompt, "anfrage")
    f.verbinden(entwurf_prompt, "prompt", entwurf_modell, "input_value")
    f.verbinden(entwurf_modell, "text_output", freigabe, "prompt")
    f.verbinden(freigabe, "branch_freigeben", freigegeben, "input_value")
    f.verbinden(freigabe, "branch_ablehnen", abgelehnt, "input_value")

    f.notiz(
        "## ✋ Hier hält der Flow an\n"
        "**Human Input** zeigt den Entwurf im Playground und wartet, bis ein Mensch *Freigeben* oder *Ablehnen* "
        "wählt. Erst dann geht es auf dem gewählten Weg weiter.",
        2620,
        1360,
        breite=440,
        farbe="amber",
    )
    return f
