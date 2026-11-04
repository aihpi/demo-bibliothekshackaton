# L3 Tabellen und JSON

Daten kommen selten so an, wie ihr sie braucht. Ein Webdienst schickt viel mehr Felder als nötig, verschachtelt ineinander. Eine Liste aus der Erwerbung enthält doppelte Zeilen, uneinheitliche Schreibweisen und Lücken. Bevor ihr Daten auswertet, an ein Sprachmodell gebt oder weitergebt, bringt ihr sie in Form. Dieser Flow zeigt das an zwei Beispielen, ganz ohne KI: einer Antwort von OpenAlex und der Liste der Neuerwerbungen.

| | |
| --- | --- |
| **Ihr lernt** | Den Unterschied zwischen Message, JSON und Table; Felder aus JSON herausgreifen und umbauen; aus einer CSV-Datei eine Tabelle machen; Tabellen filtern, sortieren, bereinigen und verbinden; Suchparameter für einen Webdienst bauen; eine Tabelle als Text ausgeben |
| **Bausteine** | Data Operations (JSON und Table), Type Convert, Dynamic Create Data, API Request, Read File, Parser, Chat Output |
| **KI** | keine |
| **Dauer** | etwa 60 Minuten |
| **Testdaten** | `daten/lernpfad/neuerwerbungen.csv`, `daten/lernpfad/fachreferate.csv`, `daten/lernpfad/neuerwerbungen_nachtrag.csv` |

## Inhalt

