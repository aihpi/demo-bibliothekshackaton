# L9 Agenten

In L1 bis L8 habt ihr festgelegt, welchen Weg die Daten nehmen: erst dieser Baustein, dann jener. Ein **Agent** arbeitet anders. Er bekommt eine Frage und eine Reihe von **Werkzeugen** und entscheidet selbst, welches Werkzeug er wann benutzt, liest das Ergebnis und entscheidet, was als Nächstes kommt. Dieser Flow gibt einem Agenten nur Standard-Bausteine als Werkzeuge: Websuche, Webseite, Taschenrechner, Datum und einen ganzen anderen Flow.

| | |
| --- | --- |
| **Ihr lernt** | Bausteine in Werkzeuge verwandeln, einem Agenten Anweisungen geben, seine Schritte lesen und prüfen, seine wichtigsten Einstellungen nutzen, einen ganzen Flow als Werkzeug einsetzen. Und: wann ein Agent die falsche Wahl ist. |
| **Bausteine** | Agent, Web Search, URL, Calculator, Current Date, Run Flow, File System, KI-Modell, Chat Input, Chat Output |
| **KI** | ja, ein Modell, das Werkzeuge bedienen kann (Cluster) |
| **Dauer** | etwa 60 Minuten |
| **Testdaten** | keine Dateien; Fragen stehen in den Übungen |

## Inhalt

