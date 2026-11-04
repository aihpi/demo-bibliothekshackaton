# L8 Wiederholen mit Loop

Viele Aufgaben in Bibliotheken bestehen darin, dasselbe für jeden Eintrag einer Liste zu tun: jede DOI nachschlagen, jede ISBN im Katalog suchen, für jede Publikation prüfen, ob sie frei zugänglich ist. Ein Webdienst beantwortet aber meist nur eine Frage auf einmal. Der Baustein **Loop** löst das: Er nimmt eine Tabelle, gibt die Zeilen nacheinander an eine Reihe von Bausteinen und sammelt die Ergebnisse wieder ein.

Dieser Flow schlägt eine Liste von DOIs bei Crossref nach und macht daraus eine Tabelle mit Titel, Jahr, Zeitschrift, Zahl der Zitationen und Hinweis auf zurückgezogene Artikel.

| | |
| --- | --- |
| **Ihr lernt** | Eine Liste in Einträge zerlegen, eine Schleife bauen und schließen, die Ausgänge *Item* und *Done* unterscheiden, pro Eintrag einen Webdienst fragen, Fehler in einer Runde verstehen. Und: wann *Batch Run* einfacher ist als eine Loop. |
| **Bausteine** | Chat Input, Split Text, Loop, Parser, Prompt Template, API Request, Data Operations, Chat Output; in Übung 7 Batch Run und KI-Modell |
| **KI** | keine, nur in Übung 7 |
| **Dauer** | etwa 60 Minuten |
| **Testdaten** | `daten/lernpfad/dois.txt` |

## Inhalt

