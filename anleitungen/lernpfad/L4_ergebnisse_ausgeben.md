# L4 Ergebnisse ausgeben

Am Ende eines Flows steht ein Ergebnis, mit dem jemand weiterarbeitet: eine Literaturliste für ein Handout, ein Stück HTML für die Webseite der Bibliothek, eine Excel-Datei für die Erwerbung. Die Daten dafür sind oft schon da, nur in der falschen Form. Dieser Flow nimmt eine einzige Tabelle, die Neuerwerbungen einer Bibliothek, und gibt sie auf sechs Wegen aus. Dafür braucht es keine KI: Vorlagen reichen.

| | |
| --- | --- |
| **Ihr lernt** | Mit Vorlagen aus jeder Tabellenzeile eine Textzeile machen, Zeilen zu einer ganzen Seite zusammensetzen, mehrere Ergebnisse im Playground zeigen und Ergebnisse als Datei speichern. |
| **Bausteine** | Parser, Prompt Template (ohne Modell), Chat Output, Write File, dazu Read File, Data Operations und Type Convert zum Vorbereiten |
| **KI** | keine |
| **Dauer** | etwa 45 Minuten |
| **Testdaten** | `daten/lernpfad/neuerwerbungen.csv` |

## Inhalt

1. [Der Flow im Überblick](#1-der-flow-im-überblick)
2. [Vorbereiten](#2-vorbereiten)
3. [Schritt für Schritt](#3-schritt-für-schritt)
4. [Übungen](#4-übungen)
5. [Wann nehme ich was?](#5-wann-nehme-ich-was)
6. [Wenn etwas nicht klappt](#6-wenn-etwas-nicht-klappt)

## 1. Der Flow im Überblick

Links wird die Tabelle vorbereitet, rechts wird sie ausgegeben.

**Vorbereiten** (links, drei Bausteine):

1. **Neuerwerbungen lesen (Read File)** liest die CSV-Datei als Text.
2. **Leere Felder füllen (Data Operations)** ersetzt ein leeres Feld durch `o. J.` (ohne Jahr). Warum das nötig ist, steht in [Abschnitt 3.1](#31-vorbereiten-aus-der-datei-wird-eine-tabelle).
3. **Als Tabelle (Type Convert)** macht aus dem Text eine echte Tabelle mit Zeilen und Spalten.

**Ausgeben** (rechts, sechs Zeilen):

| Zeile | Bausteine | Was herauskommt |
| --- | --- | --- |
| 1 | Chat Output | die Tabelle, wie sie ist |
| 2 | Parser → Chat Output | eine Zitierliste: `Berger, Anna (2024). Grundlagen der Informationskompetenz. Verlag Lesezeichen.` |
| 3 | Parser → Chat Output | eine Markdown-Liste mit fetten Titeln |
| 4 | Parser → Prompt Template → Chat Output | eine HTML-Tabelle mit Überschrift, fertig für den Editor einer Webseite |
| 5 | Parser (Stringify) → Chat Output | die ganze Tabelle als Text |
| 6 | Write File → Chat Output | eine Excel-Datei und die Meldung, wo sie liegt |

Alle sechs Zeilen hängen an derselben Tabelle. Ein Ausgang darf mit beliebig vielen Eingängen verbunden sein.

## 2. Vorbereiten

1. In der Übersicht von Langflow beim Flow **L4 Ergebnisse ausgeben** auf die drei Punkte klicken → *Duplicate*. Arbeitet in der Kopie.
2. Im Baustein **Neuerwerbungen lesen (Read File)** auf **Select files** klicken und `daten/lernpfad/neuerwerbungen.csv` hochladen.
3. Oben rechts auf **Playground** klicken, irgendetwas eintippen (z. B. *los*) und abschicken. Es erscheinen sechs Nachrichten; der Name über jeder Nachricht sagt, aus welcher Zeile sie kommt.

Wie in [L1](L1_daten_importieren.md) könnt ihr jeden Baustein auch einzeln mit **▶** ausführen und am Ausgang nachsehen, was er weitergibt. Bei den Parsern ist das der schnellste Weg, eine Vorlage auszuprobieren.

## 3. Schritt für Schritt

### 3.1 Vorbereiten: aus der Datei wird eine Tabelle

Wie eine CSV-Datei zur Tabelle wird, zeigt [L3](L3_tabellen_und_json.md) ausführlich. Hier nur so viel:

**Type Convert** mit *Output Type* **Table** und eingeschaltetem *Auto Parse* (*Parameters*) erkennt, dass der Text eine CSV-Tabelle ist, und macht Zeilen und Spalten daraus.

**Leere Felder füllen** ist ein *Data Operations* mit der Operation **Text Replace**: Er ersetzt im Text `,,` durch `,o. J.,`. In der Datei fehlt bei einem Buch das Jahr; dort stehen zwei Kommas direkt nebeneinander. Ohne diesen Schritt passiert Folgendes: Type Convert sieht in der Spalte *jahr* lauter Zahlen und eine Lücke, und behandelt die ganze Spalte als Kommazahlen. Aus *2024* wird `2024.0`, aus der Lücke `nan` (*not a number*). In einer Zitierliste sieht das so aus:

```text
Berger, Anna (2024.0). Grundlagen der Informationskompetenz. Verlag Lesezeichen.
Lange, Clara (nan). Geschichte des Buchdrucks. Verlag Lesezeichen.
```

Steht in der Spalte dagegen ein Wort wie `o. J.`, bleibt die ganze Spalte Text, und die Jahre bleiben, wie sie in der Datei stehen. Das probiert ihr in Übung 2 aus.

### 3.2 Parser: aus jeder Zeile eine Textzeile

*Parser* ist der wichtigste Baustein dieses Moduls. Er nimmt eine Tabelle (oder JSON) und eine **Vorlage**. Für jede Tabellenzeile setzt er die Werte in die Vorlage ein: `{titel}` wird durch den Wert der Spalte *titel* ersetzt, `{jahr}` durch den der Spalte *jahr*. Alles andere in der Vorlage bleibt, wie es ist. Am Ende stehen die Zeilen untereinander, als eine einzige Message.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Mode** | am Baustein | *Parser*: die Vorlage anwenden. *Stringify*: die ganze Tabelle unverändert in Text umwandeln, ohne Vorlage. |
| **Template** | am Baustein | Die Vorlage. Namen in geschweiften Klammern müssen genau so heißen wie die Spalten, auch bei Groß- und Kleinschreibung. |
| **Separator** | *Parameters* | Was zwischen den Zeilen steht. Standard: ein Zeilenumbruch. `\n\n` ergibt eine Leerzeile zwischen den Einträgen, ` \| ` alles in einer Zeile. |

Die drei Parser im Flow nutzen diese Vorlagen:

| Parser | Vorlage | Ergebnis (erste Zeile) |
| --- | --- | --- |
| Zitierliste | `{autor} ({jahr}). {titel}. {verlag}.` | `Berger, Anna (2024). Grundlagen der Informationskompetenz. Verlag Lesezeichen.` |
| Markdown-Liste | `- **{titel}** von {autor} ({fach}, {status})` | `- **Grundlagen der Informationskompetenz** von Berger, Anna (Bibliothekswissenschaft, bestellt)` |
| HTML-Tabellenzeilen | `<tr><td>{titel}</td><td>{autor}</td><td>{jahr}</td><td>{status}</td></tr>` | `<tr><td>Grundlagen der Informationskompetenz</td>…</tr>` |

Im Playground erscheint die Markdown-Liste als echte Liste mit fetten Titeln: Der Chat versteht Markdown. In ein Word-Dokument oder eine E-Mail könnt ihr den Text kopieren; dort braucht ihr die `**` dann nicht.

**Zahlen formatieren.** In der Vorlage dürft ihr hinter den Spaltennamen ein Format schreiben: `{preis_eur:.2f}` zeigt einen Preis immer mit zwei Nachkommastellen (`29.90`), `{jahr:.0f}` eine Kommazahl ohne Nachkommastellen (`2024` statt `2024.0`). Das funktioniert nur, wenn die Spalte wirklich Zahlen enthält; steht dort Text, meldet der Parser einen Fehler.

**Stringify.** Der Parser *Alles als Text* steht im Mode *Stringify*. Er braucht keine Vorlage und gibt die ganze Tabelle als Text in Tabellenform aus, mit Kopfzeile. Das ist praktisch, wenn ihr eine kleine Tabelle vollständig an einen Prompt weitergeben wollt ([L5](L5_prompts_und_modelle.md)). Bei großen Tabellen wird der Text sehr lang.

### 3.3 Prompt Template ohne Modell: Zeilen zu einer Seite zusammensetzen

Der Parser macht aus jeder Zeile eine Tabellenzeile in HTML. Für eine fertige Seite fehlen Überschrift, Tabellenkopf und der Rahmen `<table>…</table>`. Das erledigt ein **Prompt Template**, obwohl kein Sprachmodell im Spiel ist.

Ein Prompt Template tut nichts anderes, als Text in Platzhalter einzusetzen. Sein Ausgang ist eine ganz normale Message. Ob sie an ein Modell geht oder direkt an einen Chat Output, ist ihm egal. Die Vorlage im Flow:

```html
<h2>Neuerwerbungen</h2>
<p>Diese Titel hat die Bibliothek neu bestellt oder eingestellt.</p>
<table>
  <thead>
    <tr><th>Titel</th><th>Autor:in</th><th>Jahr</th><th>Status</th></tr>
  </thead>
  <tbody>
{zeilen}
  </tbody>
</table>
```

Der Platzhalter `{zeilen}` erzeugt links am Baustein einen Eingang *zeilen*, an dem der Parser hängt.

| | Parser | Prompt Template |
| --- | --- | --- |
| Bekommt | eine Tabelle oder JSON | einen oder mehrere Texte (Messages) |
| Vorlage gilt für | jede Zeile einzeln | den ganzen Text, einmal |
| Platzhalter | die Spaltennamen | frei gewählte Namen, jeder wird ein Eingang |

Die beiden ergänzen sich: Der Parser macht die Zeilen, das Prompt Template den Rahmen. Flow 05 *Schulungsplanung* baut so den Quellcode für die Lernplattform.

**Achtung bei geschweiften Klammern.** Das Prompt Template hält jedes Paar `{ }` für einen Platzhalter. CSS-Stilangaben wie `<style>td { padding: 4px; }</style>` lehnt es deshalb ab (*Input variables contain invalid characters*). Schreibt Stilangaben direkt in die Tags, z. B. `<td style="padding: 4px;">`.

### 3.4 Chat Output: Ergebnisse im Playground zeigen

Jeder *Chat Output* erscheint im Playground als eigene Nachricht. Er nimmt Messages, Tabellen und JSON: Tabellen zeigt er als Tabelle, JSON als Code-Block.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Sender Name** | *Parameters* | Der Name über der Nachricht. Standard: *AI*. Im Flow trägt jeder Chat Output einen eigenen Namen, damit ihr die sechs Nachrichten unterscheiden könnt. |
| **Store Messages** | *Parameters* | Die Nachricht im Chatverlauf speichern. Standard: an. Ausgeschaltet wird sie nicht gespeichert; Bausteine wie *Message History* ([L5](L5_prompts_und_modelle.md)) finden sie dann später nicht. |
| **Data Template**, **Basic Clean Data** | *Parameters* | Sollen festlegen, wie JSON und Tabellen in Text umgewandelt werden. In Langflow 1.12.3 haben sie bei einem einzelnen angeschlossenen Baustein keine Wirkung. Wollt ihr JSON oder eine Tabelle anders darstellen, setzt einen **Parser** davor. |

Ein Chat Output hat auch einen Ausgang (*Output Message*): derselbe Inhalt noch einmal, falls ihr ihn weitergeben wollt, z. B. an Write File.

### 3.5 Write File: Ergebnisse als Datei speichern

*Write File* speichert, was an seinem Eingang ankommt, als Datei. Welche Formate erlaubt sind, hängt davon ab, **was** ankommt:

| Am Eingang kommt an | Erlaubte Formate |
| --- | --- |
| eine Tabelle (Table) | *csv*, *excel*, *json*, *markdown* |
| ein Text (Message), z. B. aus einem Parser | *txt*, *html*, *json*, *markdown* |

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **File Name** | am Baustein | Name ohne Endung, z. B. `neuerwerbungen_aufbereitet`. Die Endung kommt vom Format. Nur ein Name, keine Ordner. |
| **File Format** | am Baustein | Das Format, siehe oben. *excel* ergibt eine `.xlsx`-Datei. |
| **Append** | am Baustein | An eine vorhandene Datei gleichen Namens anhängen, statt sie zu ersetzen. Funktioniert für Textformate (csv, json, markdown, txt, html), nicht für Excel. |

Der Ausgang **File Path** meldet, wo die Datei liegt, z. B. `DataFrame saved successfully as '/app/langflow/…/neuerwerbungen_aufbereitet.xlsx'`.

**Wo ist die Datei?** Sie liegt nicht in eurem Projektordner, sondern im Speicher von Langflow, und Langflow trägt sie in eure Dateiliste ein. Ihr findet sie in der Übersicht von Langflow unter **My Files** und könnt sie dort herunterladen. Das gilt auch auf der gemeinsamen Instanz; dort sieht jede Gruppe nur ihre eigenen Dateien. Wer Langflow auf dem eigenen Laptop betreibt, kann die Datei auch im Terminal im Projektordner herauskopieren, mit dem Pfad aus der Meldung:

```bash
docker compose cp "langflow:/app/langflow/…/neuerwerbungen_aufbereitet.xlsx" .
```

**Jeder Lauf ist ein neuer Eintrag.** Die Datei auf dem Server wird bei jedem Lauf überschrieben (oder ergänzt, mit *Append*). In *My Files* legt Langflow dagegen jedes Mal einen neuen Eintrag an: `neuerwerbungen_aufbereitet`, dann `neuerwerbungen_aufbereitet (1)`, `(2)` und so weiter. Die neueste Fassung hat die höchste Nummer. Alte Einträge könnt ihr dort löschen.

## 4. Übungen

🟢 Ausprobieren · 🟡 Umbauen · 🔴 Selbst bauen. Die Lösungen lassen sich aufklappen. Drückt nach jeder Änderung ▶ am geänderten Baustein oder an seinem Chat Output.

### 🟢 1. Ein anderer Zitierstil

Ändert die Vorlage im Parser *Zitierliste* so, dass der Titel kursiv erscheint und der Verlag vor dem Jahr steht:

```text
{autor}: *{titel}*. {verlag}, {jahr}.
```

Schreibt dann absichtlich `{Titel}` mit großem T und drückt ▶. Was meldet der Parser?

<details>
<summary>Lösung</summary>

Die Liste sieht jetzt so aus: `Berger, Anna: *Grundlagen der Informationskompetenz*. Verlag Lesezeichen, 2024.` Im Playground erscheint der Titel kursiv, weil `*…*` in Markdown kursiv bedeutet (`**…**` fett).

Mit `{Titel}` bricht der Parser ab, und als Fehlermeldung steht nur das Wort `Titel`. Gemeint ist: Eine Spalte mit diesem Namen gibt es nicht. Spaltennamen müssen genau stimmen, auch bei der Groß- und Kleinschreibung. Die Spaltennamen stehen in der ersten Zeile der CSV-Datei, oder ihr seht sie in der Tabelle am Ausgang von *Als Tabelle*.

</details>

### 🟢 2. Ohne Lückenfüller

Verbindet den Ausgang von *Neuerwerbungen lesen* direkt mit dem Eingang von *Als Tabelle*, sodass *Leere Felder füllen* übersprungen wird. Seht euch die Zitierliste und die HTML-Zeilen an. Stellt die Verbindung danach wieder her.

<details>
<summary>Lösung</summary>

Alle Jahre erscheinen als `2024.0`, `2023.0` usw., und bei *Geschichte des Buchdrucks* steht `nan`. Type Convert hat die Spalte *jahr* als Kommazahlen gelesen, weil sie bis auf eine Lücke nur Zahlen enthält; eine Lücke in einer Zahlenspalte heißt `nan`.

Zwei Wege führen zu sauberen Jahren: die Lücke vorher mit Text füllen, wie im Flow, oder im Parser `{jahr:.0f}` schreiben. Der zweite Weg macht aus `2024.0` wieder `2024`, aus der Lücke aber weiterhin `nan`. Den Weg im Flow solltet ihr euch merken: Leere Felder lohnt es sich zu füllen, bevor eine Tabelle entsteht.

</details>

### 🟢 3. Trennzeichen zwischen den Einträgen

Öffnet beim Parser *Zitierliste* die *Parameters* und setzt den **Separator** nacheinander auf:

- `\n\n`
- ` | ` (Leerzeichen, senkrechter Strich, Leerzeichen)
- `; `

<details>
<summary>Lösung</summary>

`\n\n` setzt eine Leerzeile zwischen die Einträge; im Playground erscheint dann jede Angabe als eigener Absatz. ` | ` und `; ` schreiben alle Einträge in eine einzige lange Zeile, getrennt durch das Zeichen. Das ist nützlich, wenn das Ergebnis in ein einzelnes Feld passen muss, z. B. eine Liste von Titeln in einer Betreffzeile oder in einer Tabellenzelle.

</details>

### 🟢 4. Andere Dateiformate

Ändert im Baustein *Als Excel speichern (Write File)* das **File Format** nacheinander auf *csv*, *json* und *markdown*, und dann auf *txt*. Drückt jeweils ▶ und schaut in **My Files** nach.

<details>
<summary>Lösung</summary>

*csv*, *json* und *markdown* funktionieren; in *My Files* erscheint jedes Mal ein neuer Eintrag. Die CSV-Datei öffnet sich in Excel, die JSON-Datei enthält eine Liste mit einem Datensatz pro Buch, die Markdown-Datei eine Tabelle in Markdown-Schreibweise.

Bei *txt* bricht der Baustein ab: *Invalid file format 'txt' for DataFrame. Allowed: ['csv', 'excel', 'json', 'markdown']*. Am Eingang hängt eine Tabelle, und Tabellen lassen sich nicht als einfacher Text speichern. Wer eine Textdatei will, setzt einen Parser davor (Übung 5).

</details>

### 🟢 5. Eine Literaturliste als Textdatei, Stück für Stück

1. Zieht einen zweiten **Write File** auf die Arbeitsfläche und verbindet den Ausgang des Parsers *Zitierliste* mit seinem Eingang *File Content*.
2. *File Name* `literaturliste`, *File Format* *txt*, **Append** an.
3. Drückt zweimal hintereinander ▶ und schaut euch in *My Files* die Einträge an.

<details>
<summary>Lösung</summary>

Diesmal klappt *txt*, weil der Parser einen Text liefert. Nach dem ersten Lauf steht die Liste einmal in der Datei, nach dem zweiten zweimal hintereinander: *Append* hängt an, statt zu ersetzen. In *My Files* gibt es zwei Einträge, `literaturliste` mit der einfachen und `literaturliste (1)` mit der doppelten Liste.

*Append* ist richtig für Protokolle: Jeder Lauf ergänzt eine Zeile, z. B. das Datum und das Ergebnis einer Prüfung. Für eine Liste, die bei jedem Lauf neu entsteht, schaltet ihr es aus.

Speichert ihr einen Text als *markdown*, schreibt Write File in Langflow 1.12.3 die Zeile `**Message:**` an den Anfang der Datei. Bei *txt* und *html* kommt der Text unverändert in die Datei.

</details>

### 🟢 6. Namen und Gedächtnis des Chat Outputs

Öffnet beim Chat Output *Zitierliste* die *Parameters*:

1. Setzt **Sender Name** auf `Literaturliste für das Handout` und startet den Playground neu.
2. Schaltet **Store Messages** aus. Wozu könnte das gut sein?

<details>
<summary>Lösung</summary>

1. Über der Nachricht steht jetzt der neue Name. Bei Flows mit mehreren Ausgaben ist das der einfachste Weg, den Überblick zu behalten.
2. Die Nachricht wird nicht mehr im Chatverlauf gespeichert. Das ist sinnvoll für Zwischenergebnisse oder lange Tabellen, die ein Chat mit Gedächtnis ([L5](L5_prompts_und_modelle.md)) nicht immer wieder mitlesen soll, und für Inhalte, die nicht gespeichert werden sollen, z. B. personenbezogene Daten.

</details>

### 🟡 7. Preise mit zwei Nachkommastellen

Baut einen neuen Parser mit Chat Output, der für jedes Buch eine Zeile für die Erwerbung ausgibt:

```text
Grundlagen der Informationskompetenz (Verlag Lesezeichen): 29.90 EUR, 212 Seiten
```

Probiert zuerst `{preis_eur} EUR` und dann `{preis_eur:.2f} EUR`. Was ändert sich beim Buch *Open Science in der Hochschule*?

<details>
<summary>Lösung</summary>

Vorlage: `{titel} ({verlag}): {preis_eur:.2f} EUR, {seiten} Seiten`, Eingang an den Ausgang von *Als Tabelle*.

Ohne Format zeigt der Parser die Zahl so, wie Type Convert sie gelesen hat: `29.9` statt `29.90` und `0.0` statt `0.00`. Mit `:.2f` stehen immer zwei Nachkommastellen da. Das Format schreibt einen Punkt, kein Komma; für deutsche Preise müsstet ihr den Punkt danach ersetzen (*Text Replace*, siehe [L2](L2_texte_aufbereiten.md)).

</details>

### 🟡 8. Eine Spalte mehr in der HTML-Tabelle

Die HTML-Tabelle soll zusätzlich den **Verlag** zeigen. Was müsst ihr an welchen zwei Bausteinen ändern? Probiert danach, im Prompt Template oben `<style>td { padding: 4px; }</style>` einzufügen.

<details>
<summary>Lösung</summary>

1. Im Prompt Template *HTML-Seite* den Tabellenkopf ergänzen: `<th>Verlag</th>`.
2. Im Parser *HTML-Tabellenzeilen* an derselben Stelle `<td>{verlag}</td>` einfügen.

Kopf und Zeilen müssen dieselbe Zahl Spalten in derselben Reihenfolge haben, sonst verrutscht die Tabelle.

Die `<style>`-Zeile lehnt das Prompt Template ab: Es hält `{ padding: 4px; }` für einen Platzhalter mit ungültigem Namen. Schreibt die Stilangabe stattdessen in den Parser, direkt an jede Zelle: `<td style="padding: 4px;">{titel}</td>`. So macht es auch Flow 05.

</details>

### 🔴 9. Eine Leseliste als HTML-Datei

Baut einen Flow, der aus den Neuerwerbungen eine HTML-Datei mit einer Aufzählung macht, z. B. für einen Newsletter:

```html
<h2>Neu in der Bibliothek</h2>
<ul>
  <li><strong>Grundlagen der Informationskompetenz</strong>, Berger, Anna (2024)</li>
  …
</ul>
```

Die Datei soll `leseliste.html` heißen und sich in *My Files* herunterladen lassen. Den Teil links (Read File bis Type Convert) dürft ihr aus diesem Flow kopieren: Bausteine markieren, `Strg + C` und `Strg + V`.

<details>
<summary>Lösung</summary>

**Read File** → **Data Operations** (*Text Replace*, `,,` → `,o. J.,`) → **Type Convert** (*Table*, *Auto Parse* an) → **Parser** mit der Vorlage `  <li><strong>{titel}</strong>, {autor} ({jahr})</li>` → **Prompt Template** mit

```html
<h2>Neu in der Bibliothek</h2>
<ul>
{punkte}
</ul>
```

→ **Write File** mit *File Name* `leseliste` und *File Format* *html*. Zur Kontrolle einen **Chat Output** an den Ausgang des Prompt Templates hängen.

*html* ist hier erlaubt, weil am Eingang von Write File ein Text ankommt, keine Tabelle. Die heruntergeladene Datei öffnet sich im Browser als Liste.

</details>

## 5. Wann nehme ich was?

| Ihr wollt … | Baustein | Hinweis |
| --- | --- | --- |
| aus jeder Tabellenzeile eine Textzeile nach festem Muster machen | **Parser** (*Parser*) | Spaltennamen in `{ }`, genau geschrieben |
| eine kleine Tabelle vollständig als Text weitergeben | **Parser** (*Stringify*) | Bei großen Tabellen wird der Text sehr lang |
| mehrere Texte zu einem zusammensetzen oder einen Rahmen um einen Text legen | **Prompt Template** | Funktioniert auch ohne Modell; keine `{ }` außer Platzhaltern |
| ein Ergebnis anschauen und kopieren | **Chat Output** | Pro Ergebnis einer, mit eigenem *Sender Name* |
| eine Tabelle für Excel | **Write File** (*excel* oder *csv*) | Datei in *My Files* |
| eine Liste, ein Protokoll oder HTML als Datei | **Parser** → **Write File** (*txt*, *html*, *markdown*) | Für Protokolle *Append* an |
| einen Text frei umformulieren, zusammenfassen oder übersetzen | ein Sprachmodell | Ab [L5](L5_prompts_und_modelle.md). Für feste Muster ist der Parser schneller, kostenlos und macht keine Fehler. |

Die letzte Zeile ist die wichtigste: Alles, was einem festen Muster folgt, gehört in einen Parser oder ein Prompt Template ohne Modell. Ein Sprachmodell lohnt sich erst, wenn der Text nicht vorhersehbar ist.

## 6. Wenn etwas nicht klappt

| Meldung oder Problem | Ursache und Lösung |
| --- | --- |
| *No files to process* | In *Read File* ist keine Datei hochgeladen. Mit *Select files* `daten/lernpfad/neuerwerbungen.csv` wählen. |
| Der Parser meldet nur ein einzelnes Wort, z. B. `Titel` | Diese Spalte gibt es nicht. Spaltennamen in der Vorlage genau so schreiben wie in der Kopfzeile der Datei. |
| `2024.0` und `nan` statt Jahreszahlen | Die Spalte wurde als Kommazahlen gelesen, weil ein Wert fehlt. Lücken vorher füllen (Übung 2) oder `{jahr:.0f}` schreiben. |
| *Unknown format code 'f' for object of type 'str'* oder ähnlich | Ein Zahlenformat wie `:.2f` steht an einer Spalte, die Text enthält. Format entfernen. |
| *Input variables contain invalid characters or formats* | Im Prompt Template stehen geschweifte Klammern, die kein Platzhalter sind, z. B. CSS. Stilangaben in die Tags schreiben (Übung 8). |
| *Invalid file format 'txt' for DataFrame* | Write File bekommt eine Tabelle. Tabellen nur als csv, excel, json oder markdown speichern, oder einen Parser davorsetzen. |
| Die Datei ist nicht im Projektordner | Write File speichert im Speicher von Langflow. Unter *My Files* herunterladen oder mit `docker compose cp` kopieren. |
| In *My Files* gibt es viele Einträge mit Nummern | Jeder Lauf legt einen neuen Eintrag an. Der mit der höchsten Nummer ist der neueste. |

**Weiter:** [L5 Prompts und Modelle](L5_prompts_und_modelle.md). Ab dort kommt das Sprachmodell dazu, und ihr seht, wann es mehr kann als eine Vorlage.
