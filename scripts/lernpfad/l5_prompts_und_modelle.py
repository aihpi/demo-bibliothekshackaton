"""L5 Prompts und Modelle: eine Auskunft zur Benutzungsordnung, zweimal beantwortet, mit Gedächtnis und Datum."""

from flows_bauen import KI_MODELL, WURZEL, Flow

DATEI = "L5_prompts_und_modelle"

AUSKUNFT = (
    "BENUTZUNGSORDNUNG:\n{ordnung}\n\n"
    "HEUTE: {heute}\n\n"
    "BISHERIGES GESPRÄCH:\n{verlauf}\n\n---\n"
    "Du bist Auskunftsperson der Musterbibliothek. Beantworte die NEUE FRAGE für {zielgruppe}.\n"
    "Stütze dich nur auf die Benutzungsordnung oben und nenne den Paragrafen, z. B. (§ 3). Steht die Antwort "
    "nicht darin, sag das ehrlich und verweise an die Information der Bibliothek. Erfinde nichts.\n"
    "Antworte auf Deutsch in höchstens vier Sätzen.\n\n"
    "NEUE FRAGE: {frage}"
)

TEST = {
    "eingabe": "Wie lange darf ich ein Buch behalten, und was kostet es, wenn ich es zu spät zurückbringe?",
    # Standard in der .env ist oft das lokale Modell; der Test soll schnell und zuverlässig sein
    "werte": {"KIModell-auskunft": {"quelle": "Cluster (LiteLLM)"}},
}


def bauen(lf) -> Flow:
    f = Flow(
        lf,
        DATEI,
        "L5 Prompts und Modelle",
        "Lernpfad 5: Wie Prompt und Modelleinstellungen eine Antwort verändern. Prompt Template, KI-Modell, "
        "Language Model, Message History und Current Date.",
        "MessageSquareText",
    )
    f.notiz(
        "# 💬 L5 Prompts und Modelle\n\n"
        "Eine Auskunft zur **Benutzungsordnung** der Musterbibliothek. Der Flow zeigt, was eine Antwort "
        "bestimmt: der **Prompt** und die Einstellungen des **Modells**.\n\n"
        "1. **Chat Input** – die Frage aus dem Playground\n"
        "2. **Current Date** und **Message History** – heutiges Datum und bisheriges Gespräch\n"
        "3. **Prompt Template** – setzt Benutzungsordnung, Datum, Gespräch, Zielgruppe und Frage zusammen\n"
        "4. **KI-Modell** – beantwortet den Prompt (oben)\n"
        "5. **Language Model** – derselbe Prompt mit demselben Modell, aber eigener **System Message**: "
        "Antwort in Leichter Sprache (unten)\n\n"
        "## ▶ So startet ihr\n"
        "1. Kopie anlegen (*Duplicate*).\n"
        "2. **Playground** öffnen und fragen, z. B. *Wie lange darf ich ein Buch behalten?*\n"
        "3. Nachfragen, z. B. *Und wie oft kann ich verlängern?* Der Flow erinnert sich an das Gespräch.\n\n"
        "Anleitung mit Übungen: `anleitungen/lernpfad/L5_prompts_und_modelle.md`",
        -200,
        -260,
        breite=500,
    )

    frage = f.baustein("ChatInput", 420, 0, "frage", titel="Frage (Chat)")
    heute = f.baustein("CurrentDate", 420, 360, "heute", {"timezone": "Europe/Berlin"}, titel="Heutiges Datum")
    verlauf = f.baustein("Memory", 420, 640, "verlauf", {"n_messages": 10}, titel="Bisheriges Gespräch")
    prompt = f.baustein("Prompt Template", 860, 60, "auskunft", {"template": AUSKUNFT}, titel="Prompt: Auskunft")
    # Feste Werte direkt im Platzhalter: So läuft der Flow ohne Datei-Upload
    vorlage = f._knoten(prompt)["node"]["template"]
    vorlage["ordnung"]["value"] = (WURZEL / "daten/lernpfad/benutzungsordnung.txt").read_text(encoding="utf-8")
    vorlage["zielgruppe"]["value"] = "Studierende im ersten Semester"

    modell = f.baustein(KI_MODELL, 1300, -40, "auskunft", titel="KI-Modell (Auskunft)")
    antwort = f.baustein("ChatOutput", 1740, 40, "antwort", {"sender_name": "KI-Modell"}, titel="Antwort (KI-Modell)")

    leicht = f.baustein(
        "LanguageModelComponent",
        1740,
        520,
        "leicht",
        {
            "system_message": (
                "Du schreibst in Leichter Sprache: kurze Sätze, ein Gedanke pro Satz, keine Fachwörter "
                "ohne Erklärung, Zahlen als Ziffern."
            ),
        },
        titel="Language Model (Leichte Sprache)",
    )
    # Nicht speichern: Sonst stünde jede Antwort doppelt im Gesprächsverlauf
    antwort_leicht = f.baustein(
        "ChatOutput",
        2180,
        600,
        "leicht",
        {"sender_name": "Language Model", "should_store_message": False},
        titel="Antwort (Leichte Sprache)",
    )

    f.verbinden(frage, "message", prompt, "frage")
    f.verbinden(heute, "current_date", prompt, "heute")
    f.verbinden(verlauf, "messages_text", prompt, "verlauf")
    f.verbinden(prompt, "prompt", modell, "input_value")
    f.verbinden(modell, "text_output", antwort, "input_value")
    f.verbinden(modell, "model_output", leicht, "model")
    f.verbinden(prompt, "prompt", leicht, "input_value")
    f.verbinden(leicht, "text_output", antwort_leicht, "input_value")
    return f
