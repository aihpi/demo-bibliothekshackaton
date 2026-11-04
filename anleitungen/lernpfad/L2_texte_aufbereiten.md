# L2 Texte aufbereiten

Text, der aus einem PDF, einer Webseite oder einem Katalog kommt, ist selten sauber. Wörter sind am Zeilenende getrennt, Sätze an willkürlichen Stellen umbrochen, Kopfzeilen und Seitenzahlen stehen mitten im Absatz, und zwischen den Wörtern sind doppelte Leerzeichen. Bevor ihr so einen Text weitergebt, an einen Webdienst oder später an ein Sprachmodell, lohnt es sich, ihn aufzuräumen, die wichtigen Stellen herauszuziehen und ihn in handliche Stücke zu zerlegen. Genau das zeigt dieser Flow, ganz ohne KI.

| | |
| --- | --- |
| **Ihr lernt** | Text mit Regeln säubern, Muster wie DOIs herausziehen, Text zählen, kürzen und verbinden, Text in Stücke zerlegen, aus Text eine Tabelle machen und umgekehrt. |
| **Bausteine** | Data Operations (Input Type *Text*), Split Text, Type Convert, Read File, Chat Output |
| **KI** | keine |
| **Dauer** | etwa 45 Minuten |
| **Testdaten** | `daten/lernpfad/text_aus_pdf.txt`, `daten/lernpfad/benutzungsordnung.txt`, für Übung 8 `daten/lernpfad/neuerwerbungen.csv` |
| **Vorher** | [L1 Daten importieren](L1_daten_importieren.md), vor allem das Arbeiten mit **▶** |

## Inhalt

