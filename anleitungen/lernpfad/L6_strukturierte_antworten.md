# L6 Strukturierte Antworten

Ein Sprachmodell antwortet mit Text. Für fast alles, was danach kommt, braucht ihr aber **Daten**: eine Tabelle zum Filtern, Felder für den Katalog, eine Spalte für Excel. Dieser Flow macht aus freiem Text und aus einer Tabelle mit KI strukturierte Daten, auf vier Wegen nebeneinander. Er beantwortet die Frage, die beim Bauen eigener Flows am häufigsten aufkommt: Reicht es, im Prompt um JSON oder CSV zu bitten, oder brauche ich *Structured Output*?

| | |
| --- | --- |
| **Ihr lernt** | Ein Modell im Prompt um CSV oder JSON bitten und die Antwort in eine Tabelle umwandeln, Felder mit *Structured Output* festlegen, das Modell mit *Batch Run* jede Zeile einer Tabelle bearbeiten lassen, Daten mit *Smart Transform* nach einer Anweisung in eigenen Worten umformen. Und: welcher Weg wann der richtige ist. |
| **Bausteine** | Prompt Template, KI-Modell, Type Convert, Structured Output, Batch Run, Smart Transform, Read File, Chat Output |
| **KI** | ja; für B, C und D am besten das Cluster |
| **Dauer** | etwa 60 Minuten |
| **Testdaten** | `daten/lernpfad/anschaffungsvorschlaege.txt`, `daten/lernpfad/neuerwerbungen.csv`, `daten/lernpfad/benutzungsordnung.txt` |

Ihr solltet [L1](L1_daten_importieren.md) kennen (Read File, die Typen Message, JSON und Table). [L5](L5_prompts_und_modelle.md) erklärt Prompt Template und KI-Modell ausführlich; hier reicht es zu wissen, dass das Prompt Template den Text für das Modell zusammensetzt.

## Inhalt

