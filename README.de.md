<div style="background-color: #ffffff; color: #000000; padding: 10px;">
<img src="00_aisc/img/logo_aisc_bmftr.jpg">
<h1>Bibliothekshackathon: KI-Workflows ohne Programmieren</h1>
</div>

[English](README.md) | **Deutsch**

Eine Demo- und Arbeitsumgebung für Hackathons mit Bibliotheksbeschäftigten. Gruppen ohne Programmierkenntnisse bauen in [Langflow](https://www.langflow.org/) per Drag-and-drop KI-Workflows und KI-Agenten für echte Aufgaben wissenschaftlicher Bibliotheken: Literaturangaben prüfen, die Quellen einer Abschlussarbeit analysieren, verlagsübergreifend Literatur sammeln und Forschungslücken finden. Mitgeliefert werden fertige Beispiel-Flows, eigene Bibliotheks-Bausteine (Crossref, OpenAlex, Unpaywall, hbz-Katalog) und Anleitungen auf Deutsch.

![Der Referenz-Checker in Langflow](00_aisc/img/screenshot_app.png)

## Funktionen

- **Visuell statt Code**: Flows werden in Langflow aus Bausteinen zusammengeklickt. Jeder Beispiel-Flow erklärt sich mit einer Notiz direkt auf der Arbeitsfläche.
- **Fünf fertige Beispiel-Flows** als Ausgangspunkt für die Challenges:

  | Flow | Was er tut |
  | --- | --- |
  | `00 Erste Schritte – Hallo KI` | Der kleinste Flow: Frage, Anweisung, Antwort |
  | `01 Referenz-Checker` | Prüft ein Literaturverzeichnis gegen Crossref: Existenz, Jahr, Erstautor:in, DOI, zurückgezogene Artikel |
  | `02 Masterarbeit – Quellen analysieren` | Liest ein PDF, schneidet das Literaturverzeichnis aus, reichert alle Quellen über OpenAlex an und lässt die KI die Quellenbasis bewerten |
  | `03 Literaturreview – Forschungslücken finden` | Forschungsfrage → Suchbegriffe → verlagsübergreifende Suche → freie Volltexte → Themen, Widersprüche, Forschungslücken |
  | `04 Recherche-Agent` | Ein KI-Agent, der selbst entscheidet, ob er Artikel sucht, den Katalog befragt oder Angaben prüft |

- **Bibliotheks-Bausteine** (Kategorie *Bibliothek* in Langflow):

  | Baustein | Quelle |
  | --- | --- |
  | KI-Modell | Cluster (LiteLLM) oder lokal (Ollama), umschaltbar |
  | Literaturangaben prüfen | Crossref (inkl. Retraction Watch), DataCite |
  | Literaturverzeichnis finden | schneidet das Verzeichnis aus langen Dokumenten aus |
  | Quellen anreichern | Crossref + OpenAlex, mit Statistik |
  | Literatursuche | OpenAlex (bei Bedarf mit Crossref als Suchindex) |
  | Volltexte holen | freie PDFs über OpenAlex und Unpaywall |
  | Katalogsuche | hbz-Verbundkatalog über lobid.org |

  Alle Bausteine außer *KI-Modell*, *Literaturverzeichnis finden* und *Volltexte holen* lassen sich auch als Werkzeuge für Agenten nutzen.
- **Cluster oder lokal**: Standardmäßig nutzen die Flows ein Modell über einen LiteLLM-Endpunkt. Wer Daten nicht aus dem Haus geben will (z. B. unveröffentlichte Abschlussarbeiten), schaltet auf ein lokales Modell mit Ollama um.

## Einrichtung und Installation

### Voraussetzungen

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows, macOS) oder Docker mit Docker Compose (Linux)
- Zugangsdaten zum LiteLLM-Endpunkt (von der Orga) **oder** ein lokales Modell über [Ollama](https://ollama.com/)
- Internetzugang (für Crossref, OpenAlex, Unpaywall und lobid)

### Schnellstart

1. Das Repository herunterladen (grüner Knopf *Code → Download ZIP*, dann entpacken) oder klonen:

   ```bash
   git clone https://github.com/aihpi/demo-bibliothekshackaton.git
   cd demo-bibliothekshackaton
   ```

2. Einstellungen anlegen: `.env.example` kopieren, die Kopie `.env` nennen und die Werte der Orga eintragen. Die Startdateien aus Schritt 3 legen `.env` beim ersten Start auch selbst an und öffnen sie.

   ```bash
   cp .env.example .env
   ```

3. Starten: per Doppelklick auf `starten.command` (macOS) bzw. `starten.bat` (Windows), oder:

   ```bash
   docker compose up -d
   ```

   Für ein lokales Modell in Docker zusätzlich `--profile lokal` angeben (lädt beim ersten Start einige GB).

4. Langflow öffnen: <http://localhost:7860>. Die Beispiel-Flows liegen im Projekt *Starter Project*.

## Benutzung

### Anleitungen

Die ausführliche Anleitung liegt in [`anleitungen/`](anleitungen/):

1. [**Anleitung für Teilnehmende**](anleitungen/01_teilnehmende.md): installieren, starten, erster Flow, eigene Flows bauen, häufige Probleme.
2. [**Challenges**](anleitungen/02_challenges.md): die Aufgaben des Hackathons, jeweils in drei Stufen.
3. [**Leitfaden für die Orga**](anleitungen/03_orga.md): Vorbereitung, Zugangsdaten, Ablaufplan, Fehlerbehebung, Wartung.

Beispieldaten liegen in [`daten/`](daten/): eine Literaturliste mit eingebauten Fehlern und eine fiktive Masterarbeit als PDF.

### Empfehlungen

- Einen kostenlosen [OpenAlex-API-Schlüssel](https://openalex.org/settings/api) in `.env` eintragen. Ohne Schlüssel bremst OpenAlex die Suche bei Last, und alle Gruppen im selben WLAN teilen sich das Limit.
- Eine Kontakt-E-Mail (`KONTAKT_EMAIL`) eintragen: Crossref antwortet dann schneller, und Unpaywall findet zusätzliche freie Volltexte.
- Agenten (Flow 04) brauchen Modelle, die Werkzeuge bedienen können. Mit dem Cluster funktioniert das am zuverlässigsten.

## Grenzen

- **Kleine lokale Modelle** (z. B. `qwen3.5:4b`) sind langsam und machen mehr Fehler: Sie erfinden etwa Quellennummern oder ignorieren Teile der Anweisung. Das eignet sich gut, um über die Prüfung von KI-Ergebnissen zu sprechen, ist aber kein Ersatz für ein großes Modell.
- **Abdeckung der Datenbanken**: Crossref und OpenAlex kennen vor allem Zeitschriftenartikel. Bücher, graue Literatur und Webseiten werden oft nicht gefunden. Dafür gibt es die Katalogsuche.
- **Volltexte** gibt es nur für frei zugängliche Publikationen, und nicht jedes PDF lässt sich automatisch lesen.
- **Die Oberfläche von Langflow ist englisch**; die Anleitung übersetzt die wichtigsten Begriffe.

## Für Entwickler:innen

Die Flows in `flows/` werden nicht von Hand gepflegt, sondern von [`scripts/flows_bauen.py`](scripts/flows_bauen.py) über die Langflow-API erzeugt. So passen Code und Felder immer zur installierten Langflow-Version:

```bash
docker compose up -d
uv run --with httpx scripts/flows_bauen.py --testen   # bauen, jeden Flow einmal ausführen, exportieren
```

Die Bausteine liegen in [`komponenten/bibliothek/`](komponenten/bibliothek/). Langflow liest sie beim Start; nach Änderungen `docker compose restart langflow` und die Flows neu bauen. Die Beispiel-Masterarbeit erzeugt `uv run --with reportlab scripts/beispieldaten_erzeugen.py`.

## Quellen

- [Langflow-Dokumentation](https://docs.langflow.org/)
- [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), [OpenAlex API](https://docs.openalex.org/), [Unpaywall API](https://unpaywall.org/products/api), [lobid-resources](https://lobid.org/resources/api)
- [LiteLLM](https://docs.litellm.ai/), [Ollama](https://ollama.com/)

## Autor

- [Mario Tormo Romero](https://github.com/mt0rm0)

## Lizenz

[MIT](LICENSE)

---

## Förderung

<img src="00_aisc/img/logo_bmftr_de.png" alt="drawing" style="width:170px;"/>

Das [KI-Servicezentrum Berlin-Brandenburg](https://hpi.de/kisz) wird vom [Bundesministerium für Forschung, Technologie und Raumfahrt](https://www.bmftr.bund.de/) unter dem Förderkennzeichen 16IS22092 gefördert.