1. [Der Flow im Überblick](#1-der-flow-im-überblick)
2. [Vorbereiten](#2-vorbereiten)
3. [Schritt für Schritt](#3-schritt-für-schritt)
4. [Übungen](#4-übungen)
5. [Wann nehme ich was?](#5-wann-nehme-ich-was)
6. [Wenn etwas nicht klappt](#6-wenn-etwas-nicht-klappt)

## 1. Der Flow im Überblick

Der Flow hat drei Bereiche:

| Bereich | Was passiert | Bausteine |
| --- | --- | --- |
| **Oben: einen Text säubern** | Ein Text, wie er aus einem PDF kopiert wurde, läuft durch vier Schritte: Silbentrennung entfernen, Kopfzeilen entfernen, Zeilen zusammenführen, Leerzeichen säubern. Zwei Abzweige ziehen die DOIs heraus und zählen die Wörter. | Read File, sechsmal Data Operations |
| **Mitte: einen Text zerlegen** | Die Benutzungsordnung wird an den Leerzeilen in Abschnitte zerlegt. Das Ergebnis ist eine Tabelle; Type Convert macht daraus wieder Text. | Read File, Split Text, Type Convert |
| **Unten: aus Text eine Tabelle machen** | Eine Liste von Zeitschriften, wie sie aus einer E-Mail kopiert wird, Spalten durch `\|` getrennt, wird zur echten Tabelle. Der Text steht direkt im Baustein, hier braucht ihr keine Datei. | Data Operations |

Die meiste Arbeit erledigt **Data Operations**. Er ist ein Werkzeugkasten: Ihr wählt, welche Art von Daten ihr habt (*Input Type*), und dann eine Operation. In diesem Modul ist der Input Type immer *Text*; die Operationen für JSON und Tabellen kommen in [L3](L3_tabellen_und_json.md). Jeder Data-Operations-Baustein im Flow trägt einen Titel, der sagt, welche Operation er ausführt.

## 2. Vorbereiten

1. In der Übersicht beim Flow **L2 Texte aufbereiten** auf die drei Punkte klicken → *Duplicate*. Arbeitet in der Kopie.
2. Im Baustein **Text aus dem PDF (Read File)** die Datei `daten/lernpfad/text_aus_pdf.txt` hochladen, im Baustein **Benutzungsordnung (Read File)** die Datei `daten/lernpfad/benutzungsordnung.txt`.
3. **Playground** öffnen, irgendetwas abschicken. Es erscheinen sechs Nachrichten.

Öffnet die Datei `text_aus_pdf.txt` auch einmal in einem Texteditor. Dann seht ihr, womit der Flow es zu tun hat: getrennte Wörter wie `Biblio-` / `theken`, Zeilen, die mitten im Satz enden, die Kopfzeile *Bibliotheksforum 12 (2025) … Seite 15* mitten im Text, doppelte Leerzeichen.

Am meisten lernt ihr, wenn ihr die Kette **Schritt für Schritt** ausführt: ▶ an *1 Silbentrennung entfernen*, Ausgabe ansehen, dann ▶ an *2 Kopfzeilen entfernen* und so weiter.

## 3. Schritt für Schritt

### 3.1 Data Operations: Text ersetzen (Text Replace)

*Text Replace* sucht eine Zeichenfolge und ersetzt sie. Drei der vier Säuberungsschritte oben sind *Text Replace*.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Search Pattern** | am Baustein | Was gesucht wird |
| **Replacement Text** | am Baustein | Wodurch es ersetzt wird. Leer lassen, um das Gefundene zu löschen. |
| **Use Regex** | am Baustein | Aus: genau diese Zeichen suchen. An: *Search Pattern* ist ein **Suchmuster** (ein regulärer Ausdruck), siehe unten. |

`\n` steht in beiden Feldern für einen Zeilenumbruch, auch ohne *Use Regex*.

**Suchmuster (reguläre Ausdrücke)** beschreiben nicht einen bestimmten Text, sondern eine Form von Text. Die wichtigsten Zeichen:

| Zeichen | Bedeutung | Beispiel |
| --- | --- | --- |
| `\d` | eine Ziffer | `Seite \d+` findet *Seite 14*, *Seite 15* |
| `+` | das Vorige ein- oder mehrmals | `\d+` findet *14*, *2025* |
| `*` | das Vorige beliebig oft, auch keinmal | `\s*` findet nichts, ein oder viele Leerzeichen |
| `\s` | ein Leerzeichen, Tabulator oder Zeilenumbruch | |
| `\w` | ein Buchstabe, eine Ziffer oder `_` | |
| `.` | ein beliebiges Zeichen | |
| `\.` `\(` `\)` | der Punkt, die Klammer selbst | `\(2025\)` findet *(2025)* |
| `[…]` | eines der Zeichen in der Klammer | `[\w.-]` findet Buchstaben, Punkt oder Bindestrich |
| `(?<!\n)` `(?!\n)` | „davor steht kein“ / „danach steht kein“ Zeilenumbruch | siehe Schritt 3 |

Die drei Schritte im Flow:

| Schritt | Search Pattern | Replacement Text | Was passiert |
| --- | --- | --- | --- |
| 1 Silbentrennung entfernen | `-\n` | (leer) | Ein Bindestrich am Zeilenende wird mit dem Umbruch gelöscht: *Biblio-* / *theken* wird zu *Bibliotheken*. |
| 2 Kopfzeilen entfernen | `\s*Bibliotheksforum 12 \(2025\) +Seite \d+\s*` | `\n\n` | Die Kopfzeile mit allen Leerzeilen davor und danach wird durch eine einzige Leerzeile ersetzt. |
| 3 Zeilen zusammenführen | `(?<!\n)\n(?!\n)` | ein Leerzeichen | Ein einzelner Zeilenumbruch wird zum Leerzeichen. Doppelte Umbrüche, also Absätze, bleiben. |

Die **Reihenfolge** zählt: Würde Schritt 3 vor Schritt 1 laufen, stünde aus *Biblio-* und *theken* ein *Biblio- theken* da, und `-\n` fände nichts mehr. Das probiert ihr in Übung 2 aus.

**Eine Grenze von Regeln:** Titel und Autor:innen des Artikels stehen nach Schritt 3 in einer Zeile, *Offene Metadaten in der Erwerbung Anna Berger und Deniz Yilmaz*. Für die Regel sehen ein umbrochener Satz und zwei kurze Zeilen gleich aus. Regeln sind schnell, kostenlos und immer gleich, aber sie verstehen den Text nicht. Wo das nötig wird, hilft später ein Sprachmodell ([L6](L6_strukturierte_antworten.md)).

### 3.2 Data Operations: Text säubern (Text Clean)

*Text Clean* räumt mit drei Schaltern auf. Schritt 4 im Flow nutzt nur den ersten.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Remove Extra Spaces** | am Baustein | Mehrere Leerzeichen hintereinander werden zu einem. Standard: an. |
| **Remove Empty Lines** | am Baustein | Leere Zeilen werden gelöscht. Damit verschwinden auch die Grenzen zwischen Absätzen. |
| **Remove Special Characters** | am Baustein | Löscht alles außer Buchstaben, Ziffern und Leerzeichen, auch Punkte, Kommas, `/` und `@`. |

### 3.3 Data Operations: Muster herausziehen (Text Extract)

*Text Extract* gibt alles zurück, was zu einem Suchmuster passt, eine Fundstelle pro Zeile. Der Abzweig *DOIs herausziehen* findet so die drei DOIs im Text.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Extract Pattern** | am Baustein | Das Suchmuster. Hier ist es immer ein regulärer Ausdruck. |
| **Max Matches** | am Baustein | Höchstens so viele Fundstellen. Standard: 10. |

Das Muster für DOIs im Flow ist `10\.\d{4,9}/[\w./-]*\w`: *10.*, dann vier bis neun Ziffern (`\d{4,9}`), ein Schrägstrich, dann Buchstaben, Ziffern, Punkte, Schrägstriche und Bindestriche, und am Ende ein Buchstabe oder eine Ziffer. Das letzte `\w` sorgt dafür, dass ein Satzpunkt oder eine Klammer hinter der DOI nicht mitkommt.

### 3.4 Data Operations: zählen, kürzen, verbinden, Groß- und Kleinschreibung

Diese Operationen kommen im Flow nur einmal oder gar nicht vor; ihr probiert sie in den Übungen aus, indem ihr in einem Baustein die **Operation** wechselt.

| Operation | Einstellungen | Was herauskommt |
| --- | --- | --- |
| **Word Count** | *Count Words*, *Count Characters*, *Count Lines* (*Parameters*, alle an) | Ein **JSON** mit Wörtern, verschiedenen Wörtern, Zeichen mit und ohne Leerzeichen, Zeilen und nicht leeren Zeilen. Im Flow: *Wörter zählen*. |
| **Text Head** | *Characters from Start* (Standard: 100) | Die ersten so vielen Zeichen, z. B. für eine Vorschau |
| **Text Tail** | *Characters from End* (Standard: 100) | Die letzten so vielen Zeichen |
| **Text Strip** | *Characters to Strip*, *Strip Mode* (*both*, *left*, *right*) | Entfernt am Anfang und Ende des Textes Leerzeichen oder, falls angegeben, die genannten **Zeichen**, jedes einzeln (siehe Übung 6) |
| **Text Join** | *Second Text Input* | Beide Texte hintereinander, durch einen Zeilenumbruch getrennt |
| **Case Conversion** | *Case Type*: *uppercase*, *lowercase*, *title*, *capitalize*, *swapcase* | GROSS, klein, Jedes Wort Groß, nur der erste Buchstabe groß, Groß und Klein vertauscht |

Fast alle Text-Operationen geben eine **Message** weiter; nur *Word Count* gibt JSON aus und *Text to DataFrame* eine Tabelle.

### 3.5 Split Text: Text in Stücke zerlegen

*Split Text* zerlegt einen Text in Stücke (*Chunks*) und gibt sie als **Tabelle** aus, ein Stück pro Zeile in der Spalte `text`. Wozu? Um eine Liste Eintrag für Eintrag zu bearbeiten ([L8](L8_wiederholen_mit_loop.md)), um jeden Abschnitt einzeln von einem Sprachmodell bearbeiten zu lassen ([L6](L6_strukturierte_antworten.md)) oder weil ein langer Text für ein Modell zu lang ist.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Separator** | am Baustein | Wo getrennt wird: `\n` an jedem Zeilenumbruch, `\n\n` an Leerzeilen (Absätzen), oder jedes andere Zeichen, z. B. `§` |
| **Chunk Size** | am Baustein | Höchstlänge eines Stücks in Zeichen (Standard: 1000). Kurze Teile werden zusammengelegt, bis diese Länge erreicht ist. |
| **Chunk Overlap** | am Baustein | Wie viele Zeichen am Ende eines Stücks am Anfang des nächsten wiederholt werden (Standard: 200) |
| **Clean Output** | *Parameters* | An: nur die Spalte `text`. Aus: zusätzlich gut ein Dutzend Spalten mit Angaben zur Herkunft, z. B. Dateiname und Größe. |
| **Keep Separator** | *Parameters* | Ob das Trennzeichen erhalten bleibt: *False* (Standard) entfernt es, *Start*, *End* und *True* behalten es. In Langflow 1.12.3 steht es bei allen drei am Anfang des Stücks. |

Im Flow: *Separator* `\n\n`, *Chunk Size* `1`, *Chunk Overlap* `0`, *Clean Output* an. Ergibt neun Zeilen: die Überschrift und die acht Paragrafen. Mit *Chunk Size* `1` wird an **jedem** Trennzeichen getrennt, denn schon ein Zeichen ist zu lang zum Zusammenlegen.

**Warum Overlap?** Wird ein Text nach Länge zerlegt, kann ein Satz mitten durchgeschnitten werden; Stück 2 beginnt dann mit dem halben Satz. Mit Überlappung steht das Ende von Stück 1 noch einmal am Anfang von Stück 2. Für Menschen ist das doppelt; ein Sprachmodell, das nur Stück 2 bekommt, versteht so den Zusammenhang. Bei Stücken, die an natürlichen Grenzen geschnitten werden, wie den Paragrafen hier, braucht ihr keine Überlappung.

**Im Playground** sehen Zeilenumbrüche innerhalb eines Stücks aus wie neue Tabellenzeilen. Zählt im Zweifel mit dem Ausgabe-Symbol am Baustein nach.

### 3.6 Type Convert: Tabelle, Text oder JSON

*Type Convert* wandelt zwischen **Message**, **JSON** und **Table** um, wenn zwei Bausteine nicht zusammenpassen. Im Flow macht er aus der Tabelle der Abschnitte wieder Text.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Output Type** | am Baustein | *Message*, *JSON* oder *Table*. Der Ausgang ändert sich mit. |
| **Auto Parse** | *Parameters* | Erkennt CSV oder JSON, das als Text ankommt, und macht daraus echte Spalten oder Felder. Standard: aus. |

Aus einer Tabelle wird mit *Message* eine Text-Tabelle mit senkrechten Strichen zwischen den Spalten; Zeilenumbrüche in einer Zelle stehen dann als `<br/>` da. Den umgekehrten Weg, aus CSV-Text eine Tabelle, probiert ihr in Übung 8.

### 3.7 Data Operations: aus Text eine Tabelle (Text to DataFrame)

*Text to DataFrame* macht aus Text mit einem Trennzeichen zwischen den Spalten eine Tabelle. Im Flow steht eine kleine Zeitschriftenliste direkt im Feld **Text** des Bausteins *Liste zu Tabelle*.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Table Separator** | am Baustein | Das Zeichen zwischen den Spalten. Standard: `\|`. |
| **Has Header** | *Parameters* | Die erste Zeile enthält die Spaltennamen. Standard: an. |

Er trennt stur an jedem Trennzeichen. Für echte CSV-Dateien, in denen ein Komma auch in Anführungszeichen stehen kann, ist *Type Convert* mit *Auto Parse* der richtige Weg (Übung 8).

## 4. Übungen

🟢 Ausprobieren · 🟡 Umbauen · 🔴 Selbst bauen. Die Lösungen lassen sich aufklappen.

### 🟢 1. Die Kette Schritt für Schritt

Drückt nacheinander ▶ an *1 Silbentrennung entfernen*, *2 Kopfzeilen entfernen*, *3 Zeilen zusammenführen* und *4 Leerzeichen säubern* und seht euch jedes Mal die Ausgabe an. Was hat sich in jedem Schritt verändert? Was ist am Ende noch nicht in Ordnung?

<details>
<summary>Lösung</summary>

1. Die getrennten Wörter (*Bibliotheken*, *Verlagen*, *automatisch*, *nachzutragen*) sind wieder ganz.
2. Die beiden Kopfzeilen sind weg, an ihrer Stelle steht eine Leerzeile.
3. Jeder Absatz steht in einer einzigen Zeile.
4. Die doppelten Leerzeichen sind weg.

Nicht in Ordnung: Titel und Autor:innen stehen in derselben Zeile. Für die Regel in Schritt 3 sind zwei kurze Zeilen nicht von einem umbrochenen Satz zu unterscheiden (siehe [3.1](#31-data-operations-text-ersetzen-text-replace)).

</details>

### 🟢 2. Die Reihenfolge zählt

Verbindet *Text aus dem PDF* direkt mit *3 Zeilen zusammenführen* (die Linie in dessen Eingang *Text* wird dabei ersetzt) und drückt ▶. Sucht im Ergebnis nach *Biblio*.

<details>
<summary>Lösung</summary>

Dort steht jetzt *Biblio- theken*: Der Zeilenumbruch nach dem Bindestrich ist schon zum Leerzeichen geworden, und eine Silbentrennung erkennt man nicht mehr am Muster `-\n`. Wer Text mit Regeln säubert, muss sich die Reihenfolge überlegen: zuerst das, was Zeilenumbrüche als Merkmal braucht, dann die Zeilenumbrüche selbst. Verbindet die Kette danach wieder wie vorher (*Text aus dem PDF* → *1 Silbentrennung entfernen* … *2 Kopfzeilen entfernen* → *3 Zeilen zusammenführen*).

</details>

### 🟢 3. Wie gründlich darf es sein?

Schaltet im Baustein *4 Leerzeichen säubern* nacheinander **Remove Empty Lines** und **Remove Special Characters** an und drückt jeweils ▶. Was geht verloren?

<details>
<summary>Lösung</summary>

*Remove Empty Lines* löscht die Leerzeilen zwischen den Absätzen; der ganze Artikel klebt zusammen. *Remove Special Characters* löscht alle Satzzeichen, auch die in DOIs und E-Mail-Adressen: aus *10.1371/journal.pone.0127502* wird *101371journalpone0127502*, aus *2.400* wird *2400*. Für einen Text, der noch gelesen oder ausgewertet werden soll, sind beide Schalter zu grob. Schaltet sie wieder aus.

</details>

### 🟢 4. Bessere und schlechtere Suchmuster

Im Baustein *DOIs herausziehen*:

1. Ersetzt das **Extract Pattern** durch das einfachere `10\.\d{4,9}/\S+` (`\S` heißt: alles außer Leerzeichen) und drückt ▶.
2. Zieht stattdessen E-Mail-Adressen heraus: `[\w.-]+@[\w.-]+\.\w+`. Setzt dann **Max Matches** auf `1`.

<details>
<summary>Lösung</summary>

1. Zwei der drei Fundstellen haben jetzt ein Zeichen zu viel: *10.7717/peerj.4375.* mit dem Satzpunkt und *10.1038/s41598-023-41032-5).* mit Klammer und Punkt. Mit solchen DOIs würde eine Anfrage an Crossref scheitern. Das Muster im Flow endet deshalb mit `\w`.
2. Es kommen beide Adressen heraus, mit *Max Matches* `1` nur die erste. Achtung: Das Herausziehen von E-Mail-Adressen ist schnell gebaut. Wenn ihr es mit echten Daten tut, sind das personenbezogene Daten.

</details>

### 🟢 5. Zerlegen auf fünf Arten

Ändert im Baustein *In Abschnitte zerlegen (Split Text)* die Einstellungen und drückt jeweils ▶. Zählt die Zeilen im Ausgang *Chunks*. Stellt danach immer wieder auf `\n\n`, `1`, `0` zurück.

1. **Separator** `\n`
2. **Separator** `§`. Dann zusätzlich unter *Parameters* **Keep Separator** auf *Start*.
3. **Separator** `\n\n`, unter *Parameters* **Clean Output** aus
4. **Separator** ` ` (ein Leerzeichen), **Chunk Size** `300`, **Chunk Overlap** `0`
5. wie 4, aber **Chunk Overlap** `80`. Vergleicht den Anfang der zweiten Zeile mit dem Ende der ersten.

<details>
<summary>Lösung</summary>

1. 17 Zeilen: Jede Überschrift (*§ 1 Geltungsbereich*) ist jetzt von ihrem Text getrennt.
2. 9 Zeilen wie mit `\n\n`, aber das `§` fehlt: Die Zeilen beginnen mit *1 Geltungsbereich*. Mit *Keep Separator* *Start* steht es wieder vorn.
3. Dieselben 9 Zeilen, aber mit gut einem Dutzend zusätzlicher Spalten: Dateiname, Pfad, Größe, Zeitstempel und anderes, das *Read File* mitgegeben hat. Für die Weiterarbeit stört das meist; darum ist *Clean Output* im Flow an.
4. 7 Stücke von knapp 300 Zeichen. Sie enden mitten im Satz, z. B. *… alle Mitglieder der Hochschule sowie*, und das nächste beginnt mit *externe Personen ab 16 Jahren*.
5. 8 Stücke. Das zweite beginnt jetzt mit *2 Zulassung …*, also mit dem Ende des ersten. So geht an den Schnittstellen kein Zusammenhang verloren; der Preis ist, dass Text doppelt vorkommt.

</details>

### 🟢 6. Kürzen, zählen, Groß und klein

Wechselt im Baustein *Wörter zählen* die **Operation** und drückt jeweils ▶. Mit der Operation ändert sich der Ausgang (von JSON zu Message), und die Linie zum Chat Output *Zählung* verschwindet. Für ▶ braucht ihr sie nicht; seht euch das Ergebnis mit dem Ausgabe-Symbol am Baustein an.

1. *Text Head* mit *Characters from Start* `120`, dann *Text Tail*
2. *Case Conversion* mit *Case Type* *uppercase*
3. *Text Strip* mit *Characters to Strip* `Bie`

<details>
<summary>Lösung</summary>

1. Die ersten 120 Zeichen, hier die Kopfzeile, Titel und der Anfang der Autor:innen, bzw. die letzten 100 Zeichen, die Kontaktadressen. Praktisch für eine Vorschau oder um einen Text auf eine Höchstlänge zu kürzen.
2. Der ganze Text in Großbuchstaben, sogar die DOIs.
3. Überraschung: Aus *Bibliotheksforum* wird *bliotheksforum*. *Text Strip* entfernt nicht das Wort *Bie*, sondern die Buchstaben *B*, *i* und *e*, jeden einzeln, so lange einer davon am Rand steht. Das kleine *b* steht nicht in der Liste, dort hört es auf. Ohne *Characters to Strip* entfernt *Text Strip* Leerzeichen und Leerzeilen am Anfang und Ende; dafür ist es gedacht.

Stellt die Operation danach wieder auf *Word Count* und verbindet den Ausgang *JSON* wieder mit *Zählung*.

</details>

### 🟡 7. Die Katalogsuche aus L1 reparieren

In [L1, Übung 8](L1_daten_importieren.md#4-übungen) musstet ihr die Suchbegriffe für lobid mit `+` statt Leerzeichen eintippen. Baut den Flow so um, dass ihr ganz normal *Umberto Eco Abschlussarbeit* eintippen könnt.

<details>
<summary>Lösung</summary>

Zwischen **Chat Input** und **Prompt Template** einen **Data Operations** mit *Input Type* *Text* und der Operation **Text Replace** setzen: *Search Pattern* ` ` (ein Leerzeichen), *Replacement Text* `+`, *Use Regex* aus. Seinen Ausgang mit dem Platzhalter `{suchbegriff}` des Prompt Templates verbinden.

```text
Chat Input → Data Operations (Text Replace " " → "+") → Prompt Template (URL) → API Request → Chat Output
```

Aus *Umberto Eco Abschlussarbeit* wird *Umberto+Eco+Abschlussarbeit*, und lobid findet *Wie man eine wissenschaftliche Abschlußarbeit schreibt*. Umlaute wie in *Müller* dürft ihr übrigens stehen lassen, die nimmt die Adresse an.

Den Flow könnt ihr in eurer Kopie von L2 bauen. Weil er einen Chat Input hat, führt der Playground danach nur noch diesen Zweig aus (siehe [L1](L1_daten_importieren.md#36-chat-input-text-aus-dem-playground)); die übrigen startet ihr mit ▶.

</details>

### 🟡 8. CSV-Text in eine Tabelle: zwei Wege

Ihr kennt aus L1, dass *Read File* eine CSV-Datei als Text weitergibt. Setzt einen dritten **Read File** auf die Arbeitsfläche und ladet `daten/lernpfad/neuerwerbungen.csv` hoch.

1. Verbindet ihn mit einem neuen **Data Operations** (*Input Type* *Text*, Operation *Text to DataFrame*, **Table Separator** `,`) und drückt ▶.
2. Verbindet ihn stattdessen mit einem neuen **Type Convert**, **Output Type** *Table*, und drückt ▶. Schaltet dann unter *Parameters* **Auto Parse** an und drückt noch einmal ▶.

<details>
<summary>Lösung</summary>

1. Fehler: *Header mismatch: 9 column(s) in header vs 10 column(s) in data row 1.* Die Autor:innen stehen als *"Berger, Anna"* in Anführungszeichen, weil der Name selbst ein Komma enthält. *Text to DataFrame* trennt stur an jedem Komma und zählt eine Spalte zu viel.
2. Ohne *Auto Parse* entsteht eine Tabelle mit **einer** Zeile und **einer** Spalte `text`, in der die ganze Datei steht. Mit *Auto Parse* erkennt Type Convert das CSV-Format, Anführungszeichen eingeschlossen: 15 Zeilen, 9 Spalten. Schaut euch die Spalte `jahr` an: Dort steht *2024.0* statt *2024*, weil ein Jahr fehlt und die Spalte deshalb als Kommazahl gelesen wird. Mit genau dieser Tabelle geht es in [L3](L3_tabellen_und_json.md) weiter.

</details>

### 🔴 9. Aus DOIs im Text eine Linkliste machen

Baut aus dem Abzweig *DOIs herausziehen* eine Tabelle mit klickbaren Links, eine pro Zeile: `https://doi.org/10.1371/journal.pone.0127502` und so weiter. Darüber soll im Playground als Text die Überschrift *Gefundene DOIs:* stehen, gefolgt von der Liste.

Tipp: Im Suchmuster steht `^` für den Anfang einer Zeile, wenn ihr das Muster mit `(?m)` beginnt.

<details>
<summary>Lösung</summary>

Für die Tabelle:

```text
DOIs herausziehen → Data Operations (Text Replace) → Split Text → Chat Output
```

- *Text Replace*: *Search Pattern* `(?m)^`, *Replacement Text* `https://doi.org/`, *Use Regex* an. Vor jede Zeile kommt die Adresse.
- *Split Text*: *Separator* `\n`, *Chunk Size* `1`, *Chunk Overlap* `0`, *Clean Output* an. Ergibt drei Zeilen.

Für die Überschrift einen weiteren **Data Operations** mit **Text Join**: in sein Feld *Text* `Gefundene DOIs:` tippen und den Ausgang von *Text Replace* mit *Second Text Input* verbinden. Er gibt beides untereinander aus. Diese Linkliste ist schon fast die Eingabe für eine Schleife, die jede DOI einzeln nachschlägt: Das kommt in [L8](L8_wiederholen_mit_loop.md).

</details>

## 5. Wann nehme ich was?

| Ihr wollt … | Baustein und Einstellung | Hinweis |
| --- | --- | --- |
| ein bestimmtes Wort oder Zeichen ersetzen oder löschen | **Data Operations** → *Text Replace*, *Use Regex* aus | `\n` steht für einen Zeilenumbruch |
| etwas ersetzen, das immer gleich *aussieht*, aber nie gleich *ist* (Seitenzahlen, Datumsangaben) | **Data Operations** → *Text Replace*, *Use Regex* an | Suchmuster vorher an einem Beispiel ausprobieren |
| doppelte Leerzeichen loswerden | **Data Operations** → *Text Clean* | *Remove Special Characters* nur, wenn Satzzeichen wirklich stören |
| bestimmte Angaben herausziehen (DOIs, ISBNs, E-Mail-Adressen) | **Data Operations** → *Text Extract* | Eine Fundstelle pro Zeile |
| einen Text kürzen | **Data Operations** → *Text Head* / *Text Tail* | Zählt Zeichen, nicht Wörter |
| wissen, wie lang ein Text ist | **Data Operations** → *Word Count* | Gibt JSON aus |
| zwei Texte aneinanderhängen | **Data Operations** → *Text Join* | Für mehr als zwei Texte ist ein *Prompt Template* mit Platzhaltern bequemer ([L4](L4_ergebnisse_ausgeben.md)) |
| einen Text in Absätze, Zeilen oder Paragrafen zerlegen | **Split Text**, *Chunk Size* `1`, *Chunk Overlap* `0` | *Clean Output* an |
| einen langen Text in gleich große Stücke für ein Modell schneiden | **Split Text**, *Chunk Size* z. B. `1000`, *Chunk Overlap* z. B. `200` | Separator ` ` oder `\n`, damit nicht mitten im Wort geschnitten wird |
| eine kopierte Liste mit `\|` oder Tabulator in eine Tabelle verwandeln | **Data Operations** → *Text to DataFrame* | Trennt an jedem Trennzeichen |
| eine CSV-Datei in eine Tabelle verwandeln | **Type Convert**, *Table*, *Auto Parse* an | Versteht Anführungszeichen |
| eine Tabelle wieder als Text weitergeben | **Type Convert**, *Message* | Für eine eigene Form pro Zeile ist der *Parser* besser ([L3](L3_tabellen_und_json.md)) |
| Text verstehen statt nach Regeln behandeln (Titel von Namen unterscheiden, zusammenfassen) | ein Sprachmodell | [L5](L5_prompts_und_modelle.md) und [L6](L6_strukturierte_antworten.md) |

## 6. Wenn etwas nicht klappt

| Meldung oder Problem | Ursache und Lösung |
| --- | --- |
| *No files to process* | In einem der beiden *Read File* fehlt die Datei. Beide müssen eine haben, sonst bricht der ganze Lauf im Playground ab. |
| Ein Data Operations zeigt keine Felder und keinen Ausgang | Es ist noch keine **Operation** gewählt. Erst *Input Type*, dann *Operation* wählen. |
| *Text Replace* ändert nichts | Das Suchmuster passt nicht. Steht *Use Regex* an, haben Zeichen wie `.`, `(` und `+` eine besondere Bedeutung; schreibt `\.`, `\(` und `\+`, wenn ihr das Zeichen selbst meint. |
| Fehler mit *regex* oder *pattern* | Das Suchmuster ist unvollständig, z. B. eine Klammer fehlt |
| *Header mismatch: … column(s)* | *Text to DataFrame* zählt in einer Zeile mehr oder weniger Spalten als in der Kopfzeile. Bei CSV *Type Convert* mit *Auto Parse* nehmen. |
| Die Tabelle aus *Split Text* hat viel mehr Spalten als `text` | *Clean Output* (*Parameters*) einschalten |
| Die Tabelle im Playground hat mehr Zeilen als erwartet | Zeilenumbrüche innerhalb eines Stücks sehen dort wie neue Zeilen aus. Mit dem Ausgabe-Symbol am Baustein nachzählen. |

**Weiter:** [L3 Tabellen und JSON](L3_tabellen_und_json.md) zeigt, wie ihr Tabellen filtert, sortiert und zusammenführt und die Antwort eines Webdienstes in eine Tabelle verwandelt.
