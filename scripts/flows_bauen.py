"""Baut die Beispiel-Flows über die Langflow-API und speichert sie in flows/.

Für Betreuende und Entwickler:innen, nicht für Teilnehmende. Langflow muss laufen
(docker compose up -d). Dann:

    uv run --with httpx scripts/flows_bauen.py            # Flows bauen und exportieren
    uv run --with httpx scripts/flows_bauen.py --testen   # zusätzlich jeden Flow einmal ausführen

Die Flows werden aus den Bausteinen gebaut, die Langflow gerade kennt. So passen Code und
Felder immer zur installierten Langflow-Version und zu komponenten/bibliothek/.
"""

import argparse
import copy
import json
import sys
import time
import uuid
from pathlib import Path

import httpx

LANGFLOW = "http://localhost:7860"
WURZEL = Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "flows"
NAMENSRAUM = uuid.UUID("5d0c3f8e-6a55-4d0b-9a57-3b7f1c2e9a10")

BIB = "ext:bibliothek:{}Component@extra"
KI_MODELL, REFERENZEN, ANREICHERN, VERZEICHNIS = (BIB.format(n) for n in (
    "KIModell", "ReferenzenPruefen", "QuellenAnreichern", "LiteraturverzeichnisFinden"))
OPENALEX, VOLLTEXTE, KATALOG = (BIB.format(n) for n in ("OpenAlexSuche", "VolltexteHolen", "Katalogsuche"))


class Langflow:
    def __init__(self, url: str):
        self.http = httpx.Client(base_url=url, timeout=900)
        token = self.http.get("/api/v1/auto_login").json()["access_token"]
        self.http.headers["Authorization"] = f"Bearer {token}"
        schluessel = self.http.post("/api/v1/api_key/", json={"name": "flows_bauen"}).json()
        self.http.headers["x-api-key"] = schluessel["api_key"]
        katalog = self.http.get("/api/v1/all").json()
        self.bausteine = {typ: b for kategorie in katalog.values() if isinstance(kategorie, dict)
                          for typ, b in kategorie.items() if isinstance(b, dict) and "template" in b}

    def prompt_pruefen(self, knoten: dict) -> dict:
        antwort = self.http.post("/api/v1/validate/prompt", json={
            "name": "template", "template": knoten["template"]["template"]["value"], "frontend_node": knoten})
        antwort.raise_for_status()
        return antwort.json()["frontend_node"]

    def werkzeug_modus(self, knoten: dict) -> dict:
        antwort = self.http.post("/api/v1/custom_component/update", json={
            "code": knoten["template"]["code"]["value"], "template": knoten["template"],
            "field": "tool_mode", "field_value": True, "tool_mode": True})
        antwort.raise_for_status()
        neu = antwort.json()
        neu["tool_mode"] = True
        return neu


