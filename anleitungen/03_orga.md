# Leitfaden für die Orga

Dieser Leitfaden ist für alle, die den Hackathon vorbereiten, technisch betreuen oder moderieren.

## Inhalt

1. [Wie alles zusammenhängt](#1-wie-alles-zusammenhängt)
2. [Checkliste Vorbereitung](#2-checkliste-vorbereitung)
3. [Zugänge einrichten](#3-zugänge-einrichten)
4. [Laptops vorbereiten](#4-laptops-vorbereiten)
5. [Probelauf](#5-probelauf)
6. [Ablauf des Tages](#6-ablauf-des-tages)
7. [Fehlerbehebung für Betreuende](#7-fehlerbehebung-für-betreuende)
8. [Nach dem Hackathon](#8-nach-dem-hackathon)
9. [Wartung und Weiterentwicklung](#9-wartung-und-weiterentwicklung)

---

## 1. Wie alles zusammenhängt

```
 Laptop einer Gruppe
 ┌──────────────────────────────────────────────┐
 │  Browser ──► Langflow (Docker, Port 7860)    │
 │               │  Bibliotheks-Bausteine       │
 │               │  Beispiel-Flows              │
 │               ├──► Ollama (optional, lokal)  │
 └───────────────┼──────────────────────────────┘
                 ├──► LiteLLM-Cluster (KI-Modelle)
                 └──► Crossref · OpenAlex · Unpaywall · DataCite · lobid (frei im Internet)
```

- Jede Gruppe betreibt **ihr eigenes Langflow** auf einem Laptop. Es gibt keinen zentralen Server, der ausfallen kann.
- Die KI kommt standardmäßig vom **LiteLLM-Cluster**. Optional läuft ein kleines Modell **lokal** mit Ollama.
- Die Bibliotheks-Bausteine brauchen **Internet**, aber keine Zugangsdaten. Ausnahmen: Ein OpenAlex-Schlüssel wird dringend empfohlen, und eine Kontakt-E-Mail beschleunigt Crossref und schaltet Unpaywall frei.
- Alle Einstellungen stehen in der Datei `.env` im Projektordner.

## 2. Checkliste Vorbereitung

**Zwei bis vier Wochen vorher**

- [ ] Anzahl der Gruppen festlegen (empfohlen: 3–5 Personen pro Gruppe, ein Laptop pro Gruppe als „Bau-Laptop“)
- [ ] LiteLLM: Modell auswählen und für jede Gruppe einen Schlüssel anlegen ([Abschnitt 3](#3-zugänge-einrichten))
- [ ] Klären, ob der Cluster aus dem WLAN des Veranstaltungsorts erreichbar ist (VPN? Firewall?)
- [ ] OpenAlex-API-Schlüssel besorgen (kostenlos)
- [ ] Laptops klären: eigene Geräte der Teilnehmenden oder Leihgeräte? Auf eigenen Dienstgeräten fehlen oft Adminrechte für Docker Desktop.

**Eine Woche vorher**

- [ ] Laptops vorbereiten ([Abschnitt 4](#4-laptops-vorbereiten))
- [ ] Für jede Gruppe eine fertige `.env` erstellen
- [ ] Probelauf aller Flows ([Abschnitt 5](#5-probelauf))
- [ ] Challenges und Anleitung ausdrucken oder als Link bereitstellen

**Am Tag**

- [ ] Alle Laptops starten, Langflow öffnen, einen Flow testen
- [ ] Beamer-Laptop mit Flow 00 und 01 für die Einführung
- [ ] Zettel mit WLAN-Zugang und Link zum Repository

## 3. Zugänge einrichten

### LiteLLM-Cluster

Pro Gruppe einen eigenen **virtuellen Schlüssel** anlegen, am besten mit Budget und Ablaufdatum. Beispiel für die LiteLLM-Admin-API:

```bash
curl -X POST "$LITELLM_URL/key/generate" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key_alias": "hackathon-gruppe-1", "models": ["<modellname>"], "max_budget": 10, "duration": "3d", "rpm_limit": 60}'
```

Beim Modell auf Folgendes achten:

- **Werkzeugaufrufe (Tool Calling)** müssen funktionieren, sonst läuft Flow 04 (Agent) nicht.
- **Kontextlänge ab 32.000 Tokens**: Flow 03 schickt mehrere Volltexte auf einmal.
- Gute **Deutschkenntnisse**.

Testen, ob Schlüssel und Modell funktionieren:

```bash
curl "$CLUSTER_BASE_URL/models" -H "Authorization: Bearer $CLUSTER_API_KEY"
curl "$CLUSTER_BASE_URL/chat/completions" -H "Authorization: Bearer $CLUSTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "<modellname>", "messages": [{"role": "user", "content": "Sag Hallo auf Deutsch."}]}'
```

`CLUSTER_BASE_URL` endet in der Regel auf `/v1`.

### OpenAlex

OpenAlex bremst Suchanfragen ohne Schlüssel bei hoher Last oder sperrt sie ganz. Alle Laptops im selben WLAN teilen sich eine IP-Adresse und damit das Limit. Ein kostenloser Schlüssel unter <https://openalex.org/settings/api> behebt das. Ein Schlüssel für alle Gruppen reicht meist. Ohne Schlüssel sucht der Baustein *Literatursuche* ersatzweise über Crossref, mit schlechteren Treffern.

### Kontakt-E-Mail

Crossref und Unpaywall bitten um eine Kontaktadresse (`KONTAKT_EMAIL`). Mit Adresse erlaubt Crossref drei parallele Anfragen statt einer, und der Baustein *Volltexte holen* nutzt zusätzlich Unpaywall. Am besten eine Funktionsadresse der Einrichtung nehmen.

### Die `.env` einer Gruppe

```ini
KI_STANDARD=cluster
CLUSTER_BASE_URL=https://litellm.example.org/v1
CLUSTER_API_KEY=sk-gruppe-1-…
CLUSTER_MODELL=<modellname>
LOKAL_BASE_URL=http://host.docker.internal:11434/v1
LOKAL_MODELL=qwen3.5:4b
LOKAL_KONTEXT=16384
KONTAKT_EMAIL=hackathon@bibliothek.example.org
OPENALEX_API_KEY=…
```

## 4. Laptops vorbereiten

**Mindestens:** 8 GB RAM, 10 GB freier Speicher, Docker Desktop, Adminrechte für die Installation. **Für lokale Modelle:** 16 GB RAM; am besten ein Mac mit Apple-Chip oder ein Laptop mit NVIDIA-Grafikkarte.

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) installieren. Unter Windows muss dabei WSL 2 aktiviert werden (der Installer fragt danach).
2. Das Repository herunterladen und entpacken.
3. Die `.env` der Gruppe in den Ordner legen.
4. Einmal `starten.command` bzw. `starten.bat` ausführen. Dabei wird Langflow heruntergeladen (knapp 1 GB).

**WLAN schonen:** Wenn viele Laptops gleichzeitig laden, das Image vorab auf einen USB-Stick legen:

```bash
docker pull langflowai/langflow:1.12.3
docker save langflowai/langflow:1.12.3 -o langflow-1.12.3.tar
# auf jedem Laptop:
docker load -i langflow-1.12.3.tar
```

### Lokale Modelle (optional)

Drei Wege, vom einfachsten zum aufwendigsten:

| Weg | Wann | Einstellung in `.env` |
|---|---|---|
| **Ollama-App** auf dem Laptop installieren, dann `ollama pull qwen3.5:4b` | macOS (nutzt die Grafikeinheit), Windows mit NVIDIA-Grafikkarte | `LOKAL_BASE_URL=http://host.docker.internal:11434/v1` |
| **Ollama in Docker:** `docker compose --profile lokal up -d` | Linux, oder wenn nichts installiert werden soll | `LOKAL_BASE_URL=http://ollama:11434/v1` |
| **Ollama auf einem Rechner im Raum** für alle | wenige starke Rechner, viele schwache Laptops | `LOKAL_BASE_URL=http://<ip-adresse>:11434/v1` (Ollama mit `OLLAMA_HOST=0.0.0.0` starten) |

Modellempfehlungen: `qwen3.5:4b` (3,4 GB, läuft fast überall), `qwen3.5:9b` (6,6 GB, deutlich besser, braucht 16 GB RAM). Der Baustein *KI-Modell* setzt die Kontextlänge selbst (`LOKAL_KONTEXT`), damit Ollama lange Texte nicht still abschneidet.

## 5. Probelauf

**Von Hand (auf jedem Laptop):** Langflow öffnen, Flow `00` im Playground mit einer Frage testen. Das prüft Cluster-Zugang und Modell.

**Automatisch (auf einem Laptop):** Das Skript baut alle Flows neu, führt jeden einmal mit den Testdaten aus und zeigt die Antworten:

```bash
uv run --with httpx scripts/flows_bauen.py --testen
```

Erwartete Laufzeiten: mit dem Cluster je Flow 10–60 Sekunden; mit `qwen3.5:4b` auf einer Laptop-Grafikkarte ca. 5 s (Flow 00), 40 s (01), 50 s (02), 2 min (03), 10 s (04). Ohne Grafikkarte ein Vielfaches davon.

Beim Probelauf auf Folgendes achten:

- Flow 01 findet in der Testliste: 4 × bestätigt, 3 × Abweichung, 2 × nicht gefunden, 1 × zurückgezogen.
- Flow 02 findet 17 von 17 Quellen.
- Flow 04 benutzt Werkzeuge. Antwortet der Agent, ohne zu suchen, beherrscht das Modell keine Werkzeugaufrufe.

## 6. Ablauf des Tages

Ein Vorschlag für einen Tag:

| Zeit | Programmpunkt |
|---|---|
| 09:30 | Ankommen, Laptops starten, Gruppen finden |
| 10:00 | Begrüßung, Ziele, Challenges vorstellen (15 min) |
| 10:15 | **Live-Einführung in Langflow** am Beamer: Flow 00 ausführen, Prompt ändern, Flow 01 mit Testdaten zeigen, Zwischenergebnisse ansehen (30 min) |
| 10:45 | Gruppen wählen eine Challenge, erste Schritte 🟢 |
| 12:30 | Mittagspause |
| 13:15 | Weiterarbeit 🟡 🔴, Betreuende gehen herum |
| 14:30 | Kurzer Zwischenstand: Jede Gruppe sagt in einem Satz, woran sie arbeitet |
| 15:30 | Präsentationen (5 min pro Gruppe + Fragen) |
| 16:30 | Diskussion: Was davon würden wir im Alltag nutzen? Was nicht, und warum? |
| 17:00 | Abschluss |

**Betreuung:** eine technisch versierte Person pro drei bis vier Gruppen. Hilfreich ist eine Person aus der Bibliothekspraxis, die fachliche Fragen beantwortet.

**Einführung live zeigen, nicht erklären.** Am wirkungsvollsten ist der Referenz-Checker: erst eine erfundene Angabe von einem Chatbot erzeugen lassen, dann zeigen, wie der Flow sie findet.

## 7. Fehlerbehebung für Betreuende

Die häufigsten Probleme der Teilnehmenden stehen in der [Anleitung für Teilnehmende](01_teilnehmende.md#9-wenn-etwas-nicht-klappt). Darüber hinaus:

| Problem | Lösung |
|---|---|
| Port 7860 ist belegt | In `docker-compose.yml` die Zeile `"7860:7860"` z. B. in `"7861:7860"` ändern und <http://localhost:7861> öffnen. |
| Docker Desktop startet unter Windows nicht | WSL 2 fehlt: `wsl --install` in einer Administrator-Eingabeaufforderung, Neustart. Virtualisierung im BIOS prüfen. |
| Firmen-Proxy blockiert den Download | Image per USB-Stick laden ([Abschnitt 4](#4-laptops-vorbereiten)). |
| Protokoll ansehen | `docker compose logs -f langflow` im Projektordner |
| Bausteine fehlen in der Leiste | `docker compose restart langflow`; im Protokoll nach Fehlern zu `komponenten` suchen. |
| Ein Beispiel-Flow wurde „kaputtgebaut“ | In Langflow über *Upload* die Datei aus `flows/` neu importieren. |
| Alles zurücksetzen | `docker compose down -v` und neu starten. **Achtung: löscht alle eigenen Flows.** Vorher exportieren. |
| Cluster antwortet nicht | Die `curl`-Tests aus [Abschnitt 3](#3-zugänge-einrichten) auf dem Laptop ausführen. Zur Not im *KI-Modell* auf *Lokal* umschalten. |
| Lokales Modell sehr langsam | `docker compose --profile lokal` nutzt unter macOS keine Grafikeinheit. Stattdessen die Ollama-App installieren. |

## 8. Nach dem Hackathon

- Die Flows der Gruppen einsammeln: in Langflow beim Flow auf die drei Punkte → *Export*. Die JSON-Dateien lassen sich später wieder importieren.
- LiteLLM-Schlüssel der Gruppen deaktivieren.
- Rückmeldungen sammeln: Welche Challenge hat funktioniert, welche war zu schwer?
- Wer weitermachen will: Die JSON-Dateien laufen in jedem Langflow 1.12, solange der Ordner `komponenten/` mitkommt.

## 9. Wartung und Weiterentwicklung

**Aufbau des Repositorys**

| Pfad | Inhalt |
|---|---|
| `docker-compose.yml` | Langflow (und optional Ollama) |
| `.env.example` | Vorlage für die Einstellungen |
| `komponenten/bibliothek/` | die Bibliotheks-Bausteine (Python), eine Datei pro Baustein |
| `flows/` | die Beispiel-Flows (JSON), werden beim Start automatisch geladen |
| `daten/` | Testdaten für die Challenges |
| `scripts/flows_bauen.py` | erzeugt `flows/` über die Langflow-API und testet die Flows |
| `scripts/beispieldaten_erzeugen.py` | erzeugt die Beispiel-Masterarbeit |
| `anleitungen/` | diese Anleitungen |

**Einen Baustein ändern:** Datei in `komponenten/bibliothek/` bearbeiten, `docker compose restart langflow`, dann `uv run --with httpx scripts/flows_bauen.py --testen`. Die Flows enthalten den Code der Bausteine; darum nach jeder Änderung die Flows neu bauen.

**Einen Flow ändern:** in `scripts/flows_bauen.py` (nicht in den JSON-Dateien), dann neu bauen. So bleiben Flows reproduzierbar.

**Langflow aktualisieren:** In `docker-compose.yml` die Version ändern, neu starten, Flows neu bauen und testen und die Flows einmal im Browser öffnen: Meldet Langflow „Some connections were removed“, passen Namen von Ein- oder Ausgängen nicht mehr.

**Hinweise für Bausteine:** Jede Datei muss für sich allein lauffähig sein, denn Langflow speichert den Code jedes Bausteins im Flow. Hilfsfunktionen dürfen deshalb nicht aus anderen Dateien importiert werden. Ausgänge mit `group_outputs=True` erscheinen im Editor gleichzeitig. Ausgänge mit `tool_mode=False` werden nicht zu Agenten-Werkzeugen. Die Methodennamen der Ausgänge sind die Werkzeugnamen, die der Agent sieht.