1. [Der Flow im Überblick](#1-der-flow-im-überblick)
2. [Vorbereiten](#2-vorbereiten)
3. [Schritt für Schritt](#3-schritt-für-schritt)
4. [Übungen](#4-übungen)
5. [Wann nehme ich was?](#5-wann-nehme-ich-was)
6. [Wenn etwas nicht klappt](#6-wenn-etwas-nicht-klappt)
7. [Wie geht es weiter?](#7-wie-geht-es-weiter)

## 1. Der Flow im Überblick

Links stehen fünf Werkzeuge, alle im **Tool Mode**. Jedes ist mit dem Eingang **Tools** des Agenten verbunden:

| Werkzeug | Baustein | Was der Agent damit tun kann | Name, unter dem der Agent es kennt |
| --- | --- | --- | --- |
| Websuche | **Web Search** | im Web, in Nachrichten oder in einem RSS-Feed suchen | `perform_search` |
| Webseite holen | **URL** | den Text einer Webseite lesen | `fetch_content` |
| Taschenrechner | **Calculator** | rechnen | `evaluate_expression` |
| Datum | **Current Date** | Datum und Uhrzeit abfragen | `get_current_date` |
| Referenz-Checker | **Run Flow** | den ganzen Flow *01 Referenz-Checker* ausführen | `01-Referenz-Checker_tool…` |

Dazu kommen das **KI-Modell**, mit dem der Agent denkt (Ausgang *Language Model* an den Eingang *Language Model* des Agenten), der **Chat Input** für eure Frage und ein **Chat Output** für die Antwort.

Der Unterschied zu allen bisherigen Flows: Keine Linie sagt, in welcher Reihenfolge die Werkzeuge laufen. Das entscheidet der Agent bei jeder Frage neu.

## 2. Vorbereiten

1. In der Übersicht beim Flow **L9 Agenten** auf die drei Punkte klicken → *Duplicate*. Arbeitet in der Kopie.
2. Im Baustein **KI-Modell** die **Quelle** auf *Cluster (LiteLLM)* stellen. Agenten brauchen ein Modell, das zuverlässig Werkzeuge aufruft; mehr dazu in [Abschnitt 3.7](#37-welches-modell).
3. Den **Playground** öffnen und fragen:

   *Was ist der neueste Beitrag im RSS-Feed https://bibliotheksportal.de/feed/ und vor wie vielen Tagen ist er erschienen?*

4. Nach etwa 15 Sekunden kommt die Antwort. Über der Antwort steht ein aufklappbarer Bereich mit den **Schritten** des Agenten. Klappt ihn auf.

**Die Schritte lesen.** Jeder Schritt heißt *Executed* und dann den Namen des Werkzeugs, z. B. *Executed perform_search*. Aufgeklappt zeigt er die **Eingabe**, die der Agent dem Werkzeug gegeben hat (z. B. `{"search_mode": "RSS", "query": "https://bibliotheksportal.de/feed/"}`), und die **Ausgabe**, die zurückkam. Das ist die wichtigste Technik in diesem Modul: Nur in den Schritten seht ihr, ob der Agent wirklich nachgeschaut oder etwas behauptet hat.

## 3. Schritt für Schritt

### 3.1 Agent: das Modell mit Werkzeugen

Der *Agent* bekommt die Frage, die Anweisungen und die Beschreibungen aller angeschlossenen Werkzeuge. Daraus entscheidet das Modell: antworten oder erst ein Werkzeug benutzen? Nach jedem Werkzeug liest es das Ergebnis und entscheidet neu, bis es eine Antwort hat.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Language Model** | am Baustein | Das Modell. Hier den Ausgang *Language Model* von **KI-Modell** anschließen. |
| **Agent Instructions** | am Baustein | Rolle, Werkzeuge und Regeln des Agenten. Wirkt wie der Teil eines Prompts, der für das ganze Gespräch gilt. |
| **Tools** | am Baustein | Die Werkzeuge. Beliebig viele Bausteine im Tool Mode lassen sich anschließen. |
| **Input** | am Baustein | Die Frage, meist aus Chat Input |
| **Max Iterations** | *Parameters* | Wie oft der Agent das Modell höchstens aufrufen darf. Standard: 15. Eine Sicherung gegen Agenten, die nicht aufhören. |
| **Current Date**, **Calculator** | *Parameters* | Eingebaute Werkzeuge für Datum und einfache Rechnungen (nur `+`, `-`, `*`, `/`, `**`). Standard: an. In diesem Flow aus, weil die Bausteine links dieselbe Aufgabe sichtbar übernehmen. |
| **Number of Chat History Messages** | *Parameters* | Wie viele frühere Nachrichten des Gesprächs der Agent mitliest. Standard: 100. Bei 0 vergisst er alles Vorherige. |
| **Output Schema** | *Parameters* | Eine feste Struktur mit benannten Feldern für die Antwort. Das Ergebnis kommt am Ausgang **Structured Response** heraus. |
| **Handle Parse Errors** | *Parameters* | Wiederholt einen Werkzeugaufruf, der unterwegs fehlschlägt, bis zu zweimal. Standard: an; so lassen. |

Der Agent hat zwei Ausgänge: **Response** (die Antwort als Message) und **Structured Response** (JSON, nur mit *Output Schema*).

**Die Anweisungen.** Lest sie im Flow einmal ganz. Sie beschreiben jedes Werkzeug in eigenen Worten, sagen, wann es zu nehmen ist, und setzen Regeln: Werkzeuge statt Gedächtnis, Quellen nennen, Deutsch. Ohne Anweisungen nimmt der Agent Langflows englische Standard-Anweisungen; die sind allgemein und kennen eure Aufgabe nicht.

**Das Datum kennt er schon.** In unseren Tests wusste der Agent das heutige Datum auch ohne Werkzeug: Langflow gibt es ihm mit. Das Werkzeug *Current Date* braucht er trotzdem für die Uhrzeit und für eine bestimmte Zeitzone.

### 3.2 Tool Mode: aus einem Baustein wird ein Werkzeug

Jeder Baustein links hat in seiner Leiste (über dem Baustein) den Schalter **Tool Mode** eingeschaltet. Dadurch verschwinden seine normalen Ausgänge, und es gibt nur noch den Ausgang **Toolset**, den ihr mit *Tools* des Agenten verbindet.

Im Tool Mode füllt der **Agent** einige Felder des Bausteins selbst aus, bei jedem Aufruf neu. Welche das sind, seht ihr in den Schritten unter *Eingabe*:

| Baustein | Felder, die der Agent ausfüllt | Felder, die ihr festlegt |
| --- | --- | --- |
| Web Search | *Search Mode*, *Search Query* | *Max Results*, *Language*, *Country* und die übrigen unter *Parameters* |
| URL | *URLs* | *Depth*, *Output Format*, *Headers* (hier mit User-Agent, damit z. B. Wikipedia antwortet) |
| Calculator | *Expression* | |
| Current Date | *Timezone* | |

Was der Agent ausfüllt, überschreibt euren Wert im Baustein. Ein Beispiel aus unseren Tests: Der Baustein *Current Date* stand auf *Europe/Berlin*, der Agent fragte trotzdem nach `UTC`, bis die Anweisungen ausdrücklich „Nimm die Zeitzone Europe/Berlin“ sagten. Wollt ihr ein solches Feld steuern, schreibt es in die Anweisungen.

Die Werkzeuge im Einzelnen kennt ihr aus [L1](L1_daten_importieren.md) (Web Search, URL). **Calculator** rechnet einen Ausdruck wie `18400/1275` aus und gibt ein JSON mit dem Ergebnis zurück. Sprachmodelle rechnen unzuverlässig, darum lohnt sich der Rechner für Zahlen, die stimmen müssen.

### 3.3 Run Flow: ein ganzer Flow als Werkzeug

*Run Flow* führt einen anderen Flow aus demselben Projekt aus. Im Tool Mode wird der ganze Flow zu einem einzigen Werkzeug. Hier ist es *01 Referenz-Checker*: Der Agent schickt eine Literaturangabe hinein und bekommt den Prüfbericht zurück. So kann er die Prüfung über Crossref nutzen, ohne dass ihr den Flow nachbaut.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Flow Name** | am Baustein | Der auszuführende Flow. Die Liste zeigt die Flows im selben Projekt; mit dem Pfeil-Knopf neu laden. |
| **Cache Flow** | *Parameters* | Den Flow zwischenspeichern, statt ihn bei jedem Aufruf neu zu laden |
| **Session ID** | *Parameters* | In welchem Gespräch der Ziel-Flow läuft |

Den Namen und die **Beschreibung** des Werkzeugs nimmt Run Flow vom Ziel-Flow: *Tool designed to execute the flow '01 Referenz-Checker'. Flow details: Prüft ein Literaturverzeichnis …* Daran erkennt der Agent, wofür das Werkzeug gut ist. Wer einen eigenen Flow als Werkzeug anbietet, sollte ihm also eine klare Beschreibung geben. Name und Beschreibung eines Flows ändert ihr in der Übersicht über die drei Punkte beim Flow.

**Achtung beim Weitergeben.** Wählt ihr im Feld *Flow Name* einen Flow aus, merkt sich Run Flow auch dessen interne Nummer. Diese Nummer gibt es nur in eurem Langflow. Exportiert ihr den Flow und importiert ihn anderswo, meldet Run Flow *Flow … not found*: Dann den Ziel-Flow im Feld *Flow Name* einfach neu auswählen. Der mitgelieferte L9-Flow speichert nur den Namen und funktioniert darum auf jedem Langflow, auf dem es *01 Referenz-Checker* gibt.

Ein Aufruf des Referenz-Checkers dauert so lange wie der Flow selbst, oft 30 Sekunden oder mehr.

### 3.4 File System: ein Arbeitsordner für den Agenten

*File System* gibt einem Agenten einen eigenen Ordner, in dem er Textdateien anlegen, lesen, durchsuchen und ändern kann. Der Baustein ist nicht im Flow; ihr setzt ihn in Übung 7 ein.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Workspace Sub-path** | am Baustein | Ein Unterordner im Arbeitsordner. Leer: der ganze Ordner. |
| **Read Only** | *Parameters* | Nur lesen und suchen, nicht schreiben oder ändern |

Im Tool Mode bekommt der Agent davon fünf Werkzeuge: `read_file`, `glob_search` (Dateien auflisten), `grep_search` (in Dateien suchen), `write_file` und `edit_file`. Mit *Read Only* fallen die letzten beiden weg.

Der Ordner liegt im Speicher von Langflow in Docker, **nicht** in eurem Projektordner, und auch nicht dort, wo eure Flows gespeichert sind. Nach einem Neustart des Containers mit `docker compose down` ist er leer. Was bleiben soll, lasst ihr den Agenten in die Antwort schreiben und kopiert es von dort.

### 3.5 Workflow oder Agent?

Die Flows L1 bis L8 sind **Workflows**: Der Weg steht fest, jeder Lauf geht ihn gleich. Ein Agent wählt den Weg selbst. Das hat Vor- und Nachteile:

| | Workflow | Agent |
| --- | --- | --- |
| Weg | festgelegt, für jede Eingabe gleich | wählt der Agent, für jede Frage neu |
| Verschiedene Fragen | braucht Weichen (If-Else, Smart Router aus [L7](L7_verzweigen_und_absichern.md)) | beantwortet viele Arten von Fragen mit denselben Werkzeugen |
| Gleiche Frage zweimal | gleiche Schritte | oft andere Schritte, manchmal ein anderes Ergebnis |
| Tempo und Kosten | ein Modellaufruf pro KI-Baustein | mehrere Modellaufrufe pro Frage |
| Modell | auch kleine lokale Modelle | braucht ein Modell, das Werkzeuge gut bedient |
| Prüfen | Zwischenergebnisse jedes Bausteins | die Schritte des Agenten |

Faustregel: Wenn ihr den Weg aufschreiben könnt, baut einen Workflow. Ein Agent lohnt sich, wenn die Fragen so verschieden sind, dass kein fester Weg passt, wie an einer Auskunftstheke.

### 3.6 Wann der Agent welches Werkzeug nimmt

Der Agent sieht von jedem Werkzeug nur den Namen und eine kurze Beschreibung, dazu eure Anweisungen. Ob er ein Werkzeug nimmt, hängt also davon ab, wie gut Frage, Anweisungen und Beschreibung zusammenpassen. Was wir in Tests beobachtet haben:

- Gleiche Frage, andere Schritte: Mal rechnet der Agent `18400/1275` und dann `14*1275`, mal gleich `18400 - 14*1275`. Das Ergebnis war gleich, der Weg nicht.
- Fehlt ein Werkzeug, behilft er sich: Ohne **Web Search** las er den RSS-Feed mit **URL**.
- Er behauptet manchmal Dinge, die er nicht nachgeschlagen hat, z. B. eine Uhrzeit, zu der er den Feed „abgerufen“ habe, ohne das Datum abzufragen. Die Schritte zeigen das.

### 3.7 Welches Modell?

Agenten verlangen viel vom Modell: Es muss Werkzeuge auswählen, ihre Eingaben im richtigen Format schreiben und die Ergebnisse verstehen, oft mehrmals nacheinander. Das Cluster-Modell kann das gut. Mit dem kleinen lokalen Modell hat in unserem Test eine einfache Frage mit einem Werkzeug geklappt, dauerte aber gut 50 statt 15 Sekunden; bei mehreren Werkzeugen nacheinander scheitern kleine Modelle oft oder tun nur so, als hätten sie ein Werkzeug benutzt (siehe [Anleitung für Teilnehmende](../01_teilnehmende.md#9-wenn-etwas-nicht-klappt)). Probiert es in Übung 1 selbst.

## 4. Übungen

🟢 Ausprobieren · 🟡 Umbauen · 🔴 Selbst bauen. Die Lösungen lassen sich aufklappen. Weil ein Agent bei jedem Lauf neu entscheidet, können eure Schritte von den Lösungen abweichen; entscheidend ist, was ihr in den Schritten seht.

### 🟢 1. Drei Fragen, drei Wege

Stellt im Playground nacheinander diese Fragen und klappt jedes Mal die Schritte auf. Welche Werkzeuge nimmt der Agent, mit welcher Eingabe?

1. *Was ist der neueste Beitrag im RSS-Feed https://bibliotheksportal.de/feed/ und vor wie vielen Tagen ist er erschienen?*
2. *Unser E-Book-Budget beträgt 18.400 Euro. Ein Fachpaket kostet 1.275 Euro. Wie viele Pakete können wir kaufen, und wie viel bleibt übrig?*
3. *Stimmt diese Literaturangabe? Smith, J. (2019). The intelligent library: Thought leaders' views on the likely impact of artificial intelligence on academic libraries. Library Hi Tech, 37(3), 418–435.*

Wer mag: Stellt Frage 1 noch einmal mit der Quelle *Lokal (Ollama)* im KI-Modell.

<details>
<summary>Lösung</summary>

1. *perform_search* im Modus *RSS* mit der Adresse des Feeds, dazu meist *get_current_date*. Die Tage rechnet das Modell oft selbst aus.
2. Ein- oder zweimal *evaluate_expression*, z. B. `18400/1275` (Ergebnis 14,43, also 14 Pakete) und `18400 - 14*1275` (550 Euro Rest).
3. Der Referenz-Checker (*01-Referenz-Checker_tool…*), oft zusätzlich *perform_search*. Ergebnis: Titel, Jahr und Zeitschrift stimmen, der Erstautor heißt Cox, nicht Smith. Das dauert 30 bis 40 Sekunden, weil der ganze Flow 01 läuft.

Lokal dauerte Frage 1 in unserem Test etwa 50 Sekunden statt 15, mit demselben Werkzeug. Bei Frage 3 mit mehreren Werkzeugen nacheinander scheitern kleine Modelle häufiger.

</details>

### 🟢 2. Ein Werkzeug fehlt

Löscht die Verbindung von **Web Search** zum Agenten (Linie anklicken, `Entf`). Stellt dann Frage 1 aus Übung 1 noch einmal. Was macht der Agent, und stimmt alles in seiner Antwort?

<details>
<summary>Lösung</summary>

In unseren Tests las der Agent den Feed stattdessen mit *fetch_content* (Baustein **URL**): Ein RSS-Feed ist auch nur eine Webadresse. Die Antwort war richtig, enthielt aber einmal eine erfundene Angabe, wann der Feed „abgerufen“ worden sei, ohne dass der Agent das Datum abgefragt hatte. Agenten finden oft einen anderen Weg, wenn ein Werkzeug fehlt. Ob alles in der Antwort belegt ist, zeigen nur die Schritte.

Verbindet **Web Search** danach wieder.

</details>

### 🟢 3. Wie viele Schritte darf er?

Stellt im Agenten unter *Parameters* **Max Iterations** auf `1` und stellt Frage 1 aus Übung 1. Dann zurück auf `15`.

<details>
<summary>Lösung</summary>

Die Antwort lautet *Model call limits exceeded: run limit (1/1)*. Der Agent durfte das Modell nur einmal aufrufen. Für diese Frage braucht er aber mindestens zwei Aufrufe: einen, der das Werkzeug anfordert, und einen, der dessen Ergebnis zur Antwort macht. Jede Runde „Werkzeug wählen, Ergebnis lesen“ braucht einen Modellaufruf. *Max Iterations* schützt vor Agenten, die sich im Kreis drehen; 15 reicht für fast alles.

</details>

### 🟢 4. Das Gedächtnis des Agenten

1. Fragt: *Wie viele Tage sind es von heute bis zum 24.12.2026?* (oder ein anderes Datum in der Zukunft) und danach nur: *Und bis zum 31.12.?*
2. Stellt im Agenten unter *Parameters* **Number of Chat History Messages** auf `0`. Startet im Playground links mit **+** ein neues Gespräch und stellt beide Fragen noch einmal.

<details>
<summary>Lösung</summary>

1. Die zweite Frage versteht der Agent, weil er die erste mitliest: Er rechnet die Tage bis Silvester.
2. Mit `0` sieht er nur die aktuelle Nachricht. Auf *Und bis zum 31.12.?* fragte er in unserem Test zurück, was gemeint sei. Für einen Chat mit Rückfragen braucht der Agent den Verlauf; für einzelne, unabhängige Aufträge spart ein kleiner Wert Text und Zeit. Danach wieder auf `100` stellen.

</details>

### 🟡 5. Eingebaute Werkzeuge statt Bausteine

1. Löscht die Bausteine **Calculator** und **Current Date**.
2. Schaltet im Agenten unter *Parameters* die eingebauten Werkzeuge **Current Date** und **Calculator** ein.
3. Fragt: *Wie viele Tage sind es von heute bis zum 24.12.2026?*

Was passiert? Lest dazu noch einmal die Anweisungen des Agenten.

<details>
<summary>Lösung</summary>

In unseren Tests brach der Agent nach etwa 50 Sekunden mit *Recursion limit of 35 reached* ab: Er hat sich im Kreis gedreht. Die Spur führt zu den Anweisungen: *Rechne nie im Kopf, sondern immer mit dem Taschenrechner.* Sie beschreiben die Bausteine, die ihr gerade gelöscht habt, und verlangen den Rechner auch für eine Aufgabe, bei der der eingebaute Rechner (nur `+`, `-`, `*`, `/` und `**`) wenig hilft. Entfernt ihr diesen Satz, antwortete der Agent in unseren Tests nach wenigen Sekunden richtig. Mit den Langflow-Standardanweisungen klappte es ebenfalls.

Die Lehre daraus: **Anweisungen und Werkzeuge müssen zusammenpassen.** Eine Regel, die ein Werkzeug verlangt, das die Aufgabe nicht lösen kann, führt in eine Schleife. Ändert ihr die Werkzeuge, lest die Anweisungen noch einmal.

Und warum schaltet Flow 04 die eingebauten Werkzeuge ab? Er braucht sie nicht, und jedes zusätzliche Werkzeug ist eine Möglichkeit mehr, das falsche zu wählen, besonders für kleine Modelle. Gebt einem Agenten nur die Werkzeuge, die er für seine Aufgabe braucht.

</details>

### 🟡 6. Eine Antwort mit fester Struktur

Der Agent soll den neuesten Beitrag zusätzlich als Datensatz liefern, z. B. um ihn danach in eine Tabelle zu schreiben.

1. Im Agenten unter *Parameters* bei **Output Schema** drei Zeilen anlegen: `titel` (Titel des Beitrags), `datum` (Datum des Beitrags, TT.MM.JJJJ), `link` (Link zum Beitrag), jeweils Typ *str*.
2. Einen zweiten **Chat Output** aufstellen und mit dem Ausgang **Structured Response** des Agenten verbinden.
3. Fragt: *Was ist der neueste Beitrag im RSS-Feed https://bibliotheksportal.de/feed/?*

<details>
<summary>Lösung</summary>

Der erste Chat Output zeigt die Antwort wie gewohnt. Der zweite zeigt ein JSON, z. B.

```json
{"titel": "KULTURLICHTER-Preis – Deutscher Preis für kulturelle Bildung", "datum": "03.11.2026", "link": "https://bibliotheksportal.de/2026/11/03/…"}
```

Das Datum steht im verlangten Format, obwohl der Feed es als `Tue, 03 Nov 2026 15:45:20 +0000` liefert. Ohne Verbindung am Ausgang *Structured Response* bleibt er leer: Langflow erzeugt ihn nur, wenn ein Baustein ihn braucht. Wie Output Schemas funktionieren und wann sie sich lohnen, zeigt [L6](L6_strukturierte_antworten.md) am Baustein *Structured Output*.

</details>

### 🟡 7. Ein Arbeitsordner für den Agenten

1. Zieht einen **File System** (Kategorie *Files & Knowledge*) auf die Arbeitsfläche, schaltet **Tool Mode** ein und verbindet *Toolset* mit *Tools* des Agenten.
2. Fragt: *Lege die Datei leseliste.md an mit dem Inhalt „- Eco, Wie man eine wissenschaftliche Abschlussarbeit schreibt“.*
3. Startet mit **+** ein neues Gespräch und fragt: *Welche Dateien liegen in deinem Arbeitsordner, und was steht in leseliste.md?*
4. Schaltet im File System unter *Parameters* **Read Only** ein und bittet den Agenten, eine Zeile an die Datei anzuhängen.

<details>
<summary>Lösung</summary>

2. Der Agent ruft `write_file` auf und nennt den Pfad `leseliste.md`.
3. Auch im neuen Gespräch, also ohne Erinnerung an die erste Frage, listet er den Ordner auf und liest die Datei: Der Ordner bleibt zwischen den Gesprächen erhalten.
4. Mit *Read Only* hat der Agent kein Werkzeug zum Schreiben mehr und sagt das. So gebt ihr einem Agenten Unterlagen zum Nachschlagen, ohne dass er sie verändern kann.

Bedenkt: Der Ordner liegt im Docker-Container, nicht in eurem Projektordner, und ist nach `docker compose down` leer.

</details>

### 🔴 8. Ein eigener Flow als Werkzeug

Baut einen kleinen Flow, der einen Text in Leichte Sprache übersetzt: **Chat Input** → **Prompt Template** (z. B. `Übersetze diesen Text in Leichte Sprache: {text}`) → **KI-Modell** → **Chat Output**. Gebt ihm den Namen *Leichte Sprache* und eine Beschreibung. Gebt ihn dann dem Agenten mit einem zweiten **Run Flow** als Werkzeug und fragt: *Hole den Text von https://de.wikipedia.org/wiki/Fernleihe und fasse ihn in Leichter Sprache zusammen.*

<details>
<summary>Lösung</summary>

1. Neuer Flow im selben Projekt (*Starter Project*), so gebaut wie beschrieben. In der Übersicht über die drei Punkte beim Flow den Namen *Leichte Sprache* und eine Beschreibung eintragen, z. B. *Übersetzt einen deutschen Text in Leichte Sprache.*
2. Im L9-Flow einen **Run Flow** aufstellen, im Feld *Flow Name* mit dem Pfeil-Knopf die Liste laden und *Leichte Sprache* wählen. **Tool Mode** einschalten, *Toolset* mit *Tools* verbinden.
3. Den Anweisungen des Agenten eine Zeile hinzufügen, z. B. *- Leichte Sprache: übersetzt einen Text in Leichte Sprache.*

In den Schritten sollte erst *fetch_content* mit der Wikipedia-Adresse stehen und dann das neue Werkzeug, dessen Name mit *Leichte-Sprache_tool* beginnt, mit dem Text als Eingabe. Ruft der Agent es nicht auf, sondern übersetzt selbst, schärft die Beschreibung des Flows und die Zeile in den Anweisungen nach. Flows, die ihr einzeln getestet habt, sind so wiederverwendbare Bausteine für Agenten.

</details>

### 🔴 9. Dieselbe Aufgabe als Workflow

Baut die Frage aus Übung 1.1 als festen Workflow ohne Agent: Der neueste Beitrag im Bibliotheksportal und wie viele Tage er her ist. Welche Bausteine braucht ihr? Was ist besser, was schlechter als beim Agenten?

<details>
<summary>Lösung</summary>

**Web Search** (*Search Mode* RSS, *Search Query* `https://bibliotheksportal.de/feed/`, *Max Results* 3) → **Parser** mit dem Template `- {title} ({published}) {link}` → **Prompt Template** mit den Platzhaltern `{beitraege}` und `{heute}` und der Aufgabe „Nenne den neuesten Beitrag mit Link und sage, vor wie vielen Tagen er erschienen ist“ → **KI-Modell** → **Chat Output**. Dazu **Current Date** (Zeitzone Europe/Berlin) an `{heute}`.

Besser: ein einziger Modellaufruf, schnell, jeder Lauf gleich, und es klappt auch mit einem kleinen lokalen Modell. Schlechter: Der Flow kann nur diese eine Frage. Für „Welche Beiträge gab es diese Woche zum Thema Open Access?“ müsstet ihr ihn umbauen, der Agent beantwortet sie mit denselben Werkzeugen. Weil der Flow keinen Chat Input braucht, läuft er im Playground mit jeder Nachricht.

</details>

## 5. Wann nehme ich was?

| Ihr wollt … | Nehmt | Hinweis |
| --- | --- | --- |
| immer dieselbe Aufgabe in denselben Schritten erledigen | einen **Workflow** (L1 bis L8) | schneller, günstiger, wiederholbar |
| verschiedene Arten von Anfragen auf wenige feste Wege verteilen | **Smart Router** oder **If-Else** ([L7](L7_verzweigen_und_absichern.md)) | ein agentischer Workflow: feste Wege, eine KI-Entscheidung |
| offene Fragen beantworten, bei denen der Weg vorher nicht feststeht | einen **Agent** | mit dem Cluster-Modell, Schritte prüfen |
| dem Agenten einen Baustein zur Verfügung stellen | **Tool Mode** am Baustein | Felder, die der Agent füllt, in den Anweisungen steuern |
| dem Agenten einen ganzen, getesteten Ablauf geben | **Run Flow** im Tool Mode | dem Ziel-Flow eine klare Beschreibung geben |
| Datum oder einfache Rechnungen | eingebaute Werkzeuge **Current Date** und **Calculator** oder die gleichnamigen Bausteine | Bausteine zeigen ihre Einstellungen; Anweisungen dazu passend formulieren |
| dass der Agent Notizen ablegt und wiederfindet | **File System** im Tool Mode | liegt im Container; *Read Only* für Nachschlage-Ordner |
| die Antwort als Datensatz weiterverarbeiten | **Output Schema** und **Structured Response** | Ausgang muss verbunden sein |

## 6. Wenn etwas nicht klappt

| Meldung oder Problem | Ursache und Lösung |
| --- | --- |
| Der Agent antwortet, ohne Werkzeuge zu benutzen, oder behauptet, er habe gesucht | Kein Schritt in der Liste über der Antwort. Meist ein kleines lokales Modell: im KI-Modell *Cluster* wählen. Sonst in den Anweisungen deutlicher sagen, wann welches Werkzeug zu nehmen ist. |
| *Model call limits exceeded: run limit* | *Max Iterations* ist zu klein. Auf 15 stellen. |
| *Recursion limit of 35 reached* | Der Agent dreht sich im Kreis, oft weil eine Anweisung ein Werkzeug verlangt, das die Aufgabe nicht lösen kann (siehe Übung 5). Anweisungen und Werkzeuge abgleichen. |
| *Flow … not found* bei Run Flow | Der Ziel-Flow fehlt oder hat auf diesem Langflow eine andere Nummer, z. B. nach einem Import. Im Feld *Flow Name* den Flow neu auswählen. Er muss im selben Projekt liegen. |
| Run Flow hat keinen Ausgang *Toolset* | Erst einen Flow auswählen, dann *Tool Mode* einschalten. |
| *Please respect our robot policy* in einem Schritt mit *fetch_content* | Wikipedia will einen Absender. Im Baustein URL unter *Headers* den User-Agent mit Name und Webadresse eintragen, wie im Flow. |
| *Structured Response* bleibt leer | Kein *Output Schema* angelegt, oder der Ausgang ist mit nichts verbunden. |
| Der Agent antwortet auf Englisch | Die Anweisungen wurden gelöscht oder sagen nichts zur Sprache. „Antworte auf Deutsch.“ ergänzen. |
| Der Agent erinnert sich an alte Antworten | Im Playground links mit **+** ein neues Gespräch starten. |

## 7. Wie geht es weiter?

Ihr kennt jetzt die wichtigsten Standard-Bausteine von Langflow und wisst, wann ein fester Ablauf und wann ein Agent passt. Damit seid ihr bereit für die Aufgaben aus dem Bibliotheksalltag:

- Die [Challenges](../02_challenges.md) bieten drei Aufgaben in drei Stufen und Raum für eigene Ideen. Beginnt mit dem **Bauplan**: zerlegen, zuordnen, wählen, klein bauen, absichern.
- Die Beispiel-Flows im *Starter Project* zeigen fertige Lösungen, die ihr jetzt Baustein für Baustein lesen könnt: **01 Referenz-Checker** und **01b** (derselbe Prüfer mit Bibliotheks-Baustein und aus Standard-Bausteinen), **02 Masterarbeit** (Datei, Anreichern, KI-Analyse), **03 Literaturreview** (zwei KI-Schritte hintereinander), **04 Recherche-Agent** (ein Agent mit den Bibliotheks-Bausteinen als Werkzeugen, der große Bruder von L9) und **05 Schulungsplanung** (KI plant, der Parser baut ohne KI das HTML).
- Zum Nachschlagen: die [Bausteine-Übersicht](../../COMPONENTS.de.md) und die [Übersicht des Lernpfads](README.md).