class Flow:
    def __init__(self, lf: Langflow, datei: str, name: str, beschreibung: str, symbol: str):
        self.lf, self.datei, self.name, self.beschreibung, self.symbol = lf, datei, name, beschreibung, symbol
        self.id = str(uuid.uuid5(NAMENSRAUM, name))
        self.knoten: list[dict] = []
        self.kanten: list[dict] = []

    def baustein(self, typ: str, x: float, y: float, kurz: str, werte: dict | None = None,
                 titel: str | None = None, werkzeug: bool = False) -> str:
        knoten = copy.deepcopy(self.lf.bausteine[typ])
        for feld, wert in (werte or {}).items():
            knoten["template"][feld]["value"] = wert
        if titel:
            knoten["display_name"] = titel
        if "template" in (werte or {}) and knoten["template"]["template"].get("type") == "prompt":
            knoten = self.lf.prompt_pruefen(knoten)
        if werkzeug:
            knoten = self.lf.werkzeug_modus(knoten)
        # "ext:bibliothek:OpenAlexSucheComponent@extra" -> "OpenAlexSuche-suche"
        praefix = typ.split(":")[-1].split("Component@")[0] if typ.startswith("ext:") else typ.replace(" ", "")
        knoten_id = f"{praefix}-{kurz}"
        assert all(k["id"] != knoten_id for k in self.knoten), f"doppelte Knoten-ID {knoten_id}"
        self.knoten.append({
            "id": knoten_id, "type": "genericNode", "position": {"x": x, "y": y},
            "data": {"id": knoten_id, "type": typ, "node": knoten, "showNode": True},
        })
        return knoten_id

    def notiz(self, text: str, x: float, y: float, breite: int = 440, farbe: str = "blue") -> None:
        notiz_id = f"note-{len(self.knoten)}"
        # Höhe grob aus der Textlänge schätzen, damit nichts abgeschnitten wird
        zeichen_pro_zeile = breite // 9
        zeilen = sum(3 if z.startswith("#") else max(1, -(-len(z) // zeichen_pro_zeile)) for z in text.split("\n"))
        hoehe = 80 + 34 * zeilen
        self.knoten.append({
            "id": notiz_id, "type": "noteNode", "position": {"x": x, "y": y},
            "width": breite, "height": hoehe, "measured": {"width": breite, "height": hoehe},
            "data": {"id": notiz_id, "type": "note", "node": {
                "description": text, "display_name": "", "documentation": "",
                "template": {"backgroundColor": farbe}}},
        })

    def _knoten(self, knoten_id: str) -> dict:
        return next(k for k in self.knoten if k["id"] == knoten_id)["data"]

    def verbinden(self, quelle: str, ausgang: str, ziel: str, feld: str) -> None:
        q, z = self._knoten(quelle), self._knoten(ziel)
        # Bausteine mit mehreren Ausgängen zeigen im Editor nur den gewählten an
        q["selected_output"] = ausgang
        ausgabe = next(o for o in q["node"]["outputs"] if o["name"] == ausgang)
        eingang = z["node"]["template"][feld]
        griff_q = {"dataType": q["type"], "id": quelle, "name": ausgang, "output_types": ausgabe["types"]}
        griff_z = {"fieldName": feld, "id": ziel, "inputTypes": eingang.get("input_types") or [],
                   "type": eingang["type"]}

        def text(griff: dict) -> str:
            return json.dumps(griff, ensure_ascii=False).replace('"', "œ")

        self.kanten.append({
            "id": f"reactflow__edge-{quelle}{text(griff_q)}-{ziel}{text(griff_z)}",
            "source": quelle, "target": ziel, "sourceHandle": text(griff_q), "targetHandle": text(griff_z),
            "data": {"sourceHandle": griff_q, "targetHandle": griff_z}, "animated": False, "className": "",
        })

    def als_json(self) -> dict:
        return {
            "id": self.id, "name": self.name, "description": self.beschreibung, "icon": self.symbol,
            "is_component": False, "endpoint_name": None, "tags": ["bibliothekshackathon"],
            "data": {"nodes": self.knoten, "edges": self.kanten, "viewport": {"x": 0, "y": 0, "zoom": 0.6}},
        }


# ---------------------------------------------------------------------------------------------
# Die Flows
# ---------------------------------------------------------------------------------------------

def flow_hallo(lf: Langflow) -> Flow:
    f = Flow(lf, "00_hallo_ki", "00 Erste Schritte – Hallo KI",
             "Der kleinste mögliche Flow: Frage stellen, Anweisung formulieren, KI antworten lassen.", "MessagesSquare")
    f.notiz(
        "# 👋 Willkommen!\n\n"
        "Ein **Flow** ist eine Kette von Bausteinen. Die Daten fließen **von links nach rechts** "
        "über die Verbindungslinien.\n\n"
        "1. **Chat Input** – eure Frage aus dem Playground\n"
        "2. **Prompt Template** – die Anweisung an die KI. `{frage}` ist ein Platzhalter.\n"
        "3. **KI-Modell** – das Sprachmodell (Cluster oder lokal)\n"
        "4. **Chat Output** – zeigt die Antwort an\n\n"
        "## ▶ Ausprobieren\n"
        "Oben rechts auf **Playground** klicken und eine Frage stellen.\n\n"
        "## 🔧 Verändern\n"
        "- Im Prompt die Rolle ändern (z. B. „antworte in Leichter Sprache“)\n"
        "- Beim KI-Modell **Kreativität** hochdrehen\n"
        "- Beim KI-Modell die **Quelle** wechseln: Cluster ↔ Lokal",
        -60, -120)
    eingabe = f.baustein("ChatInput", 420, 120, "frage")
    prompt = f.baustein("Prompt Template", 820, 60, "anweisung", {"template": (
        "Du bist eine freundliche, kompetente Auskunftsperson in einer wissenschaftlichen Bibliothek.\n"
        "Antworte kurz, auf Deutsch und in einfacher Sprache. Wenn du etwas nicht sicher weißt, sag das ehrlich.\n\n"
        "Frage: {frage}")}, titel="Prompt: Anweisung")
    modell = f.baustein(KI_MODELL, 1220, 20, "modell")
    ausgabe = f.baustein("ChatOutput", 1620, 120, "antwort")
    f.verbinden(eingabe, "message", prompt, "frage")
    f.verbinden(prompt, "prompt", modell, "input_value")
    f.verbinden(modell, "text_output", ausgabe, "input_value")
    return f


def flow_referenzen(lf: Langflow) -> Flow:
    f = Flow(lf, "01_referenz_checker", "01 Referenz-Checker",
             "Prüft ein Literaturverzeichnis: Gibt es die Quellen wirklich, stimmen Jahr und Autor:innen, "
             "wurde etwas zurückgezogen?", "ListChecks")
    f.notiz(
        "# 🔎 Referenz-Checker\n\n"
        "**Problem:** KI-Tools erfinden Literaturangaben, und auch echte Verzeichnisse enthalten Fehler.\n\n"
        "**So arbeitet der Flow:**\n"
        "1. Ihr fügt im Playground ein Literaturverzeichnis ein.\n"
        "2. **Literaturangaben prüfen** gleicht jede Angabe mit **Crossref** ab (Titel, Jahr, "
        "Erstautor:in, DOI) und fragt nach **zurückgezogenen** Artikeln.\n"
        "3. Die **KI** schreibt daraus einen verständlichen Prüfbericht.\n\n"
        "**Testdaten:** `daten/literaturliste_zum_pruefen.txt` – mit eingebauten Fehlern.\n\n"
        "## 💡 Ideen zum Weiterbauen\n"
        "- Statt Chat: PDF hochladen (**Read File** + **Literaturverzeichnis finden** davor)\n"
        "- Nicht gefundene Bücher in der **Katalogsuche** nachschlagen\n"
        "- Den Bericht als Datei speichern (**Write File**)",
        -60, -160)
    eingabe = f.baustein("ChatInput", 440, 120, "verzeichnis", titel="Literaturverzeichnis (Chat)")
    pruefen = f.baustein(REFERENZEN, 840, 60, "pruefen")
    prompt = f.baustein("Prompt Template", 1260, 0, "bericht", {"template": (
        "ABGLEICH EINES LITERATURVERZEICHNISSES MIT CROSSREF:\n{pruefergebnis}\n\n---\n"
        "Du unterstützt eine Bibliothek beim Prüfen von Literaturverzeichnissen.\n"
        "Oben steht das Ergebnis eines automatischen Abgleichs mit der Datenbank Crossref.\n"
        "Bedeutung: ✅ bestätigt | ⚠️ Abweichung (z. B. falsches Jahr, falsche:r Erstautor:in, DOI passt nicht) | "
        "❓ nicht gefunden (vielleicht erfunden – oder ein Buch/eine Webseite ohne DOI) | 🚫 zurückgezogen\n\n"
        "Schreibe einen kurzen Prüfbericht auf Deutsch:\n"
        "1. Gesamteinschätzung in zwei Sätzen.\n"
        "2. Alle Angaben mit Problemen als Liste: Nummer, Problem, konkreter Korrekturvorschlag.\n"
        "3. Welche Angaben sollte jemand von Hand im Bibliothekskatalog prüfen?\n"
        "Verwende nur Informationen aus dem Abgleich. Erfinde keine Daten.")}, titel="Prompt: Prüfbericht")
    modell = f.baustein(KI_MODELL, 1680, -40, "modell")
    ausgabe = f.baustein("ChatOutput", 2080, 60, "bericht", titel="Prüfbericht")
    tabelle = f.baustein("ChatOutput", 1260, 620, "tabelle", titel="Ergebnistabelle")
    f.verbinden(eingabe, "message", pruefen, "literaturangaben")
    f.verbinden(pruefen, "bericht", prompt, "pruefergebnis")
    f.verbinden(pruefen, "tabelle", tabelle, "input_value")
    f.verbinden(prompt, "prompt", modell, "input_value")
    f.verbinden(modell, "text_output", ausgabe, "input_value")
    return f


def flow_masterarbeit(lf: Langflow) -> Flow:
    f = Flow(lf, "02_masterarbeit_quellenanalyse", "02 Masterarbeit – Quellen analysieren",
             "Liest eine Abschlussarbeit (PDF), zieht alle verwendeten Publikationen heraus, reichert sie mit "
             "Metadaten an und lässt die KI die Quellenbasis analysieren.", "GraduationCap")
    f.notiz(
        "# 🎓 Quellen einer Abschlussarbeit analysieren\n\n"
        "**Problem:** Wer eine Arbeit berät oder begutachtet, will schnell sehen: Auf welche Literatur "
        "stützt sie sich? Ist sie aktuell, vielfältig, frei zugänglich?\n\n"
        "**So arbeitet der Flow:**\n"
        "1. **Read File:** PDF hochladen (Beispiel: `daten/beispiel_masterarbeit.pdf`)\n"
        "2. **Literaturverzeichnis finden** schneidet das Verzeichnis aus.\n"
        "3. **Quellen anreichern** holt für jede Angabe Abstract, Thema, Zitationen und "
        "Open-Access-Status aus **OpenAlex** und rechnet eine Statistik.\n"
        "4. Die **KI** schreibt die Analyse – euren Auftrag gebt ihr im Playground ein.\n\n"
        "## 💡 Ideen zum Weiterbauen\n"
        "- Freie Volltexte der Quellen holen (**Volltexte holen**)\n"
        "- Die Quellentabelle als Excel/CSV speichern (**Write File**)\n"
        "- Zusätzlich jede Quelle prüfen (**Literaturangaben prüfen**)",
        -60, -200)
    datei = f.baustein("File", 460, 0, "arbeit", titel="Abschlussarbeit (PDF)")
    verzeichnis = f.baustein(VERZEICHNIS, 860, 40, "verzeichnis")
    anreichern = f.baustein(ANREICHERN, 1260, 20, "anreichern")
    auftrag = f.baustein("ChatInput", 1260, 480, "auftrag", titel="Auftrag (Chat)")
    prompt = f.baustein("Prompt Template", 1680, 80, "analyse", {"template": (
        "AUSWERTUNG DER QUELLEN:\n{quellen}\n\n---\n"
        "Du bist Fachreferent:in in einer wissenschaftlichen Bibliothek und berätst Studierende.\n"
        "Oben steht eine automatische Auswertung aller Quellen aus dem Literaturverzeichnis einer "
        "Abschlussarbeit (Metadaten aus OpenAlex).\n\n"
        "Auftrag: {auftrag}\n\n"
        "Erstelle auf Deutsch eine Quellenanalyse mit diesen Abschnitten:\n"
        "1. Überblick: Umfang, Zeitraum, Anteil Open Access, Publikationstypen. Übernimm die Zahlen aus der "
        "STATISTIK, rechne nicht selbst.\n"
        "2. Thematische Schwerpunkte: 3–5 Themengruppen, jeweils mit den Nummern der Quellen.\n"
        "3. Auffälligkeiten: z. B. veraltete oder fehlende aktuelle Literatur, Einseitigkeit, nicht gefundene Angaben.\n"
        "4. Empfehlungen: Welche Art von Literatur könnte ergänzt werden?\n"
        "Nenne Quellen immer mit Nummer, z. B. [3], und nur Nummern, die in der Auswertung vorkommen. "
        "Erfinde keine Quellen.")}, titel="Prompt: Quellenanalyse")
    modell = f.baustein(KI_MODELL, 2100, 20, "modell")
    ausgabe = f.baustein("ChatOutput", 2500, 120, "analyse", titel="Quellenanalyse")
    f.verbinden(datei, "message", verzeichnis, "dokument")
    f.verbinden(verzeichnis, "verzeichnis", anreichern, "literaturangaben")
    f.verbinden(anreichern, "ueberblick", prompt, "quellen")
    f.verbinden(auftrag, "message", prompt, "auftrag")
    f.verbinden(prompt, "prompt", modell, "input_value")
    f.verbinden(modell, "text_output", ausgabe, "input_value")
    return f


def flow_review(lf: Langflow) -> Flow:
    f = Flow(lf, "03_literaturreview", "03 Literaturreview – Forschungslücken finden",
             "Sammelt verlagsübergreifend Publikationen zu einer Forschungsfrage, lädt freie Volltexte und lässt "
             "die KI Themen, Widersprüche und Forschungslücken herausarbeiten.", "Microscope")
    f.notiz(
        "# 🔬 Text- und Data-Mining: Literaturüberblick\n\n"
        "**Problem:** Für einen Überblick (Systematic Review) muss man Literatur vieler Verlage "
        "sammeln, lesen und vergleichen.\n\n"
        "**So arbeitet der Flow:**\n"
        "1. Ihr stellt im Playground eine **Forschungsfrage** (gern auf Deutsch).\n"
        "2. Die **erste KI** macht daraus englische Suchbegriffe.\n"
        "3. **Literatursuche (OpenAlex)** findet Publikationen aller Verlage.\n"
        "4. **Volltexte holen** lädt freie PDFs (Open Access), sonst das Abstract.\n"
        "5. Die **zweite KI** vergleicht die Texte und benennt **Forschungslücken**.\n\n"
        "**Beispielfrage:** *Wie verändern Sprachmodelle die Auskunft in wissenschaftlichen Bibliotheken?*\n\n"
        "## 💡 Ideen zum Weiterbauen\n"
        "- Filter ändern: Jahre, nur Open Access, Sortierung nach Zitationen\n"
        "- Jede Publikation einzeln zusammenfassen lassen (**Batch Run**)\n"
        "- Eine PRISMA-artige Tabelle der Ein-/Ausschlüsse erzeugen\n\n"
        "⚠️ Kleine lokale Modelle vertragen wenig Text: dann **Höchstens Dokumente** und "
        "**Zeichen pro Dokument** verringern.",
        -60, -240)
    frage = f.baustein("ChatInput", 460, 120, "frage", titel="Forschungsfrage (Chat)")
    such_prompt = f.baustein("Prompt Template", 860, -160, "suchbegriffe", {"template": (
        "Formuliere aus der folgenden Forschungsfrage eine kurze englische Suchanfrage für eine "
        "Literaturdatenbank: 3 bis 6 Schlüsselbegriffe, ohne Operatoren, ohne Anführungszeichen, ohne Erklärung.\n"
        "Nimm eindeutige Fachbegriffe. Beispiel: Die Bibliothek als Einrichtung heißt 'academic libraries' oder "
        "'library services' – 'libraries' allein findet auch Software-Bibliotheken.\n"
        "Antworte nur mit der Suchanfrage.\n\nForschungsfrage: {frage}")}, titel="Prompt: Suchbegriffe")
    such_modell = f.baustein(KI_MODELL, 1260, -220, "suche", {"temperature": 0.0}, titel="KI-Modell (Suchbegriffe)")
    suche = f.baustein(OPENALEX, 1660, -160, "suche", {"anzahl": 8})
    volltexte = f.baustein(VOLLTEXTE, 2060, -60, "volltexte", {"max_dokumente": 6, "max_zeichen": 2500})
    review_prompt = f.baustein("Prompt Template", 2460, 60, "review", {"template": (
        "GEFUNDENE PUBLIKATIONEN:\n{texte}\n\n---\n"
        "Du unterstützt eine systematische Literaturrecherche in einer wissenschaftlichen Bibliothek.\n"
        "Forschungsfrage: {frage}\n"
        "Verwendete Suchanfrage: {suchanfrage}\n\n"
        "Oben stehen die gefundenen Publikationen (Volltext-Auszüge oder Abstracts), jeweils mit Nummer.\n\n"
        "Erstelle auf Deutsch einen strukturierten Literaturüberblick:\n"
        "1. Tabelle: Nr. | Jahr | Kernaussage in einem Satz | Methode\n"
        "2. Themencluster: 2–4 Gruppen mit den zugehörigen Nummern\n"
        "3. Übereinstimmungen und Widersprüche zwischen den Arbeiten\n"
        "4. Forschungslücken: Was wird nicht oder kaum untersucht? Begründe mit Nummern.\n"
        "5. Vorschläge für weitere Suchbegriffe\n"
        "Stütze jede Aussage auf Nummern, z. B. [2]. Passt eine Publikation nicht zur Frage, sag das. "
        "Erfinde nichts. Antworte auf Deutsch.")}, titel="Prompt: Literaturüberblick")
    review_modell = f.baustein(KI_MODELL, 2880, 0, "review", titel="KI-Modell (Überblick)")
    ausgabe = f.baustein("ChatOutput", 3280, 120, "review", titel="Literaturüberblick")
    f.verbinden(frage, "message", such_prompt, "frage")
    f.verbinden(such_prompt, "prompt", such_modell, "input_value")
    f.verbinden(such_modell, "text_output", suche, "suchanfrage")
    f.verbinden(suche, "tabelle", volltexte, "publikationen")
    f.verbinden(volltexte, "texte", review_prompt, "texte")
    f.verbinden(frage, "message", review_prompt, "frage")
    f.verbinden(such_modell, "text_output", review_prompt, "suchanfrage")
    f.verbinden(review_prompt, "prompt", review_modell, "input_value")
    f.verbinden(review_modell, "text_output", ausgabe, "input_value")
    return f


def flow_agent(lf: Langflow) -> Flow:
    f = Flow(lf, "04_recherche_agent", "04 Recherche-Agent",
             "Ein KI-Agent, der selbst entscheidet, welche Werkzeuge er nutzt: Literatursuche, Katalogsuche und "
             "Quellenprüfung.", "Bot")
    f.notiz(
        "# 🤖 Recherche-Agent\n\n"
        "Die anderen Flows laufen immer gleich ab. Ein **Agent** entscheidet dagegen **selbst**, "
        "welche Werkzeuge er in welcher Reihenfolge nutzt.\n\n"
        "**Werkzeuge** (links, im Werkzeug-Modus 🛠):\n"
        "- **Literatursuche (OpenAlex)** – Artikel aller Verlage\n"
        "- **Katalogsuche (hbz / lobid)** – Bücher im Verbundkatalog\n"
        "- **Literaturangaben prüfen (Crossref)** – Existenz und Korrektheit\n\n"
        "**Fragt z. B.:**\n"
        "- *Finde drei aktuelle Artikel über Open Access in Deutschland.*\n"
        "- *Gibt es ein Buch von Umberto Eco über Abschlussarbeiten?*\n"
        "- *Stimmt diese Angabe? Smith, J. (2019). The intelligent library. Library Hi Tech.*\n\n"
        "## 💡 Ideen\n"
        "- Anweisungen des Agenten ändern (Feld **Agent Instructions**)\n"
        "- Weitere Werkzeuge anschließen, z. B. **Wikipedia** oder **URL**\n\n"
        "⚠️ Agenten brauchen Modelle, die Werkzeuge bedienen können. Kleine lokale Modelle "
        "scheitern daran oft – dann den Cluster nehmen.",
        -560, -260)
    suche = f.baustein(OPENALEX, -60, -320, "werkzeug", {"anzahl": 5}, werkzeug=True)
    katalog = f.baustein(KATALOG, -60, 330, "werkzeug", werkzeug=True)
    pruefen = f.baustein(REFERENZEN, -60, 700, "werkzeug", werkzeug=True)
    modell = f.baustein(KI_MODELL, 360, -260, "agent")
    eingabe = f.baustein("ChatInput", 360, 420, "frage")
    agent = f.baustein("Agent", 800, 0, "recherche", {
        "system_prompt": (
            "Du bist ein Recherche-Assistent einer wissenschaftlichen Bibliothek. Du hilfst bei Literatursuche "
            "und Quellenprüfung.\n\n"
            "Werkzeuge:\n"
            "- Literatursuche (OpenAlex): Zeitschriftenartikel suchen. Suchbegriffe auf Englisch.\n"
            "- Katalogsuche (hbz / lobid): Bücher und deutschsprachige Literatur im Bibliothekskatalog.\n"
            "- Literaturangaben prüfen (Crossref): prüfen, ob Angaben existieren und korrekt sind.\n\n"
            "Regeln:\n"
            "- Nutze die Werkzeuge, statt aus dem Gedächtnis zu antworten. Erfinde niemals Literatur.\n"
            "- Nenne bei jeder Publikation Autor:innen, Jahr, Titel und DOI oder Link.\n"
            "- Antworte auf Deutsch, knapp und übersichtlich."),
        "add_current_date_tool": False,
        "add_calculator_tool": False,
    }, titel="Recherche-Agent")
    ausgabe = f.baustein("ChatOutput", 1240, 120, "antwort")
    for werkzeug in (suche, katalog, pruefen):
        f.verbinden(werkzeug, "component_as_tool", agent, "tools")
    f.verbinden(modell, "model_output", agent, "model")
    f.verbinden(eingabe, "message", agent, "input_value")
    f.verbinden(agent, "response", ausgabe, "input_value")
    return f


# ---------------------------------------------------------------------------------------------

TESTS = {
    "00 Erste Schritte – Hallo KI": {"eingabe": "Wie lange darf ich ein Buch normalerweise ausleihen?"},
    "01 Referenz-Checker": {"eingabe_datei": "daten/literaturliste_zum_pruefen.txt"},
    "02 Masterarbeit – Quellen analysieren": {"eingabe": "Bitte analysiere die Quellen dieser Masterarbeit.",
                                                "pdf": "daten/beispiel_masterarbeit.pdf"},
    "03 Literaturreview – Forschungslücken finden": {
        "eingabe": "Wie verändern Sprachmodelle die Auskunft in wissenschaftlichen Bibliotheken?"},
    "04 Recherche-Agent": {"eingabe": "Gibt es ein Buch von Umberto Eco darüber, wie man eine Abschlussarbeit "
                                      "schreibt? Suche im Katalog."},
}


def speichern(lf: Langflow, flow: Flow) -> None:
    daten = flow.als_json()
    lf.http.delete(f"/api/v1/flows/{flow.id}")
    antwort = lf.http.post("/api/v1/flows/", json=daten)
    if antwort.status_code >= 400:
        sys.exit(f"Fehler beim Anlegen von {flow.name}: {antwort.text[:500]}")
    datei = ZIEL / f"{flow.datei}.json"
    datei.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✔ {flow.name} → {datei.relative_to(WURZEL)}")


def testen(lf: Langflow, flow: Flow) -> None:
    test = TESTS[flow.name]
    eingabe = test.get("eingabe") or (WURZEL / test["eingabe_datei"]).read_text(encoding="utf-8")
    tweaks = {}
    if "pdf" in test:
        pfad = WURZEL / test["pdf"]
        hochgeladen = lf.http.post("/api/v2/files", files={"file": (pfad.name, pfad.read_bytes(), "application/pdf")})
        hochgeladen.raise_for_status()
        datei_knoten = next(k["id"] for k in flow.knoten if k["data"].get("type") == "File")
        tweaks[datei_knoten] = {"path": [hochgeladen.json()["path"]]}
    start = time.time()
    antwort = lf.http.post(f"/api/v1/run/{flow.id}", params={"stream": "false"}, json={
        "input_value": eingabe, "input_type": "chat", "output_type": "chat", "tweaks": tweaks,
        "session_id": f"test-{uuid.uuid4()}"})  # neue Sitzung: kein Chatverlauf aus früheren Tests
    dauer = time.time() - start
    if antwort.status_code >= 400:
        print(f"  ✘ Test fehlgeschlagen nach {dauer:.0f} s: {antwort.text[:1500]}")
        return
    for ergebnis in antwort.json()["outputs"][0]["outputs"]:
        nachricht = (ergebnis.get("results") or {}).get("message") or {}
        text = nachricht.get("text") if isinstance(nachricht, dict) else str(nachricht)
        print(f"  ── Ausgabe ({dauer:.0f} s):\n" + "\n".join("  │ " + z for z in str(text).splitlines()[:60]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--testen", action="store_true", help="jeden Flow nach dem Bauen einmal ausführen")
    parser.add_argument("--nur", help="nur Flows bauen, deren Name diesen Text enthält, z. B. '01'")
    parser.add_argument("--url", default=LANGFLOW)
    args = parser.parse_args()

    lf = Langflow(args.url)
    ZIEL.mkdir(exist_ok=True)
    for baue in (flow_hallo, flow_referenzen, flow_masterarbeit, flow_review, flow_agent):
        flow = baue(lf)
        if args.nur and args.nur not in flow.name:
            continue  # gebaut wird trotzdem alles, damit Fehler in jedem Flow auffallen
        speichern(lf, flow)
        if args.testen:
            testen(lf, flow)


if __name__ == "__main__":
    main()