1. [Der Flow im Überblick](#1-der-flow-im-überblick)
2. [Vorbereiten](#2-vorbereiten)
3. [Schritt für Schritt](#3-schritt-für-schritt)
4. [Übungen](#4-übungen)
5. [Wann nehme ich was?](#5-wann-nehme-ich-was)
6. [Wenn etwas nicht klappt](#6-wenn-etwas-nicht-klappt)

## 1. Der Flow im Überblick

**Drei Datentypen.** In [L1](L1_daten_importieren.md) habt ihr gesehen, dass jede Quelle einen Typ liefert. In diesem Modul wechselt ihr ständig zwischen ihnen:

| Typ | Was es ist | Typisches Beispiel |
| --- | --- | --- |
| **Message** | Text | der Inhalt einer CSV-Datei aus *Read File*, ein Prompt, die Antwort eines Modells |
| **JSON** | ein Datensatz aus benannten Feldern, die wieder Felder oder Listen enthalten können | die Antwort eines Webdienstes |
| **Table** | Zeilen und Spalten wie in Excel | eine Trefferliste, eine Liste der Neuerwerbungen |

Viele Bausteine nehmen nur einen dieser Typen an. **Type Convert** wandelt zwischen ihnen um, und **Data Operations** bearbeitet jeden der drei, je nachdem, welchen *Input Type* ihr wählt.

Der Flow hat zwei Teile.

**Oben: Ein Webdienst wird zur Tabelle.**

| Schritt | Baustein | Was passiert |
| --- | --- | --- |
| 1 | **Suchparameter** (Dynamic Create Data) | baut die Suchparameter für OpenAlex: Suchbegriffe, Zahl der Treffer, gewünschte Felder |
| 2 | **OpenAlex fragen** (API Request) | schickt die Anfrage und bekommt JSON zurück |
| 3a | **Treffer herausgreifen** (Data Operations, *Path Selection*) | nimmt aus der Antwort nur die Liste der Treffer |
| 3b | **Felder auswählen und umbenennen** (Data Operations, *JQ Expression*) | baut jeden Treffer um: deutsche Feldnamen, verschachtelte Felder aufgelöst |
| 4 | **Als Tabelle** (Type Convert) | macht aus der Liste eine Tabelle |

Die beiden Chat Outputs *Treffer, wie OpenAlex sie liefert* und *Treffer, aufgeräumt* zeigen den Unterschied zwischen 3a und 3b.

**Unten: Eine Liste wird aufgeräumt.**

| Schritt | Baustein | Was passiert |
| --- | --- | --- |
| 1 | **Neuerwerbungen** (Read File) | liest die CSV-Datei als Text |
| 2 | **CSV als Tabelle** (Type Convert) | macht aus dem Text eine Tabelle |
| 3 | **Fach vereinheitlichen** (*Replace Value*) | ersetzt `informatik` durch `Informatik` |
| 4 | **Doppelte entfernen** (*Drop Duplicates*) | entfernt Zeilen mit derselben ISBN |
| 5 | **Fachreferat ergänzen** (*Merge*) | holt zu jedem Fach Fachreferat und Standort aus `fachreferate.csv` |
| 6 | **Nach Fach sortieren** (*Sort*) | sortiert die Tabelle |
| 7a | **Spalten auswählen** (*Select Columns*) | behält nur die Spalten, die jemand lesen will |
| 7b | **Nur bestellte** (*Filter*) und **Als Liste** (Parser) | behält die bestellten Titel und schreibt sie als Liste |

## 2. Vorbereiten

1. In der Übersicht beim Flow **L3 Tabellen und JSON** auf die drei Punkte klicken → *Duplicate*. Arbeitet in der Kopie.
2. Im Baustein **Neuerwerbungen (Read File)** `daten/lernpfad/neuerwerbungen.csv` hochladen, im Baustein **Fachreferate (Read File)** `daten/lernpfad/fachreferate.csv`.
3. **Playground** öffnen, irgendetwas abschicken. Nach wenigen Sekunden erscheinen vier Nachrichten.

Der Flow hat keinen Chat Input; der Playground führt also alles aus. Für die Übungen nutzt ihr meist **▶** am Baustein und schaut euch die Ausgabe direkt am Baustein an (Symbol unten rechts am Ausgang). Bei Tabellen erscheint dort eine Tabellenansicht.

Lest die Neuerwerbungen einmal in Ruhe durch. In der Datei stecken mit Absicht vier Fehler, wie sie in echten Listen vorkommen: *Künstliche Intelligenz verstehen* steht zweimal da, bei *Geschichte des Buchdrucks* fehlt das Jahr, *Datenbanken kompakt* hat das Fach `informatik` in Kleinbuchstaben, und um den Titel *Bibliotheken im Nationalsozialismus* stehen Leerzeichen.

## 3. Schritt für Schritt

### 3.1 Dynamic Create Data: Suchparameter bauen

In [L1](L1_daten_importieren.md) standen die Suchparameter für OpenAlex in der Adresse, mit `%20` statt Leerzeichen. Das ist fehleranfällig. *Dynamic Create Data* baut stattdessen einen JSON-Datensatz aus Feldern, die ihr festlegt. Den schließt ihr an den Eingang **Query Parameters** von *API Request* an, und der Baustein setzt die Parameter selbst richtig in die Adresse ein, Leerzeichen eingeschlossen.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Input Configuration** | am Baustein | Die Felder, eines pro Zeile: *Field Name* und *Field Type* (*Text*, *Number*, *Boolean* …). Für jedes Feld erscheint ein Eingang. Hier: `search`, `per-page` und `select`. |
| *ein Eingang pro Feld* | am Baustein | Der Wert. Eintippen oder von einem anderen Baustein verbinden, z. B. die Suchbegriffe aus einem Chat Input. |

Der Ausgang **JSON** ist der Datensatz, der Ausgang **Message** derselbe Inhalt als Text.

Die Feldnamen müssen genau so heißen, wie der Webdienst es erwartet. Welche das sind, steht in seiner Dokumentation, für OpenAlex unter <https://docs.openalex.org>.

### 3.2 Data Operations mit JSON

*Data Operations* ist ein Werkzeugkasten. Ihr wählt zuerst den **Input Type**, dann eine **Operation**; erst danach erscheinen die passenden Felder. Mit *JSON* gibt es diese Operationen:

| Operation | Was sie tut | Felder |
| --- | --- | --- |
| **Select Keys** | behält nur die genannten Felder der obersten Ebene | *Select Keys*: eine Liste von Feldnamen |
| **Remove Keys** | entfernt die genannten Felder | *Remove Keys* |
| **Rename Keys** | benennt Felder um | *Rename Keys*: Paare aus altem und neuem Namen |
| **Append or Update** | fügt Felder hinzu oder überschreibt vorhandene | *Append or Update*: Paare aus Name und Wert |
| **Path Selection** | greift einen einzelnen Wert heraus, auch tief verschachtelt | *JSON to Map* und *Select Path*, siehe unten |
| **JQ Expression** | baut JSON mit der Abfragesprache jq beliebig um | *JQ Expression* |
| **Combine** | führt mehrere Datensätze zu einem zusammen; gibt es ein Feld in beiden, wird daraus eine Liste beider Werte | mehrere Linien an den Eingang *JSON* |
| **Literal Eval** | verwandelt Text, der wie JSON aussieht, in echtes JSON | keine. Nützlich, wenn ein Sprachmodell JSON als Text liefert ([L6](L6_strukturierte_antworten.md)). |

Die Antwort von *API Request* sieht im Kern so aus:

```json
{
  "source": "https://api.openalex.org/works?search=…",
  "status_code": 200,
  "response_headers": { … },
  "result": {
    "meta": { "count": 1928193, … },
    "results": [
      { "display_name": "…", "publication_year": 2019, "doi": "…", "open_access": { "is_oa": true, … } },
      …
    ]
  }
}
```

Die Treffer stecken also in `result`, darin in `results`. Ein Punkt trennt die Ebenen: Der Weg zu den Treffern heißt `.result.results`.

**Path Selection.** Im Feld **JSON to Map** fügt ihr ein Beispiel der Daten ein, etwa die Ausgabe von *OpenAlex fragen*, die ihr nach ▶ kopiert. Langflow liest daraus alle Wege und bietet sie im Feld **Select Path** zur Auswahl an. Im Flow ist `.result.results` gewählt. Heraus kommt `{"result": [ … ]}`: die Liste der Treffer, unverändert, unter dem Namen `result`.

**JQ Expression.** jq ist eine kleine Sprache für JSON. Der Ausdruck im Flow lautet:

```text
.result.results | map({titel: .display_name, jahr: .publication_year, doi: (.doi // "keine DOI"), zitiert: .cited_by_count, frei_zugaenglich: .open_access.is_oa})
```

Gelesen von links nach rechts: Nimm `.result.results`, gib die Liste weiter (`|`) und baue mit `map(…)` jeden Treffer zu einem neuen Datensatz um. `titel: .display_name` heißt: Das neue Feld `titel` bekommt den Wert von `display_name`. `.open_access.is_oa` holt einen Wert aus der Ebene darunter. `//` heißt „oder, wenn leer“. jq kann sehr viel; für den Einstieg reichen diese vier Zeichen. Eine Einführung gibt es unter <https://jqlang.org/tutorial/>.

### 3.3 Type Convert: zwischen Message, JSON und Table wechseln

*Type Convert* wandelt die Eingabe in den Typ um, den ihr unter **Output Type** wählt.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Output Type** | am Baustein | *Message*, *JSON* oder *Table*. Der Ausgang ändert sich mit. |
| **Auto Parse** | *Parameters* | Erkennt JSON oder CSV, das als Text vorliegt, und macht daraus echtes JSON oder eine echte Tabelle. Standard: aus. |

Was beim Umwandeln passiert:

| Von | Nach | Ergebnis |
| --- | --- | --- |
| JSON mit einer Liste (z. B. `{"result": [ … ]}`) | Table | eine Zeile pro Listeneintrag, eine Spalte pro Feld |
| Message mit CSV-Text, *Auto Parse* an | Table | eine echte Tabelle mit den Spalten der Kopfzeile |
| Message mit CSV-Text, *Auto Parse* aus | Table | eine Tabelle mit **einer** Zeile und **einer** Spalte `text`, in der der ganze Text steht |
| Table | JSON | `{"results": [ … ]}`, ein Datensatz pro Zeile |
| Table | Message | die Tabelle als Text (Markdown-Tabelle) |

### 3.4 Data Operations mit Tabellen

Mit dem Input Type *Table* gibt es diese Operationen:

| Operation | Was sie tut | Felder |
| --- | --- | --- |
| **Filter** | behält die Zeilen, die eine Bedingung erfüllen | *Column Name*, *Filter Operator* (*equals*, *not equals*, *contains*, *not contains*, *starts with*, *ends with*, *greater than*, *less than*), *Filter Value* |
| **Sort** | sortiert nach einer Spalte | *Column Name*, *Sort Ascending* (an: aufsteigend) |
| **Select Columns** | behält nur die genannten Spalten, in dieser Reihenfolge | *Columns to Select* |
| **Drop Column** | entfernt eine Spalte | *Column Name* |
| **Rename Column** | benennt eine Spalte um | *Column Name*, *New Column Name* |
| **Add Column** | fügt eine Spalte mit demselben Wert in jeder Zeile hinzu | *New Column Name*, *New Column Value* |
| **Replace Value** | ersetzt in einer Spalte einen Wert durch einen anderen; der ganze Zellinhalt muss passen | *Column Name*, *Value to Replace*, *Replacement Value* |
| **Drop Duplicates** | entfernt Zeilen, die in einer Spalte denselben Wert haben wie eine frühere | *Column Name* (muss ausgefüllt sein) |
| **Head**, **Tail** | behält die ersten oder letzten Zeilen | *Number of Rows* (Standard: 5) |
| **Merge** | verbindet zwei Tabellen über eine gemeinsame Spalte | *Left Table*, *Right Table*, *Merge On Column*, *Merge Type* |
| **Concatenate** | hängt Tabellen untereinander | mehrere Linien an den Eingang *Table* |

**Merge** ist der wichtigste und der am wenigsten selbsterklärende. Im Flow ist die linke Tabelle die Liste der Neuerwerbungen, die rechte die Liste der Fachreferate. Für jede Zeile links sucht Merge die Zeile rechts mit demselben Wert in `fach` und hängt deren Spalten an. Der **Merge Type** legt fest, was mit Zeilen ohne Partner geschieht:

| Merge Type | Welche Zeilen bleiben |
| --- | --- |
| **left** (im Flow) | alle Zeilen der linken Tabelle; fehlt ein Partner, bleiben die neuen Spalten leer |
| **inner** | nur Zeilen, die in beiden Tabellen einen Partner haben |
| **right** | alle Zeilen der rechten Tabelle |
| **outer** | alle Zeilen beider Tabellen |

Leere Zellen erscheinen in der Tabelle als `nan` (*not a number*, so nennt die Tabellen-Bibliothek fehlende Werte).

**Reihenfolge.** Die Schritte im Flow stehen nicht zufällig in dieser Reihenfolge: Erst wird das Fach vereinheitlicht, dann verbunden. Sonst fände Merge für `informatik` kein Fachreferat, weil `informatik` und `Informatik` für den Computer verschiedene Werte sind. Übung 6 zeigt das.

### 3.5 Parser: eine Tabelle als Text

*Parser* setzt die Werte jeder Zeile in eine Vorlage ein und gibt eine Zeile Text pro Tabellenzeile aus. Im Flow:

```text
- {titel} ({autor}), Fachreferat: {fachreferat}
```

Namen in geschweiften Klammern müssen genau den Spaltennamen entsprechen. Wie ihr mit Parser Listen, Zitate, HTML und mehr erzeugt, ist Thema von [L4](L4_ergebnisse_ausgeben.md).

## 4. Übungen

🟢 Ausprobieren · 🟡 Umbauen · 🔴 Selbst bauen. Die Lösungen lassen sich aufklappen.

### 🟢 1. Ohne Auto Parse

Schaltet im Baustein **CSV als Tabelle** unter *Parameters* **Auto Parse** aus und drückt ▶. Wie sieht die Tabelle aus? Schaltet es danach wieder ein.

<details>
<summary>Lösung</summary>

Die Tabelle hat eine einzige Zeile und eine einzige Spalte `text`, in der der ganze Inhalt der Datei steht. Ohne *Auto Parse* weiß Type Convert nicht, dass der Text eine CSV-Tabelle ist, und packt ihn als Ganzes in eine Zelle. Die Bausteine danach finden dann keine Spalte `fach` und brechen ab.

</details>

### 🟢 2. Andere Suchparameter

Tragt im Baustein **Suchparameter** bei `search` `citizen science libraries` ein und bei `per-page` `10`. Drückt ▶ an **Treffer, aufgeräumt**.

<details>
<summary>Lösung</summary>

Ihr bekommt zehn Treffer zu Citizen Science. Die Leerzeichen in den Suchbegriffen sind kein Problem: *API Request* setzt die Parameter selbst korrekt in die Adresse ein (als `search=citizen+science+libraries`). Vergleicht das mit Übung 8 in [L1](L1_daten_importieren.md), wo ihr die Leerzeichen von Hand ersetzen musstet.

</details>

### 🟢 3. Filtern

Ändert im Baustein **Nur bestellte** die Bedingung und drückt jeweils ▶ an **Bestellt: Liste für die Fachreferate**:

1. *Column Name* `jahr`, *Filter Operator* *greater than*, *Filter Value* `2023`
2. *Column Name* `fach`, *Filter Operator* *equals*, *Filter Value* `informatik`
3. *Column Name* `status`, *Filter Operator* *contains*, *Filter Value* `best`

Was fällt bei 1 an *Geschichte des Buchdrucks* auf? Warum ist die Liste bei 2 leer?

<details>
<summary>Lösung</summary>

1. Sechs Titel ab 2024. *Geschichte des Buchdrucks* fehlt: Ohne Jahr ist der Wert leer, und ein leerer Wert ist weder größer noch kleiner als 2023. Wer alle sehen will, die *nicht* älter sind, verliert so Titel ohne Jahr, ohne es zu merken.
2. Der Filter unterscheidet Groß- und Kleinschreibung. `informatik` gibt es nach *Fach vereinheitlichen* nicht mehr. Mit `Informatik` erscheinen die drei Informatik-Titel.
3. *contains* sucht einen Teil des Textes. `best` passt zu `bestellt`, also dieselben drei Titel wie vorher. Vorsicht: `in` würde auch auf `in Bearbeitung` und auf alles andere passen, das `in` enthält.

</details>

### 🟢 4. Doppelte entfernen

Leert im Baustein **Doppelte entfernen** das Feld *Column Name* und drückt ▶. Tragt danach `titel` ein und dann wieder `isbn`.

<details>
<summary>Lösung</summary>

Mit leerem Feld bricht der Baustein mit einer Fehlermeldung ab (*KeyError … Index([''])*): Er braucht eine Spalte, nach der er vergleicht. Mit `titel` und mit `isbn` bleiben 14 von 15 Zeilen, weil die doppelte Zeile in beiden Spalten gleich ist. Bei echten Daten ist die ISBN die bessere Wahl: Zwei verschiedene Bücher können denselben Titel haben.

</details>

### 🟢 5. Merge Type

Stellt im Baustein **Fachreferat ergänzen** den **Merge Type** nacheinander auf *inner*, *right* und *outer* und drückt jeweils ▶ an **Neuerwerbungen, aufgeräumt**. Was passiert mit *Wissenschaftliches Schreiben*?

<details>
<summary>Lösung</summary>

Das Buch hat das Fach `Allgemein`, für das es in `fachreferate.csv` kein Fachreferat gibt.

- *left*: 14 Zeilen, *Wissenschaftliches Schreiben* steht mit `nan` bei Fachreferat und Standort da.
- *inner* und *right*: 13 Zeilen, das Buch fehlt, weil es rechts keinen Partner hat.
- *outer*: 14 Zeilen wie bei *left*, denn jedes Fach aus `fachreferate.csv` kommt in der Liste vor.

Für „ergänze Angaben, aber verliere nichts“ ist *left* richtig. *inner* ist praktisch, um gezielt nur die Zeilen zu sehen, für die es Angaben gibt, aber gefährlich, wenn man es nicht bemerkt.

</details>

### 🟡 6. Die Reihenfolge zählt

Löscht den Baustein **Fach vereinheitlichen** und verbindet **CSV als Tabelle** direkt mit **Doppelte entfernen**. Drückt ▶ an **Neuerwerbungen, aufgeräumt**. Wo steht jetzt *Datenbanken kompakt*, und was fehlt? (Danach mit Strg+Z rückgängig machen.)

<details>
<summary>Lösung</summary>

*Datenbanken kompakt* steht ganz unten, mit Fach `informatik` und `nan` bei Fachreferat und Standort. Merge findet für `informatik` keinen Partner, und Sort stellt Kleinbuchstaben hinter alle Großbuchstaben. Ein uneinheitlicher Wert verdirbt also jeden späteren Schritt, der ihn vergleicht. Deshalb gilt: erst bereinigen, dann filtern, verbinden und sortieren.

</details>

### 🟡 7. Einen einzelnen Wert herausgreifen

Wie viele Treffer hat OpenAlex insgesamt zu eurer Suche? Die Zahl steht in `.result.meta.count`.

1. Drückt ▶ an **OpenAlex fragen** und kopiert die Ausgabe.
2. Setzt einen neuen **Data Operations** auf die Arbeitsfläche, *Input Type* *JSON*, Operation *Path Selection*, und verbindet *API Response* mit seinem Eingang *JSON*.
3. Fügt die kopierte Ausgabe in **JSON to Map** ein und wählt in **Select Path** `.result.meta.count`.

<details>
<summary>Lösung</summary>

Heraus kommt eine einzelne Zahl, z. B. `{"result": 1928193}`; sie hängt von euren Suchbegriffen ab und wächst mit OpenAlex. In der Auswahl stehen alle Wege, die es im Beispiel gibt, auch `.result.results[0].display_name` für den Titel des ersten Treffers. Path Selection ist der einfachste Weg, *einen* Wert zu holen; für mehrere Werte oder für jeden Eintrag einer Liste nehmt ihr JQ.

</details>

### 🟡 8. Spalten umbenennen, ohne etwas kaputtzumachen

Die Spalte `fachreferat` soll in der Tabelle `Ansprechperson` heißen. Setzt zwischen **Nach Fach sortieren** und **Spalten auswählen** einen **Data Operations** mit *Input Type* *Table* und Operation *Rename Column* (*Column Name* `fachreferat`, *New Column Name* `Ansprechperson`). Drückt ▶ an **Neuerwerbungen, aufgeräumt**. Was meldet Langflow, und wie behebt ihr es?

<details>
<summary>Lösung</summary>

*Spalten auswählen* bricht ab: *['fachreferat'] not in index*. Die Spalte heißt nach dem Umbenennen nicht mehr `fachreferat`, aber *Columns to Select* fragt noch nach dem alten Namen. Ersetzt dort `fachreferat` durch `Ansprechperson`. Der untere Zweig (*Nur bestellte* und *Als Liste*) läuft weiter, weil er schon vor dem Umbenennen abzweigt.

Merkt euch: Jeder Baustein, der eine Spalte beim Namen nennt, hängt von allen Umbenennungen davor ab. Benennt deshalb möglichst spät um, kurz vor der Ausgabe.

</details>

### 🟡 9. Einen Nachtrag anhängen

Die Erwerbung schickt drei weitere Titel in `daten/lernpfad/neuerwerbungen_nachtrag.csv`. Hängt sie an die Liste an:

1. Einen neuen **Read File** mit dieser Datei und einen **Type Convert** (*Output Type* *Table*, *Auto Parse* an) auf die Arbeitsfläche setzen und verbinden.
2. Einen **Data Operations** mit *Input Type* *Table* und Operation *Concatenate* einfügen. Beide Tabellen (aus **CSV als Tabelle** und aus dem neuen Type Convert) mit seinem Eingang *Table* verbinden.
3. Seinen Ausgang an **Fach vereinheitlichen** anschließen, statt der alten Verbindung von **CSV als Tabelle**.

Wie viele Zeilen hat **Neuerwerbungen, aufgeräumt** jetzt?

<details>
<summary>Lösung</summary>

Concatenate hängt die 3 Zeilen unter die 15 alten: 18 Zeilen. Nach *Doppelte entfernen* bleiben 17. Concatenate braucht Tabellen mit denselben Spalten; der Nachtrag hat dieselbe Kopfzeile wie die Liste. Für Tabellen mit *verschiedenen* Spalten, die über einen gemeinsamen Wert zusammengehören, nehmt ihr Merge.

</details>

### 🔴 10. Das Jahr reparieren

In der Liste der bestellten Titel soll auch das Jahr stehen. Ändert die Vorlage von **Als Liste** zu `- {titel} ({autor}, {jahr})` und drückt ▶. Ihr seht `2024.0` und bei *Geschichte des Buchdrucks* `nan`. Repariert das so, dass `2024` und `o. J.` erscheinen.

Tipp: Data Operations mit *Table* kann das nicht, JQ schon. Ihr braucht dafür einen Umweg über JSON.

<details>
<summary>Lösung</summary>

Warum es passiert: Weil ein Jahr fehlt, speichert die Tabelle die ganze Spalte als Kommazahl, und das fehlende Jahr als *nan*.

Die Reparatur zwischen **Nur bestellte** und **Als Liste**:

1. **Type Convert** mit *Output Type* *JSON*: aus der Tabelle wird `{"results": [ … ]}`.
2. **Data Operations** mit *Input Type* *JSON*, Operation *JQ Expression*:

   ```text
   .results | map(.jahr |= (if . == null or isnan then "o. J." else (floor | tostring) end))
   ```

   `|=` ändert ein Feld an Ort und Stelle. `isnan` erkennt den fehlenden Wert, `floor` schneidet die Nachkommastellen ab, `tostring` macht Text daraus.
3. **Type Convert** mit *Output Type* *Table*, dann weiter an **Als Liste**.

Ergebnis: *Geschichte des Buchdrucks (Lange, Clara, o. J.)*. Oft ist es einfacher, den Fehler in der Quelle zu beheben, hier also das Jahr in der CSV-Datei nachzutragen. Wenn die Daten aber jeden Tag neu aus einem System kommen, gehört die Reparatur in den Flow.

</details>

### 🔴 11. Eine Katalogsuche, die eine Tabelle liefert

In [L1](L1_daten_importieren.md) (Übung 8) habt ihr den hbz-Verbundkatalog über lobid gefragt und rohes JSON bekommen. Baut daraus einen Flow, der eine Tabelle mit Titel, Jahr und Verlag liefert. Die Suchparameter heißen `q` (Suchbegriffe), `size` (Zahl der Treffer) und `format` (`json`). Die Treffer stehen in `.result.member`; in jedem Treffer steht der Titel in `title`, Jahr und Verlag in der ersten Angabe von `publication` als `startDate` und `publishedBy`.

<details>
<summary>Lösung</summary>

1. **Dynamic Create Data** mit den Feldern `q`, `size` und `format`, Werte z. B. `Umberto Eco Abschlussarbeit`, `3`, `json`.
2. **API Request** mit der URL `https://lobid.org/resources/search`, den Ausgang *JSON* von Dynamic Create Data an *Query Parameters*.
3. **Data Operations**, *JSON*, *JQ Expression*:

   ```text
   .result.member | map({titel: .title, jahr: (.publication[0].startDate // "o. J."), verlag: (.publication[0].publishedBy[0] // "")})
   ```

   `[0]` nimmt den ersten Eintrag einer Liste.
4. **Type Convert** auf *Table*, dann **Chat Output**.

Ergebnis: eine Tabelle mit Ausgaben von *Wie man eine wissenschaftliche Abschlußarbeit schreibt*, mit Jahr und Verlag. Soll die Suche aus dem Playground kommen, verbindet ihr einen **Chat Input** mit dem Eingang `q`.

</details>

## 5. Wann nehme ich was?

| Ihr wollt … | Baustein und Einstellung | Hinweis |
| --- | --- | --- |
| einen einzelnen Wert aus JSON | Data Operations, *Path Selection* | Am bequemsten: Beispiel einfügen, Weg auswählen |
| einige Felder der obersten Ebene behalten oder loswerden | Data Operations, *Select Keys* / *Remove Keys* | Wirkt nur auf die oberste Ebene, nicht auf die Treffer in einer Liste |
| jeden Eintrag einer Liste umbauen, verschachtelte Felder auflösen, Werte reparieren | Data Operations, *JQ Expression* | Mächtig, aber eine eigene kleine Sprache; ausprobieren mit ▶ |
| aus CSV-Text eine Tabelle | Type Convert, *Table*, *Auto Parse* an | Ohne Auto Parse: eine einzige Zelle |
| aus JSON eine Tabelle | Type Convert, *Table* | Das JSON muss eine Liste enthalten |
| Zeilen auswählen, sortieren, Spalten wählen | Data Operations, *Table* | Achtet auf Groß- und Kleinschreibung |
| zwei Tabellen über eine gemeinsame Spalte verbinden | Data Operations, *Merge* | *left*, wenn keine Zeile verloren gehen soll |
| zwei Tabellen mit gleichen Spalten untereinander | Data Operations, *Concatenate* | Spaltennamen müssen gleich sein |
| Parameter für einen Webdienst | Dynamic Create Data → *Query Parameters* | Statt die Adresse von Hand zu bauen |
| eine Tabelle als Text mit eigener Form | Parser | mehr in [L4](L4_ergebnisse_ausgeben.md) |
| eine Tabelle als Text, ohne Vorlage | Type Convert, *Message* | ergibt eine Markdown-Tabelle |

Und wann braucht ihr dafür eine KI? Fast nie. Alles in diesem Modul läuft ohne Sprachmodell: schneller, kostenlos, und jedes Mal mit demselben Ergebnis. Eine KI lohnt sich erst, wenn die Daten keine feste Form haben, z. B. freier Text ([L6](L6_strukturierte_antworten.md)).

## 6. Wenn etwas nicht klappt

| Meldung oder Problem | Ursache und Lösung |
| --- | --- |
| *No files to process* | In einem der beiden *Read File* fehlt die Datei. |
| Die Tabelle hat nur eine Spalte `text` | Bei *Type Convert* ist *Auto Parse* aus. |
| *KeyError … Index([''])* | Bei einer Tabellen-Operation ist *Column Name* leer, z. B. bei *Drop Duplicates*. |
| *KeyError* mit einem Spaltennamen, z. B. *KeyError: fach* | Die Spalte gibt es in der Tabelle nicht. Oft ist *Auto Parse* aus, und die Tabelle hat nur die Spalte `text`. |
| *['…'] not in index* | Eine Spalte mit diesem Namen gibt es nicht (mehr). Tippfehler? Wurde sie vorher umbenannt oder entfernt? |
| Der Filter findet nichts | Groß- und Kleinschreibung, Leerzeichen am Rand, oder eine Zahl in einer Textspalte. Mit ▶ am Baustein davor nachsehen, was wirklich in der Spalte steht. |
| `nan` in der Tabelle | Ein Wert fehlt: in der Quelle oder weil Merge keinen Partner gefunden hat. |
| Jahre erscheinen als `2024.0` | In der Spalte fehlt mindestens ein Wert. Siehe Übung 10. |
| Das Feld *Select Path* ist leer | Bei *Path Selection* erst in *JSON to Map* ein Beispiel einfügen. |
| Bei OpenAlex steht in `meta` ein Hinweis auf einen API-Schlüssel | Ohne Schlüssel teilen sich alle im selben Netz ein tägliches Kontingent. Siehe [Anleitung für Teilnehmende](../01_teilnehmende.md#23-zugangsdaten-eintragen). |

**Weiter:** [L4 Ergebnisse ausgeben](L4_ergebnisse_ausgeben.md) zeigt, wie ihr eure Tabellen als Liste, Zitate, HTML oder Datei ausgebt.