1. [Der Flow im Überblick](#1-der-flow-im-überblick)
2. [Vorbereiten](#2-vorbereiten)
3. [Schritt für Schritt](#3-schritt-für-schritt)
4. [Übungen](#4-übungen)
5. [Wann nehme ich was?](#5-wann-nehme-ich-was)
6. [Wenn etwas nicht klappt](#6-wenn-etwas-nicht-klappt)

## 1. Der Flow im Überblick

Die Erwerbung bekommt Anschaffungsvorschläge per E-Mail, jede anders geschrieben: mal mit ISBN, mal mit „ist letztes Jahr erschienen“, einmal zwei Bücher in einer Mail. Daraus soll eine Tabelle werden. Außerdem gibt es eine Liste der Neuerwerbungen, die das Modell ergänzen und umformen soll.

| Weg | Eingabe | Bausteine | Was herauskommt |
| --- | --- | --- | --- |
| **A** | die E-Mails | **Prompt Template** verlangt CSV → **KI-Modell** → **Type Convert** | die Antwort des Modells als Text und als Tabelle |
| **B** | die E-Mails | **Structured Output** mit festen Feldern | eine Tabelle mit genau diesen Feldern |
| **C** | die Liste | **Batch Run**: ein Aufruf des Modells pro Zeile | die Liste mit einer neuen Spalte *fachgruppe* |
| **D** | die Liste | **Smart Transform**: eine Anweisung in eigenen Worten | eine gefilterte, sortierte Liste |

Der Baustein **KI-Modell (für B, C, D)** liefert über seinen Ausgang *Language Model* das Modell an die drei Bausteine, die eines brauchen. Weg A hat ein eigenes KI-Modell, weil dort dessen Antworttext gebraucht wird.

Die Wege A und B lesen dieselben E-Mails. Vergleicht ihre Tabellen: Das ist der Kern dieses Moduls.

## 2. Vorbereiten

1. In der Übersicht beim Flow **L6 Strukturierte Antworten** auf die drei Punkte → *Duplicate*. Arbeitet in der Kopie.
2. Im Baustein **E-Mails (Read File)** `daten/lernpfad/anschaffungsvorschlaege.txt` hochladen, im Baustein **Liste (Read File)** `daten/lernpfad/neuerwerbungen.csv`.
3. In **beiden** KI-Modellen die **Quelle** auf *Cluster (LiteLLM)* stellen. Mit einem lokalen Modell funktionieren A und D, B wird unzuverlässig und C dauert sehr lange (siehe Übung 2).
4. **Playground** öffnen, irgendetwas abschicken. Nach ein bis drei Minuten erscheinen fünf Nachrichten: die Antwort des Modells aus A und die Tabellen von A bis D.

Der Flow hat keinen Chat Input, darum laufen alle Wege. Einzelne Wege startet ihr mit **▶** an ihrem Chat Output, z. B. an *B: Tabelle*. Das spart Zeit, wenn ihr nur an einem Weg arbeitet.

## 3. Schritt für Schritt

### 3.1 Weg A: Prompt verlangt CSV, Type Convert macht eine Tabelle

Der einfachste Weg: Ihr schreibt in den Prompt, in welcher Form das Modell antworten soll. Der Prompt im Flow verlangt eine CSV-Tabelle mit fester Kopfzeile:

```text
Antworte nur mit einer CSV-Tabelle, ohne Erklärung und ohne ```. …
Die erste Zeile ist genau diese Kopfzeile:
autor,titel,jahr,verlag,isbn,wer
```

Das Modell schreibt dann Text, der wie eine Tabelle aussieht. Für Langflow ist es aber immer noch eine **Message**. Erst **Type Convert** macht daraus eine echte **Table**.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Kreativität (Temperatur)** | KI-Modell, am Baustein | Steht auf *0*. Je niedriger, desto eher hält sich das Modell an das Format und antwortet beim nächsten Lauf gleich. |
| **Output Type** | Type Convert, am Baustein | *Table*: Der Baustein hat dann den Ausgang *Table Output*. |
| **Auto Parse** | Type Convert, *Parameters* | Erkennt CSV oder JSON im Text und macht Spalten daraus. Ohne Auto Parse wird jede Zeile des Texts eine Zeile in einer einzigen Spalte `text`. |

**Was Auto Parse versteht und was nicht** (ausprobiert mit Text, der direkt in Type Convert ging):

| Antwort des Modells | Ergebnis von Type Convert |
| --- | --- |
| reine CSV mit Kopfzeile | richtige Tabelle |
| ein JSON-Array, z. B. `[{"autor": "Albers", "jahr": 2025}, …]` | richtige Tabelle |
| ein JSON-Objekt mit einer Liste darin, z. B. `{"buecher": [ … ]}` | richtige Tabelle aus der Liste |
| CSV oder JSON in ```` ``` ```` (Code-Block) | **eine** Spalte `text`, jede Zeile einzeln |
| ein Satz davor, z. B. „Hier ist die Tabelle:“ | **eine** Spalte `text` |
| CSV ohne Kopfzeile | die erste Datenzeile wird zur Kopfzeile |

Darum steht im Prompt „ohne Erklärung und ohne ```“ und die Kopfzeile wörtlich. Große Modelle halten sich meist daran, kleine nicht immer.

**Ein Stolperstein mit JSON:** Wollt ihr im Prompt ein JSON-Beispiel zeigen, z. B. `{"autor": "…"}`, macht *Prompt Template* aus jedem Teil in geschweiften Klammern einen Platzhalter mit eigenem Eingang. Beschreibt das gewünschte JSON darum in Worten (Übung 5).

### 3.2 Weg B: Structured Output

*Structured Output* bekommt den Text und eine Liste von Feldern, das **Output Schema**. Der Baustein schickt dem Modell die Felder nicht als Bitte im Prompt, sondern als feste Vorgabe: Das Modell muss eine Funktion mit genau diesen Feldern „aufrufen“ (ein *Werkzeugaufruf*, wie bei Agenten). Was zurückkommt, hat darum immer die richtigen Spalten, auch wenn der Inhalt falsch sein kann.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Language Model** | am Baustein | Hier ist der Ausgang *Language Model* von **KI-Modell** angeschlossen. |
| **Input Message** | am Baustein | Der Text, aus dem herausgezogen wird; hier die E-Mails |
| **Output Schema** | am Baustein, öffnet sich als Tabelle | Die Felder, eines pro Zeile: **Name** (wird zum Spaltennamen), **Description** (was in das Feld gehört; das liest das Modell), **Type** (*str* Text, *int* ganze Zahl, *float* Zahl mit Komma, *bool* ja/nein, *dict* verschachtelte Angaben) und **As List** (mehrere Werte pro Feld, z. B. mehrere Autor:innen) |
| **Schema Name** | *Parameters* | Der Name dessen, was herausgezogen wird, hier *Anschaffungsvorschlag*. Das Modell sieht ihn als Namen der Funktion. Ein guter Name hilft spürbar (Übung 9). |
| **Format Instructions** | *Parameters* | Die Anweisung an das Modell, auf Englisch voreingestellt: alle passenden Einträge herausziehen, fehlende Werte mit *null* füllen, Doppelte entfernen. Ihr könnt einen Satz auf Deutsch davorsetzen, z. B. was genau gesucht ist. |

Der Baustein hat zwei Ausgänge mit dem Namen *Structured Output*: einen als **JSON** und einen als **Table**. Fahrt mit der Maus darüber, um den Typ zu sehen. Findet das Modell mehrere Einträge (hier fünf Bücher), stehen sie im JSON unter `results`, in der Tabelle als fünf Zeilen.

**Was wir beobachtet haben** (Cluster, Kreativität 0): Beide Wege A und B finden alle fünf Bücher, auch die zwei in der Mail von Prof. Brandt. Unterschiede gibt es im Detail. A schreibt bei *wer* nur den Namen, B schrieb in einem Lauf Name, E-Mail-Adresse, Betreff und „2 Exemplare“ hinein, weil die Beschreibung des Felds nicht sagte, was nicht hineingehört. Fehlende Werte heißen bei A *nan* (leer), bei B *null*. Und beim Buch von Okan Demir („ist letztes Jahr rausgekommen“) ließ A das Jahr leer, B setzte *2023* ein: Das Modell weiß nicht, welches Jahr heute ist, und rät.

### 3.3 Weg C: Batch Run

*Batch Run* nimmt eine **Tabelle** und fragt das Modell **für jede Zeile einmal**, mit derselben Anweisung. Die Antworten kommen als neue Spalte an die Tabelle. Hier ordnet das Modell jedes Buch der Liste einer Fachgruppe zu.

Die Liste kommt als CSV-Text aus *Read File*; ein **Type Convert** mit *Auto Parse* macht daraus erst eine Tabelle, wie in Weg A.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Instructions** | am Baustein | Die Anweisung, die für jede Zeile gilt. Hier: „Ordne das Buch genau einer dieser Fachgruppen zu: … Antworte nur mit dem Namen der Fachgruppe.“ |
| **Table** | am Baustein | Die Tabelle |
| **Column Name** | am Baustein | Welche Spalte das Modell zu sehen bekommt, hier `titel`. **Leer**: alle Spalten der Zeile, als Liste „spalte = wert“. Die Ergebnistabelle enthält immer alle Spalten. |
| **Output Column Name** | *Parameters* | Name der neuen Spalte. Standard `model_response`, hier `fachgruppe`. |
| **Enable Metadata** | *Parameters* | Fügt eine Spalte `metadata` an, z. B. ob der Aufruf geklappt hat und wie lang die Antwort war |

Außerdem hängt Batch Run immer eine Spalte `batch_index` an, die Nummer der Zeile ab 0.

**Gut zu wissen:** Jede Zeile ist ein eigener Aufruf des Modells, und Batch Run schickt alle auf einmal ab. Beim Cluster ist das schnell. Ein lokales Modell auf dem Laptop bekommt so 15 Anfragen gleichzeitig; in unserem Test war es nach 10 Minuten nicht fertig und brach ab.

### 3.4 Weg D: Smart Transform

*Smart Transform* formt Daten nach einer Anweisung in normaler Sprache um. Anders als bei den anderen Wegen bearbeitet das Modell die Daten nicht selbst: Es sieht die Daten (bei großen Daten nur Anfang und Ende), **schreibt ein kleines Python-Programm** und Langflow führt dieses Programm auf allen Daten aus. Das Ergebnis ist darum genau und schnell, aber nur so gut wie das Programm.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **JSON** | am Baustein | Die Daten: JSON, Table oder Message. Hier die Tabelle der Liste. |
| **Instructions** | am Baustein | Was geschehen soll. Hier: nur verfügbare Bücher ab 2022, nur Titel, Jahr und Preis, nach Preis sortiert. |
| **Max Size** | *Parameters* | Ab wie vielen Zeichen die Daten als groß gelten. Standard 30000. |
| **Sample Size** | *Parameters* | Wie viele Zeichen von Anfang und Ende das Modell bei großen Daten sieht. Standard 1000. |

Der Baustein hat drei Ausgänge mit dem Namen *Output*: **JSON**, **Table** und **Message**. Der Flow nutzt *Table*.

Langflow lässt das Programm nur in einem engen Rahmen laufen, ohne zusätzliche Programm-Bibliotheken. Filtern, Sortieren, Spalten auswählen und einfache Rechnungen funktionieren. Zählen und Gruppieren nicht: Das Modell greift dafür zu einer Bibliothek, und der Baustein meldet *name '\_\_import\_\_' is not defined* (Übung 8).

### 3.5 Und der Agent?

Auch der Baustein **Agent** hat in den *Parameters* ein **Output Schema**, das genauso funktioniert wie bei Structured Output. Der Agent liefert seine Antwort dann zusätzlich am Ausgang *Structured Response* als JSON. Das lohnt sich, wenn der Agent erst mit Werkzeugen recherchieren und das Ergebnis dann in festen Feldern abliefern soll. Mehr dazu in [L9](L9_agenten.md).

## 4. Übungen

🟢 Ausprobieren · 🟡 Umbauen · 🔴 Selbst bauen. Die Lösungen lassen sich aufklappen. Sprachmodelle antworten nicht jedes Mal gleich; eure Ergebnisse können von den beschriebenen abweichen.

### 🟢 1. Vier Wege vergleichen

Führt den Flow einmal aus und legt die Tabellen von A und B nebeneinander. Achtet auf:

- die Spalte *wer*
- das Jahr beim Buch von Okan Demir
- wie fehlende Werte aussehen

Prüft dann C und D gegen die Liste: Stimmen die Fachgruppen? Sind in D wirklich nur verfügbare Bücher ab 2022, richtig sortiert?

<details>
<summary>Lösung</summary>

In unseren Läufen fanden A und B alle fünf Bücher. Bei *wer* schrieb A nur den Namen, B manchmal den ganzen Absender mit E-Mail-Adresse. Das Jahr bei Okan Demir („letztes Jahr“) ließ A leer; B setzte *2023* ein, geraten. Fehlende Werte sind bei A leer (*nan*), bei B *null*.

C ordnet die meisten Bücher plausibel zu; bei Grenzfällen wie *Lesen im digitalen Zeitalter* (Erziehungswissenschaft, aber keine der Fachgruppen) muss das Modell sich etwas aussuchen. D lieferte sechs Bücher, richtig gefiltert und sortiert, vom teuersten (*Metadaten in der Praxis*, 49,95 €) bis *Open Science in der Hochschule* (0 €).

Die Lehre: Keiner der Wege prüft, ob der Inhalt stimmt. Structured Output garantiert die **Form**, nicht den **Inhalt**.

</details>

### 🟢 2. Ein kleines Modell

Stellt in beiden KI-Modellen die **Quelle** auf *Lokal (Ollama)* und drückt **▶** an *A: Antwort des Modells*, *A: Tabelle* und *B: Tabelle*. Startet nicht den ganzen Flow: Batch Run (C) braucht mit dem lokalen Modell sehr lange.

<details>
<summary>Lösung</summary>

Mit `qwen3.5:4b` haben wir beobachtet:

- **A:** Das Modell ließ die Kopfzeile weg und ein Buch (das zweite von Prof. Brandt) fehlte. Type Convert machte die erste Datenzeile zur Kopfzeile: Die Spalten hießen *Martin Albers*, *Digitale Editionen planen*, *2025* und so weiter.
- **B:** Die Spalten stimmten, weil Structured Output sie vorgibt. Aber das Modell vertauschte *autor* und *wer*: Unter *autor* standen die Personen, die die Bücher vorschlagen.

Der Unterschied zeigt, was Structured Output leistet: Die Form ist sicher, der Inhalt hängt vom Modell ab. Ganz kleine Modelle, die keine Werkzeugaufrufe können, brechen bei Structured Output mit einer Meldung wie *Model does not support tool calling* ab. Stellt danach die Quelle wieder auf *Cluster*.

</details>

### 🟢 3. Ohne Auto Parse

1. Im Baustein *A: Text → Tabelle (Type Convert)* unter *Parameters* **Auto Parse** ausschalten und ▶ an *A: Tabelle* drücken.
2. Auto Parse wieder einschalten. Ergänzt im Prompt *A: Prompt verlangt CSV* am Ende: `Beginne deine Antwort mit dem Satz: Hier ist die Tabelle.` Drückt ▶ an *A: Tabelle*.

<details>
<summary>Lösung</summary>

1. Ohne Auto Parse wird jede Zeile der Antwort eine Zeile in einer einzigen Spalte `text`, die Kopfzeile eingeschlossen. Type Convert weiß dann nicht, dass es CSV ist.
2. Mit dem Satz davor erkennt auch Auto Parse keine CSV mehr, und es kommt wieder eine Spalte `text` heraus. Genau das passiert, wenn ein Modell freundlich sein will. Darum „nur“, „ohne Erklärung“ und „ohne ```“ im Prompt. Entfernt den Satz wieder.

</details>

### 🟢 4. Bessere Feldbeschreibungen

Öffnet im Baustein *B: Structured Output* das **Output Schema** und ändert die **Description**:

- bei *wer*: `Vor- und Nachname der Person, die das Buch vorschlägt, ohne Titel und E-Mail-Adresse`
- bei *jahr*: `Erscheinungsjahr, nur wenn es ausdrücklich genannt ist; sonst 0`

Drückt zwei- oder dreimal ▶ an *B: Tabelle*.

<details>
<summary>Lösung</summary>

In unseren Läufen half die neue Beschreibung bei *wer* nicht immer: Einmal standen noch die E-Mail-Adressen dabei, beim nächsten Lauf nur die Namen. Das Jahr für „letztes Jahr“ blieb trotz der Beschreibung *2023*. Beschreibungen steuern das Modell, sie zwingen es nicht. Was sich sicher prüfen lässt (ist das Jahr eine Zahl zwischen 1450 und heute?), prüft besser ein Baustein ohne KI, z. B. *Data Operations* mit *Filter* ([L3](L3_tabellen_und_json.md)) oder *If-Else* ([L7](L7_verzweigen_und_absichern.md)).

</details>

### 🟡 5. JSON statt CSV

Schreibt den Prompt von Weg A so um, dass das Modell JSON liefert. Ersetzt alles ab „Antworte nur mit einer CSV-Tabelle“ durch:

```text
Antworte nur mit einem JSON-Array: ein Objekt pro Buch mit den Schlüsseln autor, titel, jahr, verlag, isbn und wer. Fehlt eine Angabe, nimm null. Keine Erklärung. Erfinde nichts.
```

Drückt ▶ an *A: Antwort des Modells* und *A: Tabelle*. Probiert dann, ein Beispiel mit geschweiften Klammern in den Prompt zu schreiben, z. B. `{"autor": "Nachname, Vorname"}`. Was passiert am Baustein?

<details>
<summary>Lösung</summary>

Das Modell antwortete mit einem JSON-Array, Type Convert machte mit Auto Parse dieselbe Tabelle daraus wie bei CSV. In unserem Lauf stand beim Buch von Okan Demir für *jahr* ehrlich *null*, dafür fehlte dort der Verlag, obwohl er in der Mail steht. JSON oder CSV ist für Type Convert gleich gut; JSON ist robuster, wenn Werte Kommas enthalten.

Mit dem Beispiel in geschweiften Klammern bekommt das Prompt Template einen neuen Eingang namens `"autor"`: Es hält den Text für einen Platzhalter. Löscht das Beispiel wieder und beschreibt die Form in Worten.

</details>

### 🟡 6. Ein neues Feld

Ergänzt im **Output Schema** von *B: Structured Output* eine neue Zeile:

| Name | Description | Type | As List |
| --- | --- | --- | --- |
| `exemplare` | `Anzahl gewünschter Exemplare; 1, wenn nichts dazu gesagt wird` | `int` | aus |

Wie würdet ihr dasselbe in Weg A erreichen?

<details>
<summary>Lösung</summary>

B lieferte eine neue Spalte *exemplare*: 2 bei Jana Petersen („zwei Exemplare wären toll“), 1 bei allen anderen. Ein neues Feld kostet in Structured Output eine Tabellenzeile. In Weg A müsst ihr die Kopfzeile im Prompt um `exemplare` erweitern und die Regel für fehlende Angaben dazuschreiben.

</details>

### 🟡 7. Batch Run sieht die ganze Zeile

Im Baustein *C: Batch Run*:

1. **Column Name** leeren.
2. Unter *Parameters* **Enable Metadata** einschalten.
3. Unter *Parameters* den **Output Column Name** auf `gruppe` ändern.

Drückt ▶ an *C: Tabelle*. Was ändert sich?

<details>
<summary>Lösung</summary>

Mit leerem *Column Name* bekommt das Modell die ganze Zeile als Liste „spalte = wert“, also auch das Fach aus der Liste, nicht nur den Titel. Das Modell hat damit mehr Anhaltspunkte, dafür schickt jeder Aufruf mehr Text. Vergleicht die Fachgruppen mit dem vorigen Lauf. Die neue Spalte heißt jetzt *gruppe*. *Enable Metadata* fügt eine Spalte *metadata* an, z. B. mit `processing_status: success`. *batch_index* ist immer da.

</details>

### 🟡 8. Was Smart Transform kann und was nicht

Gebt *D: Smart Transform* nacheinander diese **Instructions** und drückt jeweils ▶ an *D: Tabelle*:

1. `Füge eine Spalte preis_mit_rabatt hinzu: preis_eur minus 10 Prozent, auf zwei Stellen gerundet. Behalte nur titel, preis_eur und preis_mit_rabatt.`
2. `Zähle für jedes Fach, wie viele Bücher es gibt.`

<details>
<summary>Lösung</summary>

1. funktioniert: eine Tabelle mit Titel, Preis und Rabattpreis, für alle 15 Zeilen, richtig gerechnet (29,90 → 26,91). Das Modell hat ein Programm geschrieben, Langflow hat es auf jede Zeile angewendet. Es ist darum genauer als Batch Run, wo das Modell selbst rechnen müsste.
2. scheitert in unseren Versuchen jedes Mal mit *name '\_\_import\_\_' is not defined*. Fürs Zählen greift das Modell zu einer Programm-Bibliothek, und die erlaubt Langflow hier nicht.

Faustregel: Smart Transform für Filtern, Sortieren, Spalten auswählen und einfache Rechnungen pro Zeile. Was sich auch ohne KI einstellen lässt, macht ihr besser mit *Data Operations* ([L3](L3_tabellen_und_json.md)): Das Ergebnis ist bei jedem Lauf gleich.

</details>

### 🔴 9. Gebühren aus der Benutzungsordnung

Baut einen neuen kleinen Flow: **Read File** mit `daten/lernpfad/benutzungsordnung.txt` → **Structured Output** → **Chat Output**, dazu ein **KI-Modell** (Quelle *Cluster*) für den Eingang *Language Model*. Das Ergebnis soll eine Tabelle aller Gebühren sein, mit den Feldern *leistung* (Text), *betrag_euro* (Zahl mit Komma) und *einheit* (Text). Probiert es erst **ohne** Schema Name.

<details>
<summary>Lösung</summary>

Output Schema:

| Name | Description | Type |
| --- | --- | --- |
| `leistung` | `Wofür die Gebühr anfällt` | `str` |
| `betrag_euro` | `Betrag in Euro als Zahl` | `float` |
| `einheit` | `Wofür der Betrag gilt, z. B. pro Medium und Öffnungstag` | `str` |

Den Ausgang *Structured Output* (Table) mit dem Chat Output verbinden.

**Ohne Schema Name** bekamen wir eine einzige, unsinnige Zeile: *Eligibility*, 0, *N/A*. Das Modell wusste nicht, *was* es herausziehen soll; die Feldbeschreibungen allein sagen das nicht. **Mit Schema Name** `Gebuehr` (*Parameters*) kamen alle vier Gebühren: Fernleihe 1,50 €, Versäumnisgebühr 0,50 € pro Medium und Öffnungstag, höchstens 20 € pro Medium, Ersatzausweis 10 €. Ein Satz vor den *Format Instructions* wie „Ziehe aus der Benutzungsordnung jede Gebühr heraus, eine Zeile pro Gebühr.“ hilft zusätzlich.

</details>

## 5. Wann nehme ich was?

| | **A: Prompt + Type Convert** | **B: Structured Output** | **C: Batch Run** | **D: Smart Transform** |
| --- | --- | --- | --- | --- |
| **Eingabe** | Text | Text | Tabelle | JSON, Tabelle oder Text |
| **Ergebnis** | Tabelle, wenn die Antwort sauber ist | Tabelle oder JSON mit genau euren Feldern | eure Tabelle plus eine Spalte | umgeformte Daten |
| **Wer macht die Arbeit?** | das Modell | das Modell | das Modell, Zeile für Zeile | ein Programm, das das Modell schreibt |
| **Wie sicher ist die Form?** | hängt vom Modell ab; ein Satz zu viel und es gibt keine Spalten | sicher | sicher (eine neue Spalte), der Inhalt der Spalte ist freier Text | sicher, wenn das Programm läuft |
| **Was muss das Modell können?** | Anweisungen genau befolgen | Werkzeugaufrufe | kurze Anweisungen befolgen | ein kleines Programm schreiben |
| **Aufrufe des Modells** | einer | einer | einer pro Zeile | einer, egal wie viele Zeilen |
| **Mit einem kleinen lokalen Modell** | oft fehlerhaft | Form stimmt, Inhalt oft nicht | sehr langsam | funktioniert für einfache Anweisungen |
| **Typisch für** | schnelle Versuche, flexible Formate | Angaben aus E-Mails, PDFs, Literaturangaben herausziehen | jede Publikation zusammenfassen, einordnen, übersetzen | filtern, sortieren, rechnen in Worten statt mit Einstellungen |

Und zwei Wege ganz ohne KI, die oft reichen:

- Liegen die Daten **schon strukturiert** vor (CSV, JSON von einem Webdienst), braucht ihr kein Modell: *Type Convert*, *Data Operations* und *Parser* ([L3](L3_tabellen_und_json.md), [L4](L4_ergebnisse_ausgeben.md)) sind schneller, kostenlos und liefern jedes Mal dasselbe.
- Soll ein **Agent** recherchieren und das Ergebnis in Feldern abliefern, gebt ihm ein *Output Schema* ([L9](L9_agenten.md)).

Die Faustregel: Wenn ein Baustein ohne KI die Aufgabe kann, nehmt ihn. Wenn das Modell Text verstehen muss, nehmt Structured Output für feste Felder und Batch Run für viele einzelne Einträge.

## 6. Wenn etwas nicht klappt

| Meldung oder Problem | Ursache und Lösung |
| --- | --- |
| Die Tabelle von A hat nur eine Spalte `text` | Die Antwort ist kein reines CSV oder JSON: ein Satz davor, ein Code-Block mit ```, oder Auto Parse ist aus. Prompt verschärfen, *Kreativität* auf 0, Auto Parse einschalten. |
| Die Spalten von A heißen wie ein Buch | Das Modell hat die Kopfzeile weggelassen. Die Kopfzeile wörtlich in den Prompt schreiben, ein größeres Modell nehmen. |
| Das Prompt Template hat plötzlich einen Eingang wie `"autor"` | Geschweifte Klammern im Prompt werden zu Platzhaltern. JSON in Worten beschreiben. |
| *Model does not support tool calling* | Das Modell kann keine Werkzeugaufrufe, Structured Output braucht sie. Quelle *Cluster* nehmen. |
| *No structured output returned* | Das Modell hat nichts Passendes gefunden. *Schema Name* setzen, einen Satz in die *Format Instructions* schreiben, was gesucht ist. |
| Structured Output liefert eine einzige, unsinnige Zeile | Wie oben: Dem Modell fehlt die Aufgabe. Schema Name und Format Instructions ergänzen. |
| Batch Run läuft und läuft | Jede Zeile ist ein Aufruf, alle gleichzeitig. Mit dem lokalen Modell bricht er nach dem Zeitlimit von 10 Minuten ab. Cluster nehmen oder die Tabelle vorher kürzen (*Data Operations* → *Head*, [L3](L3_tabellen_und_json.md)). |
| *Column '…' not found in the DataFrame* | Der *Column Name* in Batch Run passt zu keiner Spalte. Groß- und Kleinschreibung beachten oder das Feld leeren. |
| *name '\_\_import\_\_' is not defined* | Smart Transform hat ein Programm geschrieben, das Langflow nicht erlaubt, meist beim Zählen oder Gruppieren. Anweisung vereinfachen oder einen anderen Weg nehmen. |
| *Failed to convert result to DataFrame output* | Smart Transform hat etwas geliefert, das keine Tabelle ist. Den Ausgang *Message* oder *JSON* nehmen oder die Anweisung genauer fassen. |
| Ein Jahr wie „letztes Jahr“ wird falsch | Das Modell kennt das heutige Datum nicht. *Current Date* in den Prompt geben ([L5](L5_prompts_und_modelle.md)) oder das Feld leer lassen und von Hand prüfen. |

**Weiter:** [L7 Verzweigen und absichern](L7_verzweigen_und_absichern.md) zeigt, wie ihr Ergebnisse prüft und je nach Inhalt auf verschiedene Wege schickt.