1. [Der Flow im Überblick](#1-der-flow-im-überblick)
2. [Vorbereiten](#2-vorbereiten)
3. [Schritt für Schritt](#3-schritt-für-schritt)
4. [Übungen](#4-übungen)
5. [Wann nehme ich was?](#5-wann-nehme-ich-was)
6. [Wenn etwas nicht klappt](#6-wenn-etwas-nicht-klappt)

## 1. Der Flow im Überblick

Der Flow hat drei Teile:

| Teil | Bausteine | Was passiert |
| --- | --- | --- |
| Vorher | **DOI-Liste (Chat)**, **Eine DOI pro Zeile** (Split Text) | Die eingefügte Liste wird zu einer Tabelle mit einer Zeile pro DOI. |
| Die Schleife (gelber Bereich) | **DOI als Text** (Parser), **Adresse bauen** (Prompt Template), **Crossref fragen** (API Request), **Felder auslesen** (Data Operations) | Läuft einmal pro DOI: Adresse bauen, Crossref fragen, die wichtigen Felder als Datensatz ausgeben. |
| Nachher | **Ergebnistabelle** (Chat Output), **Als Liste** (Parser), **Ergebnisliste** (Chat Output) | Bekommt alle Datensätze auf einmal, als Tabelle und als Textliste. |

In der Mitte steht die **Loop** (*Jede DOI einzeln*). Sie hat zwei Ausgänge:

- **Item** führt in die Schleife. Hier kommt in jeder Runde ein Eintrag heraus.
- **Done** führt nach draußen. Hier kommen alle Ergebnisse heraus, wenn jeder Eintrag bearbeitet ist.

Die **gestrichelte Linie** vom letzten Baustein der Schleife zurück an den Ausgang *Item* schließt die Schleife. Sie sagt der Loop: Diese Runde ist fertig, hier ist ihr Ergebnis.

## 2. Vorbereiten

1. In der Übersicht beim Flow **L8 Wiederholen mit Loop** auf die drei Punkte klicken → *Duplicate*. Arbeitet in der Kopie.
2. Die Kopie öffnen und oben rechts auf **Playground** klicken.
3. Den Inhalt von `daten/lernpfad/dois.txt` einfügen und abschicken. Nach etwa 15 Sekunden erscheinen zwei Nachrichten: die Ergebnistabelle und dieselben Ergebnisse als Liste.

Die Datei enthält neun DOIs. Sieben kennt Crossref, eine davon gehört zu einem zurückgezogenen Artikel. Zwei kennt Crossref nicht: eine DOI, die bei DataCite registriert ist (Zenodo), und eine ausgedachte aus der Literaturliste des [Referenz-Checkers](../../daten/referenz_checker/).

Hier steht ein Chat Input am Anfang, und der ganze Flow hängt von ihm ab. Darum führt der Playground alles aus (zur Regel siehe [L1](L1_daten_importieren.md)).

## 3. Schritt für Schritt

### 3.1 Split Text: aus einer Liste eine Tabelle machen

Eine Loop braucht eine **Tabelle** (oder eine Liste von Datensätzen). Der Chat Input liefert aber einen einzigen Text. *Split Text* zerlegt ihn: Mit diesen Einstellungen wird jede Zeile zu einer Tabellenzeile, in der Spalte `text`.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Separator** | am Baustein | `\n`: an jedem Zeilenumbruch trennen |
| **Chunk Size** | am Baustein | `1`: jedes Stück so kurz wie möglich, also nie zwei Zeilen zusammenlegen |
| **Chunk Overlap** | am Baustein | `0`: keine Zeichen doppelt in benachbarten Stücken |
| **Clean Output** | *Parameters* | an: nur die Spalte `text`, ohne Zusatzangaben. Leere Zeilen und Leerzeichen am Rand fallen dabei weg. |

Mehr zu Split Text in [L2](L2_texte_aufbereiten.md).

### 3.2 Loop: Eintrag für Eintrag

| | Name | Was es ist |
| --- | --- | --- |
| Eingang | **Inputs** | Die Einträge: eine Tabelle, ein Datensatz (JSON) oder ein Text |
| Ausgang | **Item** | Der aktuelle Eintrag als JSON, für den ersten Baustein der Schleife. Hier endet auch die Rücklinie. |
| Ausgang | **Done** | Alle Ergebnisse als Tabelle, eine Zeile pro Runde |

Die Loop hat keine Einstellungen. Was sie tut, bestimmt ihr durch die Verbindungen:

- Alles, was von *Item* aus erreichbar ist, bis zur Rücklinie, gehört zur Schleife und läuft einmal pro Eintrag.
- Was in der letzten Runde an der Rücklinie ankommt, ist das Ergebnis dieser Runde. Die Loop sammelt alle diese Ergebnisse und gibt sie bei *Done* als Tabelle aus. Liefert der letzte Baustein einen Datensatz mit Feldern (wie hier), werden die Felder zu Spalten.
- Alles, was an *Done* hängt, läuft einmal, wenn die Schleife fertig ist.

**So schließt ihr eine Schleife:** Vom Ausgang des letzten Bausteins in der Schleife eine Linie **zurück zum Ausgang *Item*** der Loop ziehen, nicht zu ihrem Eingang. Die Linie wird gestrichelt angezeigt.

**Zwischenergebnisse ansehen:** Nach einem Lauf zeigen die Bausteine in der Schleife den Stand der **letzten Runde**, hier also die Antwort zur letzten DOI. Die Ergebnisse aller Runden seht ihr nur bei *Done*. Drückt ihr **▶** an einem Baustein in der Schleife, läuft die ganze Schleife, nicht nur eine Runde.

### 3.3 Parser und Prompt Template: die Adresse bauen

Der Eintrag aus *Item* ist ein Datensatz mit dem Feld `text`. **DOI als Text** (Parser mit der Vorlage `{text}`) macht daraus einen einfachen Text, denn ein Prompt Template nimmt nur Text an.

**Adresse bauen** (Prompt Template) setzt die DOI in die Adresse ein, ganz ohne KI:

```text
https://api.crossref.org/works?filter=doi:{doi}&rows=1&select=DOI,title,issued,container-title,is-referenced-by-count,updated-by
```

| Teil | Bedeutung |
| --- | --- |
| `filter=doi:{doi}` | nur die Publikation mit dieser DOI |
| `rows=1` | höchstens ein Treffer |
| `select=…` | nur diese Felder: DOI, Titel, Erscheinungsdatum, Zeitschrift, Zahl der Zitationen, Hinweise auf Korrekturen und Rückzüge |

Warum nicht einfach `https://api.crossref.org/works/{doi}`? Diese kürzere Adresse gibt es auch. Kennt Crossref die DOI aber nicht, antwortet sie mit einem kurzen Text statt mit JSON, und daran scheitert der nächste Schritt (siehe Übung 5). Die Suche mit `filter` antwortet immer mit JSON, notfalls mit einer leeren Trefferliste.

### 3.4 API Request: Crossref fragen

Derselbe Baustein wie in [L1](L1_daten_importieren.md), nur kommt die Adresse jetzt aus dem Prompt Template: Im Feld **URL** steht *Receiving input*.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **URL** | am Baustein | Kommt in jeder Runde neu aus *Adresse bauen* |
| **Headers** | *Parameters* | Ein *User-Agent* mit Name und Webadresse. Crossref bittet darum, damit es bei Problemen Kontakt aufnehmen kann. Ergänzt ihr eure E-Mail-Adresse, z. B. `Bibliothekshackathon/1.0 (https://github.com/aihpi/demo-bibliothekshackaton; mailto:name@bibliothek.de)`, landet die Anfrage im *Polite Pool* von Crossref, der seltener gebremst wird. |
| **Timeout** | *Parameters* | Sekunden bis zum Abbruch einer Anfrage, Standard 30 |

**Höflich bleiben:** Jede Runde ist eine Anfrage an Crossref. Neun DOIs sind kein Problem, eine Runde dauert gut eine Sekunde. Fragen aber viele Gruppen im selben WLAN gleichzeitig, bremst Crossref und antwortet mit Status 429 (*zu viele Anfragen*); dann bricht die Schleife ab (siehe [Abschnitt 6](#6-wenn-etwas-nicht-klappt)). Für tausende DOIs ist eine Schleife im Playground nicht gedacht; dafür gibt es Massendownloads und Abfragen mit mehreren DOIs auf einmal (siehe [Abschnitt 5](#5-wann-nehme-ich-was)).

### 3.5 Data Operations: die Felder auslesen

**Felder auslesen** steht auf *Input Type* **JSON** und *Operation* **JQ Expression**. JQ ist eine kleine Abfragesprache für JSON. Der Ausdruck im Feld *JQ Expression* macht aus der langen Antwort von Crossref einen Datensatz mit sechs Feldern: `doi`, `jahr`, `titel`, `zeitschrift`, `zitiert` und `status`. Ihr müsst ihn nicht im Detail verstehen; diese Teile genügen:

| Teil des Ausdrucks | Bedeutung |
| --- | --- |
| `.result.message.items[0] as $w` | den ersten Treffer unter dem Namen `$w` merken |
| `if $w == null then … else … end` | Gibt es keinen Treffer, einen Datensatz mit `status: "nicht bei Crossref"` ausgeben, sonst die Felder des Treffers |
| `titel: ($w.title[0] // "?")` | das Feld `titel` aus dem ersten Titel füllen; `//` heißt „wenn das fehlt, dann …“ |
| `updated-by … "retraction"` | `status` auf `ZURÜCKGEZOGEN` setzen, wenn Crossref einen Rückzug kennt |

Mehr zu JQ und den übrigen JSON-Operationen in [L3](L3_tabellen_und_json.md).

Der Ausgang dieses Bausteins ist das Ergebnis einer Runde. Darum führt von ihm die Rücklinie zur Loop.

### 3.6 Nach der Schleife: Done weiterverarbeiten

*Done* liefert eine ganz normale Tabelle. Alles, was ihr in [L3](L3_tabellen_und_json.md) und [L4](L4_ergebnisse_ausgeben.md) mit Tabellen macht, geht auch hier:

- **Ergebnistabelle** (Chat Output) zeigt sie direkt an.
- **Als Liste** (Parser) macht aus jeder Zeile eine Textzeile mit der Vorlage `- {doi}: {titel} ({jahr}), {zeitschrift}. {status}`. Die Namen in Klammern sind die Spalten aus *Felder auslesen*.

## 4. Übungen

🟢 Ausprobieren · 🟡 Umbauen · 🔴 Selbst bauen. Die Lösungen lassen sich aufklappen.

### 🟢 1. Was eine Runde sieht

Führt den Flow mit `dois.txt` aus. Klickt danach nacheinander auf die Ausgabe-Symbole von **DOI als Text**, **Crossref fragen** und **Felder auslesen**. Welche DOI seht ihr dort? Vergleicht mit dem Ausgang **Done** der Loop.

<details>
<summary>Lösung</summary>

Die Bausteine in der Schleife zeigen nur die **letzte Runde**, hier die letzte DOI der Liste (`10.1515/bfp-2021-9917`): Crossref hat keinen Treffer, *Felder auslesen* gibt einen Datensatz mit `status: nicht bei Crossref` aus. *Done* dagegen enthält alle neun Ergebnisse. Wollt ihr eine bestimmte Runde genauer ansehen, setzt die DOI ans Ende der Liste oder lasst den Flow mit nur dieser DOI laufen.

</details>

### 🟢 2. Eure eigene Liste

1. Fügt im Playground eine Liste mit Leerzeilen und Leerzeichen ein, z. B.:

   ```text
     10.1136/bmj.n71

   10.7717/peerj.4375
   ```

2. Ergänzt dann eine Zeile, die keine DOI ist, z. B. `DOIs aus der Masterarbeit`, und schickt die Liste noch einmal ab.

<details>
<summary>Lösung</summary>

1. Funktioniert: *Split Text* lässt mit *Clean Output* leere Zeilen weg und entfernt Leerzeichen am Rand.
2. Der ganze Lauf bricht ab mit *Invalid URL provided*, und es gibt **gar kein Ergebnis**, auch nicht für die gültigen DOIs. Die Zeile enthält Leerzeichen, die Adresse wird ungültig, *API Request* meldet einen Fehler, und ein Fehler in einer Runde beendet die ganze Schleife. Darum lohnt es sich, die Liste vorher zu säubern ([L2](L2_texte_aufbereiten.md)) oder ungeeignete Einträge mit *If-Else* auszusortieren ([L7](L7_verzweigen_und_absichern.md)).

</details>

### 🟢 3. Ohne Rücklinie

Klickt die gestrichelte Linie von **Felder auslesen** zur Loop an und löscht sie (`Entf` bzw. `Backspace`). Führt den Flow aus. Zieht die Linie danach wieder: vom Ausgang von *Felder auslesen* zum Ausgang **Item** der Loop.

<details>
<summary>Lösung</summary>

Ohne Rücklinie gibt es keine Schleife: Die Bausteine dazwischen laufen gar nicht, *Done* ist leer, und beide Chat Outputs bleiben leer. Eine Fehlermeldung gibt es nicht. Wenn eine Loop „nichts tut“, ist die fehlende oder falsch angeschlossene Rücklinie die häufigste Ursache. Die Linie muss am Ausgang *Item* enden; den Eingang *Inputs* belegt schon *Split Text*.

</details>

### 🟢 4. Ein Feld mehr: der Verlag

Crossref kennt auch den Verlag, im Feld `publisher`. Nehmt ihn in die Ergebnisse auf:

1. In **Felder auslesen** im Ausdruck vor `status: (if` den Text `verlag: $w.publisher, ` einfügen.
2. In **Als Liste** die Vorlage auf `- {doi}: {titel}, Verlag: {verlag}` ändern.
3. Ausführen. Was steht beim Verlag?

<details>
<summary>Lösung</summary>

Beim Verlag steht `nan` (*not a number*, so zeigt eine Tabelle ein leeres Feld). Die Adresse holt mit `select` nur die Felder, die dort aufgezählt sind, und `publisher` gehört nicht dazu. Ergänzt in **Adresse bauen** am Ende `,publisher`. Dann steht z. B. bei `10.1136/bmj.n71` *BMJ*. Bei den DOIs, die Crossref nicht kennt, bleibt es bei `nan`, weil ihr Datensatz kein Feld `verlag` hat.

Merkt euch: Ein Feld muss an zwei Stellen stehen, in der Anfrage und in der Auswertung.

</details>

### 🟡 5. DOIs als Links

Oft stehen DOIs als Link in einer Liste, z. B. `https://doi.org/10.1136/bmj.n71`.

1. Schickt diese Liste ab:

   ```text
   https://doi.org/10.1136/bmj.n71
   10.7717/peerj.4375
   ```

2. Repariert den Flow, sodass beide Schreibweisen funktionieren. Tipp: ein Baustein zwischen *DOI-Liste (Chat)* und *Eine DOI pro Zeile*.

<details>
<summary>Lösung</summary>

1. Der Lauf bricht ab mit *JSON Query error: Object of type bytes is not JSON serializable*. Crossref versteht `doi:https://doi.org/…` nicht und antwortet mit einer Fehlermeldung als Text statt mit JSON. *API Request* reicht den Text weiter, und *Data Operations* kann ihn nicht als JSON lesen.
2. Einen **Data Operations** einfügen: *Input Type* **Text**, *Operation* **Text Replace**, *Search Pattern* `https://doi.org/`, *Replacement Text* leer lassen. Die Verbindung vom Chat Input an seinen Eingang *Text* legen und seinen Ausgang *Message* mit dem Eingang von *Eine DOI pro Zeile* verbinden. Jetzt kommen beide DOIs durch.

</details>

### 🟡 6. Nach Zitationen sortieren

Fügt hinter *Done* einen **Data Operations** ein, der die Ergebnisse nach der Zahl der Zitationen sortiert, die meistzitierte Publikation zuerst, und zeigt das Ergebnis in einem neuen Chat Output.

<details>
<summary>Lösung</summary>

*Input Type* **Table**, *Operation* **Sort**, *Column Name* `zitiert`, *Sort Ascending* **aus**. *Done* an den Eingang *Table* anschließen, den Ausgang an einen neuen *Chat Output*. Ganz oben steht jetzt das PRISMA-2020-Statement. *Done* kann mehrere Bausteine gleichzeitig beliefern; die Schleife läuft trotzdem nur einmal.

</details>

### 🟡 7. Batch Run: eine KI-Frage pro Zeile

Lasst die KI jede gefundene Publikation einem Thema zuordnen:

1. Einen **KI-Modell**-Baustein (Kategorie *Bibliothek*) und einen **Batch Run** (Kategorie *LLM Operations*) auf die Arbeitsfläche ziehen.
2. Den Ausgang **Language Model** von *KI-Modell* mit dem Eingang **Language Model** von *Batch Run* verbinden, *Done* mit dem Eingang **Table**.
3. In *Batch Run*: **Instructions** `Ordne die Publikation einem Thema zu: Open Access, Forschungsintegrität, Bibliometrie oder Sonstiges. Antworte nur mit dem Thema.`, **Column Name** `titel`. Unter *Parameters* **Output Column Name** `thema`.
4. Den Ausgang *LLM Results* an einen neuen Chat Output hängen und ausführen.

Warum steht *Batch Run* hinter der Loop und nicht in ihr?

<details>
<summary>Lösung</summary>

Die Tabelle bekommt eine neue Spalte `thema` (und eine Spalte `batch_index` mit der Zeilennummer). *Batch Run* ist selbst eine Art Schleife: Er ruft das Modell einmal pro Zeile auf, aber nur mit dem Inhalt der gewählten Spalte und eurer Anweisung. Für „eine KI-Frage pro Zeile“ ist er viel einfacher als eine Loop mit Prompt und Modell darin.

Eine Loop braucht ihr, wenn eine Runde **mehrere Schritte** hat oder etwas anderes als ein Modell fragt, wie hier eine Adresse bauen, Crossref fragen und die Antwort auslesen. Beides lässt sich kombinieren: erst mit der Loop Daten holen, dann mit *Batch Run* jede Zeile von der KI einordnen lassen.

Mit einem kleinen lokalen Modell dauert jede Zeile einige Sekunden; nehmt im KI-Modell bei **Quelle** den Cluster, wenn es zu langsam ist. Prüft die Themen stichprobenartig: Die KI ordnet nach dem Titel ein und kann sich irren.

</details>

### 🔴 8. Ist es frei zugänglich? Eine Schleife mit Unpaywall

Baut eine zweite Schleife, die für jede DOI bei **Unpaywall** nachsieht, ob die Publikation frei zugänglich ist und wo. Die Adresse:

```text
https://api.unpaywall.org/v2/DOI?email=EURE-E-MAIL-ADRESSE
```

Unpaywall verlangt eine echte E-Mail-Adresse. In der Antwort stehen unter `result` die Felder `is_oa` (frei zugänglich: true/false), `oa_status` (z. B. *gold*, *hybrid*, *green*, *closed*) und `best_oa_location.url` (der beste freie Link). Tipp: Kopiert die Bausteine aus diesem Flow und ändert nur, was nötig ist.

<details>
<summary>Lösung</summary>

Dieselbe Bauweise wie im Flow, mit drei Änderungen:

1. **Adresse bauen**: `https://api.unpaywall.org/v2/{doi}?email=EURE-E-MAIL-ADRESSE`
2. **Felder auslesen**: `{doi: .result.doi, frei: .result.is_oa, art: (.result.oa_status // "–"), link: (.result.best_oa_location.url // "–")}`
3. **Als Liste**: `- {doi}: frei zugänglich {frei} ({art}) {link}`

Mit `10.1136/bmj.n71`, `10.7717/peerj.4375` und `10.1016/S0140-6736(97)11096-0` kommt heraus: *True (hybrid)* mit einem Link zum PDF beim BMJ, *True (gold)* bei PeerJ, *False (closed)* beim zurückgezogenen Lancet-Artikel.

Achtung: Für DOIs, die Unpaywall nicht kennt, antwortet der Dienst mit einer Webseite statt mit JSON, und die ganze Schleife bricht ab, wie in Übung 5. Nehmt für diese Übung nur DOIs, die Crossref gefunden hat.

</details>

## 5. Wann nehme ich was?

| Ihr wollt … | Baustein | Hinweis |
| --- | --- | --- |
| für jede Zeile **eine KI-Frage** stellen (zusammenfassen, einordnen, übersetzen) | **Batch Run** | Einfacher als eine Loop; das Ergebnis ist eine neue Spalte |
| für jede Zeile **mehrere Schritte** ausführen oder einen **Webdienst** fragen | **Loop** | Rücklinie an *Item* nicht vergessen; Ergebnisse kommen bei *Done* |
| viele Einträge bei einem Dienst nachschlagen, der **mehrere auf einmal** annimmt | **API Request** ohne Loop | Crossref nimmt z. B. `filter=doi:10.1136/bmj.n71,doi:10.7717/peerj.4375&rows=20`. Eine Anfrage statt vieler ist schneller und schont den Dienst. |
| eine Tabelle filtern, sortieren oder umformen | **Data Operations** (Table) | Braucht keine Schleife, wirkt auf alle Zeilen ([L3](L3_tabellen_und_json.md)) |
| aus jeder Zeile eine Textzeile machen | **Parser** | Wendet die Vorlage auf jede Zeile an, ganz ohne Schleife ([L4](L4_ergebnisse_ausgeben.md)) |

Faustregel: Erst prüfen, ob ein Baustein die ganze Tabelle auf einmal bearbeiten kann. Die Loop ist das Werkzeug für den Rest.

## 6. Wenn etwas nicht klappt

| Meldung oder Problem | Ursache und Lösung |
| --- | --- |
| Die Chat Outputs bleiben leer, keine Fehlermeldung | Die Rücklinie fehlt oder endet nicht am Ausgang *Item* der Loop (Übung 3). Oder die Liste war leer. |
| *Invalid URL provided* | Ein Eintrag enthält Leerzeichen oder ist keine DOI (Übung 2). Die Liste säubern. |
| *JSON Query error: Object of type bytes is not JSON serializable* | Der Webdienst hat nicht mit JSON geantwortet: Er versteht die Adresse nicht (Übung 5), kennt den Eintrag nicht (Übung 8), oder er bremst gerade, weil zu viele Anfragen kommen (Status 429, oft wenn viele Gruppen gleichzeitig fragen). Dann einige Sekunden warten und noch einmal ausführen; eine E-Mail-Adresse im *User-Agent* hilft (siehe [3.4](#34-api-request-crossref-fragen)). |
| Es gibt gar kein Ergebnis, obwohl nur ein Eintrag falsch ist | So arbeitet die Loop: Ein Fehler in einer Runde beendet die ganze Schleife. Fehlerhafte Einträge vorher aussortieren. |
| In der Liste steht `nan` | Das Feld fehlt im Datensatz: nicht mit `select` angefragt (Übung 4) oder für diesen Eintrag nicht vorhanden. |
| Die Bausteine in der Schleife zeigen nur eine DOI | Richtig so: Sie zeigen die letzte Runde. Alle Ergebnisse stehen bei *Done*. |
| Der Lauf dauert sehr lange | Jede Runde ist eine Anfrage, gut eine Sekunde bei Crossref. Lange Listen kürzen oder mehrere DOIs in einer Anfrage abfragen ([Abschnitt 5](#5-wann-nehme-ich-was)). |

**Weiter:** [L9 Agenten](L9_agenten.md) zeigt, wie eine KI selbst entscheidet, welche Werkzeuge sie in welcher Reihenfolge nutzt, statt einer festen Schleife zu folgen.
