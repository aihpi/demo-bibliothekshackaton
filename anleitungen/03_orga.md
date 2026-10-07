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

Können die Teilnehmenden kein Docker installieren, gibt es eine Alternative: eine gemeinsame Instanz im Cluster, in der jede Gruppe ein eigenes Konto hat. Siehe [Gehostete Instanz](../HOSTING.de.md).

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
- [ ] Die Aufträge 2a bis 3b aus den Folien einmal selbst durchbauen ([Abschnitt 5](#5-probelauf))
- [ ] Challenges und Anleitung ausdrucken oder als Link bereitstellen

**Am Tag**

- [ ] Alle Laptops starten, Langflow öffnen, einen Flow testen
- [ ] Beamer-Laptop mit den Folien (`dokumente/Hackathon-Praesentation_DE.pptx`) und Langflow für die Live-Teile
- [ ] Zettel mit WLAN-Zugang und Link zum Repository

## 3. Zugänge einrichten

### LiteLLM-Cluster

Pro Gruppe einen eigenen **virtuellen Schlüssel** anlegen, am besten mit Budget und Ablaufdatum. Die Schlüssel sollten **zehn Tage über den Hackathon hinaus** gültig bleiben, damit die Teilnehmenden zu Hause weiterbauen können. Beispiel für die LiteLLM-Admin-API:

```bash
curl -X POST "$LITELLM_URL/key/generate" \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"key_alias": "hackathon-gruppe-1", "models": ["<modellname>"], "max_budget": 10, "duration": "10d", "rpm_limit": 60}'
```

`duration` zählt ab dem Anlegen. Wer die Schlüssel schon vor dem Hackathon anlegt, rechnet die Tage bis dahin dazu (z. B. `"13d"` bei drei Tagen Vorlauf) und nennt den Teilnehmenden das genaue Ablaufdatum.

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

Crossref und Unpaywall bitten um eine Kontaktadresse (`KONTAKT_EMAIL`). Mit Adresse erlaubt Crossref drei parallele Anfragen statt einer, und der Baustein *Volltexte holen* nutzt zusätzlich Unpaywall. Am besten eine Funktionsadresse der Einrichtung nehmen. Die Gruppen können auch selbst eine Adresse eintragen, als globale Variable `KONTAKT_EMAIL` in Langflow (siehe [Bausteine](../COMPONENTS.de.md#39-bibliothek)); sie gilt dann statt der aus der `.env`.

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
- Die Aufträge 2a bis 3b aus den Folien gibt es nicht als fertige Flows. Einmal selbst durchbauen, besonders diese Schritte: das KI-Modell an den Eingang *Language Model* von *Agent* und *Smart Router* anschließen, Tool Mode bei *Literatursuche* und *Katalogsuche*, die *Route Message* der Route Sonstiges. Flow 04 zeigt, wie der Agent verbunden wird.

## 6. Ablauf des Tages

Der Tag folgt dem Prinzip *erst verstehen, dann bauen, dann anwenden*. Am Vormittag führen drei Lernblöcke Schritt für Schritt von einfachen LLM-Workflows über Agenten zu agentischen Workflows. Jeder Block beginnt mit kurzer Theorie und endet mit Aufträgen, die die Gruppen in Langflow bauen. Erst am Nachmittag arbeiten die Gruppen an den Use Cases (Challenges). Ziel ist, dass alle nach Hause gehen und allein weiterarbeiten können, nicht dass am Ende fertige Lösungen stehen.

Die Folien dazu liegen in `dokumente/Hackathon-Praesentation_DE.pptx`. Die Theorie, die Aufträge und Hinweise für die Moderation stehen in den Notizen der Folien.

| Zeit | Programmpunkt |
|---|---|
| 10:00 | Ankommen, letzte Installationen abschließen. Wer fertig ist, öffnet Langflow und probiert Flow 00 aus |
| 10:20 | Begrüßung, zwei Ziele, Lernpfad, Thesen zum Abstimmen |
| 10:30 | **Teil 1: LLM-Workflows.** Theorie (Sprachmodell, Prompt, Einstellungen, Modell und Backend, Grenzen), dann Aufträge 1a bis 1c: Flow 00 anpassen, einen eigenen Flow bauen, ihn um eine Literatursuche erweitern |
| 11:25 | **Teil 2: Agenten.** Theorie (Workflow oder Agent, Werkzeuge, Agentenschleife, Grenzen), dann Aufträge 2a und 2b: ein eigener Agent mit einem und mit zwei Werkzeugen |
| 12:10 | Mittagspause |
| 12:50 | **Teil 3: Agentische Workflows.** Theorie (Spektrum, vier Muster, Mensch in der Schleife, Bauplan), dann Aufträge 3a und 3b: die Auskunfts-Weiche mit dem Smart Router |
| 13:35 | **Teil 4: Use Cases.** Gruppen wählen eine Challenge oder eine eigene Idee, machen zuerst den Bauplan auf Papier und bauen dann |
| 15:15 | Show & Tell: 3 Minuten pro Gruppe |
| 15:40 | Rückblick auf die Thesen, „So macht ihr zu Hause weiter“, Feedback |
| 16:00 | Ende |

Der Zeitplan ist knapp. Wenn es eng wird, lassen sich Auftrag 1c und der Bonus in 3b kürzen; die Aufträge 2a, 2b und 3a sollten bleiben, weil sie aufeinander aufbauen.

**Betreuung:** eine technisch versierte Person pro drei bis vier Gruppen. Die fachliche Expertise bringen die Teilnehmenden selbst mit; die Betreuung hilft vor allem bei Langflow, den Modellen und der Technik. In der Use-Case-Phase beim Herumgehen nach dem Bauplan fragen, bevor es um einzelne Bausteine geht.

**Live zeigen, nicht erklären.** Vor jedem Auftrag kurz am Beamer vormachen, wo die Bausteine liegen und wie man verbindet. In Teil 2 lohnt es sich, im Playground die aufgeklappten Schritte des Agenten zu zeigen.

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
- Die LiteLLM-Schlüssel laufen nach zehn Tagen von selbst ab, wenn sie mit `duration` angelegt wurden ([Abschnitt 3](#3-zugänge-einrichten)). Den Teilnehmenden das Ablaufdatum nennen.
- Rückmeldungen sammeln: Welche Aufträge und Challenges haben funktioniert, welche waren zu schwer? Die offenen Fragen aus dem Feedback am Ende, wenn möglich, nachliefern.
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
| `dokumente/` | Installationsanleitung, Bausteine-Übersicht und die Folien für den Tag |

**Einen Baustein ändern:** Datei in `komponenten/bibliothek/` bearbeiten, `docker compose restart langflow`, dann `uv run --with httpx scripts/flows_bauen.py --testen`. Die Flows enthalten den Code der Bausteine; darum nach jeder Änderung die Flows neu bauen.

**Einen Flow ändern:** in `scripts/flows_bauen.py` (nicht in den JSON-Dateien), dann neu bauen. So bleiben Flows reproduzierbar.

**Langflow aktualisieren:** In `docker-compose.yml` die Version ändern, neu starten, Flows neu bauen und testen und die Flows einmal im Browser öffnen: Meldet Langflow „Some connections were removed“, passen Namen von Ein- oder Ausgängen nicht mehr.

**Hinweise für Bausteine:** Jede Datei muss für sich allein lauffähig sein, denn Langflow speichert den Code jedes Bausteins im Flow. Hilfsfunktionen dürfen deshalb nicht aus anderen Dateien importiert werden. Ausgänge mit `group_outputs=True` erscheinen im Editor gleichzeitig. Ausgänge mit `tool_mode=False` werden nicht zu Agenten-Werkzeugen. Die Methodennamen der Ausgänge sind die Werkzeugnamen, die der Agent sieht.
