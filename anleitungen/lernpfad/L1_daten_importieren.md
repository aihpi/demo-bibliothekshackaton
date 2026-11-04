# L1 Daten importieren

Bevor ein Flow etwas prüfen, zusammenfassen oder sortieren kann, braucht er Daten. In Bibliotheken liegen sie an ganz verschiedenen Orten: in einer Excel-Liste der Erwerbung, auf einer Webseite, in einer Datenbank wie OpenAlex oder in den Nachrichten. Dieser Flow holt Daten auf fünf Wegen und zeigt jedes Ergebnis in einem eigenen Chat Output, damit ihr die Wege direkt vergleichen könnt.

| | |
| --- | --- |
| **Ihr lernt** | Dateien hochladen und lesen, Webseiten holen, einen Webdienst abfragen, im Web suchen, mit Testdaten arbeiten. Und: was im Playground läuft und was nicht. |
| **Bausteine** | Read File, URL, API Request, Web Search, Mock Data, Chat Output, Chat Input |
| **KI** | keine |
| **Dauer** | etwa 45 Minuten |
| **Testdaten** | `daten/lernpfad/neuerwerbungen.csv`, `daten/lernpfad/benutzungsordnung.txt`, `daten/masterarbeit_quellenanalyse/beispiel_masterarbeit.pdf` |

## Inhalt

1. [Der Flow im Überblick](#1-der-flow-im-überblick)
2. [Vorbereiten](#2-vorbereiten)
3. [Schritt für Schritt](#3-schritt-für-schritt)
4. [Übungen](#4-übungen)
5. [Wann nehme ich was?](#5-wann-nehme-ich-was)
6. [Wenn etwas nicht klappt](#6-wenn-etwas-nicht-klappt)

## 1. Der Flow im Überblick

Der Flow besteht aus fünf Zeilen, die nichts miteinander zu tun haben. Jede holt Daten aus einer anderen Quelle:

| Zeile | Baustein | Woher die Daten kommen | Was herauskommt |
| --- | --- | --- | --- |
| 1 | **Read File** | eine Datei, die ihr hochladet | der Text der Datei (Message) |
| 2 | **URL** | die Wikipedia-Seite *Open Access* | der Text der Seite (Message) oder eine Tabelle der Seiten (Table) |
| 3 | **API Request** | der Webdienst OpenAlex, eine Literaturdatenbank | die Antwort des Dienstes (JSON) |
| 4 | **Web Search** | Google News | eine Tabelle der Treffer (Table) |
| 5 | **Mock Data** | ausgedacht, vom Baustein selbst | eine Tabelle mit Testdaten (Table) |

Rechts am Ende jeder Zeile steht ein **Chat Output**. Er zeigt das Ergebnis im Playground an, Tabellen als Tabellen.

Achtet auf die **Typen** in der rechten Spalte: Message (Text), JSON (Datensatz mit benannten Feldern) und Table (Zeilen und Spalten). Welchen Typ eine Quelle liefert, entscheidet, was ihr danach damit tun könnt. Darum geht es in [L2](L2_texte_aufbereiten.md) und [L3](L3_tabellen_und_json.md).

## 2. Vorbereiten

1. In der Übersicht von Langflow beim Flow **L1 Daten importieren** auf die drei Punkte klicken → *Duplicate*. Arbeitet in der Kopie.
2. Die Kopie öffnen. Im Baustein **Datei lesen (Read File)** auf **Select files** klicken und `daten/lernpfad/neuerwerbungen.csv` aus dem Projektordner hochladen.
3. Oben rechts auf **Playground** klicken, irgendetwas eintippen (z. B. *los*) und abschicken. Nach einigen Sekunden erscheinen fünf Nachrichten, eine pro Zeile.

Der Flow hat keinen Chat Input, darum ist es egal, was ihr eintippt: Die Nachricht startet nur den Lauf. Warum das wichtig ist, zeigt Übung 6.

**Einen Baustein einzeln ausführen.** Statt des Playgrounds könnt ihr jeden Baustein mit dem Knopf **▶** oben rechts am Baustein ausführen. Danach erscheint unten rechts am Ausgang ein kleines Symbol. Ein Klick darauf zeigt, was der Baustein weitergibt. So arbeitet ihr in diesem ganzen Modul: Einstellung ändern, ▶ drücken, Ausgabe ansehen.

## 3. Schritt für Schritt

### 3.1 Read File: Daten aus einer Datei

*Read File* liest eine hochgeladene Datei und gibt ihren Text als **Message** weiter. Er versteht Text, CSV, Excel, PDF, Word und viele weitere Formate.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Files** | am Baustein | Die Datei(en). Mit *Select files* hochladen. Mehrere Dateien sind erlaubt. |
| **Advanced Parser** | am Baustein | Liest schwierige PDFs, Scans und Office-Dateien genauer (mit Docling). Deutlich langsamer und braucht viel Arbeitsspeicher. Für CSV und Excel nicht verfügbar. |
| **Separator** | *Parameters* | Was zwischen mehreren Dateien steht. Standard: eine Leerzeile. |

**Ausprobieren:** ▶ drücken und den Ausgang *Raw Content* ansehen. Die CSV-Datei kommt als **Text** heraus, mit Kommas zwischen den Werten, nicht als Tabelle. Wie daraus eine Tabelle wird, zeigt [L3](L3_tabellen_und_json.md).

### 3.2 URL: Daten von einer Webseite

*URL* lädt eine oder mehrere Webseiten herunter und entfernt die HTML-Befehle, sodass der lesbare Text übrig bleibt.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **URLs** | am Baustein | Eine oder mehrere Adressen. Mit **+** weitere hinzufügen. |
| **Depth** | am Baustein | *1*: nur die Seite. *2*: dazu jede Seite, auf die sie verlinkt. *3*: noch eine Ebene weiter. Jede Stufe vervielfacht die Zahl der Seiten. |
| **Output Format** | *Parameters* | *Text* (nur der Text), *Markdown* (Text mit Überschriften und Links), *HTML* (die Seite, wie sie ist) |
| **Prevent Outside** | *Parameters* | Bei Depth 2 oder 3 nur Links auf derselben Website folgen. Standard: an. |
| **Headers** | *Parameters* | Zusatzangaben zur Anfrage. Hier steht ein *User-Agent*, also ein Absender. |

Der Baustein hat zwei Ausgänge: **Extracted Pages** (Table, eine Zeile pro Seite mit Adresse und Text) und **Raw Content** (Message, der Text aller Seiten hintereinander). Der Flow nutzt *Raw Content*.

**Warum der User-Agent?** Wikipedia lehnt Anfragen ab, die nicht sagen, wer fragt. Der Eintrag im Flow nennt einen Namen und eine Webadresse; das reicht.

### 3.3 API Request: Daten von einem Webdienst

Ein **Webdienst** (eine *API*) ist eine Adresse, die keine Webseite für Menschen liefert, sondern Daten für Programme. Viele Bibliotheksdienste haben eine: OpenAlex, Crossref, lobid (der hbz-Verbundkatalog), die DNB. *API Request* ruft eine solche Adresse auf und gibt die Antwort als **JSON** weiter.

Die Adresse im Flow fragt OpenAlex nach Publikationen zu *academic libraries open access*:

```text
https://api.openalex.org/works?search=academic%20libraries%20open%20access&per-page=3&select=display_name,publication_year,doi
```

Alles nach dem `?` sind **Parameter**, durch `&` getrennt: `search` (Suchbegriffe; `%20` steht für ein Leerzeichen), `per-page` (wie viele Treffer) und `select` (welche Felder). Welche Parameter es gibt, steht in der Dokumentation des Dienstes, für OpenAlex unter <https://docs.openalex.org>.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Mode** | am Baustein | *URL*: Adresse und Methode ausfüllen. *cURL*: einen fertigen cURL-Befehl einfügen, wie ihn viele Dokumentationen zeigen. |
| **URL** | am Baustein | Die Adresse mit den Parametern |
| **Method** | am Baustein | *GET* holt Daten (fast immer richtig). *POST*, *PUT*, *PATCH*, *DELETE* schicken Daten. |
| **Query Parameters** | *Parameters* | Die Parameter als JSON-Eingang statt in der Adresse. Praktisch, wenn ein anderer Baustein sie berechnet ([L3](L3_tabellen_und_json.md)). |
| **Headers** | *Parameters* | z. B. ein *User-Agent* oder ein API-Schlüssel |
| **Timeout** | *Parameters* | Wie viele Sekunden auf eine Antwort gewartet wird. Standard: 30. |

**Ausprobieren:** ▶ drücken und den Ausgang *API Response* ansehen. Die eigentlichen Daten stehen im Feld `result`. Davor stehen Angaben zur Anfrage, z. B. `status_code`: *200* heißt „alles in Ordnung“, *404* „nicht gefunden“, *429* „zu viele Anfragen“.

### 3.4 Web Search: Treffer aus Websuche, News oder RSS

*Web Search* durchsucht das Web, ohne Konto und ohne Schlüssel, und gibt eine **Tabelle** mit Titel, Link und Textauszug zurück.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Search Mode** | am Baustein | *Web* (DuckDuckGo), *News* (Google News) oder *RSS* (ein Nachrichten-Feed) |
| **Search Query** | am Baustein | Die Suchbegriffe. Im Modus *RSS* die Adresse des Feeds. |
| **Max Results** | *Parameters* | Wie viele Treffer. Standard: 5. |
| **Language (hl)**, **Country (gl)**, **Country:Language (ceid)** | *Parameters* | Sprache und Land für *News*. Im Flow auf Deutsch und Deutschland gestellt: `de`, `DE`, `DE:de`. |
| **Max Content Length** | *Parameters* | Wie viele Zeichen pro Treffer behalten werden |

Ein **RSS-Feed** ist eine Liste der neuesten Beiträge einer Website, z. B. eines Blogs. Viele Bibliotheken und Fachportale haben einen. Der Feed des Bibliotheksportals des dbv steht unter `https://bibliotheksportal.de/feed/`.

### 3.5 Mock Data: Testdaten

*Mock Data* erzeugt ausgedachte Daten: Kund:innen mit Namen, Alter, Stadt und Bestellungen. Er hat keine Eingänge und drei Ausgänge mit demselben Namen *Result*, je einer als **Table**, **Message** und **JSON**. Fahrt mit der Maus über die Punkte, um den Typ zu sehen.

Wozu? Wenn ihr einen Flow baut, aber die echten Daten noch nicht habt oder sie nicht in einen Test geben wollt. Für Bibliotheksdaten passt er inhaltlich nicht, für das Ausprobieren von Tabellen-Bausteinen schon.

### 3.6 Chat Input: Text aus dem Playground

Fast jeder andere Flow beginnt mit *Chat Input*: Er nimmt, was ihr im Playground eintippt, und gibt es als Message weiter. Ihr könnt dort auch Text einfügen, z. B. ein Literaturverzeichnis. Das ist der schnellste Weg, Daten in einen Flow zu bringen, aber nur für Text, den ihr kopieren könnt.

In diesem Flow fehlt er mit Absicht. Hat ein Flow einen Chat Input, führt der Playground **nur die Bausteine aus, die von ihm abhängen**, und alles, was diese Bausteine brauchen. Die übrigen bleiben stehen. Das probiert ihr in Übung 6 aus.

## 4. Übungen

🟢 Ausprobieren · 🟡 Umbauen · 🔴 Selbst bauen. Die Lösungen lassen sich aufklappen.

### 🟢 1. Verschiedene Dateien lesen

Ladet nacheinander diese Dateien in *Read File* hoch und drückt jeweils ▶ (vorher die alte Datei mit dem Papierkorb entfernen):

- `daten/lernpfad/benutzungsordnung.txt`
- `daten/masterarbeit_quellenanalyse/beispiel_masterarbeit.pdf`
- beide zusammen

Was kommt jeweils heraus? Was steht bei zwei Dateien zwischen den Texten?

<details>
<summary>Lösung</summary>

Die Textdatei kommt unverändert heraus. Aus dem PDF holt *Read File* den Text Seite für Seite; Kopfzeilen und Seitenzahlen stehen mitten im Text, die Gestaltung ist weg. Bei zwei Dateien kommt ein Text heraus, beide hintereinander, getrennt durch eine Leerzeile: Das ist der *Separator* (*Parameters*). Tragt dort z. B. `=====` ein und drückt noch einmal ▶: Jetzt ist die Grenze zwischen den Dateien gut zu sehen.

</details>

### 🟢 2. Tiefe und Format einer Webseite

Im Baustein *Webseite holen (URL)*:

1. Unter *Parameters* das **Output Format** von *Text* auf *Markdown* und dann auf *HTML* stellen und jeweils ▶ drücken. Vergleicht die Länge des Ergebnisses.
2. Zurück auf *Text*. Die Adresse durch `https://lobid.org/` ersetzen, **Depth** auf *2* stellen, ▶ drücken und den Ausgang **Extracted Pages** ansehen. Wie viele Zeilen hat die Tabelle? Wie lange hat es gedauert? Dann Depth und Adresse zurückstellen.
3. Unter *Parameters* bei **Headers** den Eintrag *User-Agent* leeren und ▶ drücken.

<details>
<summary>Lösung</summary>

1. *Markdown* ist etwas länger als *Text*, weil Überschriften (`#`) und Links erhalten bleiben. *HTML* ist um ein Vielfaches länger: Es enthält alle Befehle für Layout, Menüs und Skripte. Für ein Sprachmodell ist *Text* oder *Markdown* fast immer die bessere Wahl.
2. Die Startseite von lobid.org verlinkt auf wenige Unterseiten derselben Website; bei Depth 2 holt der Baustein sie alle, etwa zehn Seiten in einigen Sekunden. Probiert Depth 2 **nicht** mit der Wikipedia-Seite: Sie verlinkt auf Hunderte andere Seiten, und der Baustein würde sie alle laden. Depth 2 und 3 sind für kleine Websites gedacht, die ihr kennt.
3. Wikipedia antwortet mit einer Fehlerseite (*Please respect our robot policy*). Der Baustein meldet keinen Fehler, er gibt die Fehlerseite als Text weiter. Darum lohnt sich immer ein Blick in die Ausgabe.

</details>

### 🟢 3. Einen Webdienst anders fragen

Ändert im Baustein *Webdienst fragen (API Request)* die **URL** und drückt jeweils ▶:

1. Andere Suchbegriffe: `search=citizen%20science%20libraries`
2. Mehr Treffer: `per-page=10`
3. Den Teil `&select=display_name,publication_year,doi` ganz entfernen

<details>
<summary>Lösung</summary>

1. und 2. Andere Treffer, und bei `per-page=10` zehn statt drei.
3. Ohne `select` liefert OpenAlex jeden Datensatz vollständig: Autor:innen mit Institutionen, Abstract, Themen, Zitationen, Open-Access-Status und vieles mehr. Die Antwort wird um ein Vielfaches länger. `select` ist ein guter Weg, nur das zu holen, was ihr braucht; das spart Zeit und, wenn die Daten zu einem Sprachmodell gehen, auch Kosten.

</details>

### 🟢 4. Websuche, News und RSS

Im Baustein *Im Web suchen (Web Search)*:

1. **Search Mode** auf *Web* stellen, ▶ drücken. Dann zurück auf *News*.
2. **Search Mode** auf *RSS* stellen und als Adresse `https://bibliotheksportal.de/feed/` eintragen.
3. Unter *Parameters* **Max Results** auf `10` setzen.

Worin unterscheiden sich die Treffer?

<details>
<summary>Lösung</summary>

*Web* findet Webseiten, die zu den Begriffen passen, egal wie alt. *News* findet Nachrichtenartikel mit Datum, die neuesten zuerst. *RSS* sucht gar nicht: Es liest die neuesten Beiträge genau einer Website, unabhängig von Suchbegriffen. Für „Was gibt es Neues im Bibliotheksportal?“ ist RSS richtig, für „Was wird über KI in Bibliotheken berichtet?“ *News*.

</details>

### 🟢 5. Ein Ausgang, drei Typen

Zieht im Baustein *Testdaten erzeugen (Mock Data)* die Verbindung vom ersten Ausgang *Result* (Table) auf den zweiten (Message) und dann auf den dritten (JSON). Fahrt vorher mit der Maus über die Punkte, um den Typ zu sehen. Was zeigt der Playground jeweils?

<details>
<summary>Lösung</summary>

*Table* erscheint als Tabelle. *Message* ist derselbe Inhalt als Text, für einen Prompt gedacht. *JSON* ist ein Datensatz mit einem Feld pro Spalte; im Playground erscheint er als Code-Block. Dieselben Daten, drei Formen: Welche richtig ist, hängt davon ab, was der nächste Baustein erwartet. Passt der Typ nicht, lässt Langflow die Verbindung nicht zu.

</details>

### 🟡 6. Ein Chat Input kommt dazu

1. Zieht einen **Chat Input** auf die Arbeitsfläche (Kategorie *Input & Output*).
2. Verbindet seinen Ausgang *Chat Message* mit dem Eingang **Search Query** von *Web Search*. Im Feld steht jetzt *Receiving input*.
3. Öffnet den Playground und schickt `Fernleihe` ab.

Wie viele Nachrichten erscheinen jetzt? Wie bekommt ihr die übrigen Ergebnisse?

<details>
<summary>Lösung</summary>

Nur noch eine: die der Websuche. Mit einem Chat Input führt der Playground nur die Bausteine aus, die von ihm abhängen. Die anderen Zeilen hängen nicht davon ab und bleiben stehen. Ihr startet sie mit ▶ an ihrem Chat Output.

Merkt euch das für eigene Flows: Soll eine Datei *zusammen mit* einer Chat-Frage verarbeitet werden, müssen beide in denselben Baustein münden, z. B. in ein *Prompt Template* mit zwei Platzhaltern. So macht es Flow 02 mit der Masterarbeit und dem Auftrag.

</details>

### 🟡 7. Ein zweiter Webdienst: Crossref

Setzt einen zweiten *API Request* auf die Arbeitsfläche und fragt Crossref nach einer bestimmten Publikation, über ihre DOI:

```text
https://api.crossref.org/works/10.1136/bmj.n71
```

Verbindet den Ausgang mit einem neuen *Chat Output*. Probiert dann den **Mode** *cURL* aus und fügt diesen Befehl ein:

```text
curl "https://api.crossref.org/works?query.bibliographic=PRISMA+2020+statement&rows=2"
```

<details>
<summary>Lösung</summary>

Die erste Anfrage liefert den vollständigen Datensatz des PRISMA-2020-Statements: Titel, Autor:innen, Zeitschrift, Datum, Referenzen. Im Modus *cURL* übernimmt der Baustein Adresse, Methode und Header aus dem Befehl; das ist praktisch, wenn eine Dokumentation Beispiele als cURL zeigt. `query.bibliographic` sucht nach einer Literaturangabe, so wie Flow 01b.

</details>

### 🔴 8. Eine Katalogsuche ohne Bibliotheks-Baustein

Baut einen kleinen Flow, der im hbz-Verbundkatalog sucht. Der Webdienst lobid nimmt Suchbegriffe so entgegen:

```text
https://lobid.org/resources/search?q=SUCHBEGRIFFE&size=3&format=json
```

Die Suchbegriffe sollen aus dem Playground kommen. Tipp: Ein *Prompt Template* setzt Text in Platzhalter ein, auch ganz ohne KI.

<details>
<summary>Lösung</summary>

**Chat Input** → **Prompt Template** mit dem Template `https://lobid.org/resources/search?q={suchbegriff}&size=3&format=json` → Ausgang *Prompt* an den Eingang **URL** von **API Request** → **Chat Output**.

Im Playground die Begriffe mit `+` statt Leerzeichen eintippen, z. B. `Umberto+Eco+Abschlussarbeit`. Mit Leerzeichen meldet *API Request* *Invalid URL provided*, weil Webadressen keine Leerzeichen enthalten dürfen. Wie ihr Leerzeichen automatisch ersetzt, zeigt [L2](L2_texte_aufbereiten.md) (*Text Replace*); wie ihr Parameter ohne Basteln an der Adresse übergebt, [L3](L3_tabellen_und_json.md) (*Query Parameters*).

Der Bibliotheks-Baustein *Katalogsuche* macht dasselbe und bereitet die Antwort zusätzlich als Tabelle auf.

</details>

## 5. Wann nehme ich was?

| Ihr habt … | Baustein | Hinweis |
| --- | --- | --- |
| eine Datei auf dem Rechner (PDF, Word, Excel, CSV, Text) | **Read File** | Für Scans und schwierige PDFs *Advanced Parser* einschalten |
| ein kurzes Stück Text zum Kopieren | **Chat Input** | Schnell, aber der Playground führt dann nur dessen Zweig aus |
| eine Webseite für Menschen | **URL** | *Depth* 1, *Output Format* Text oder Markdown |
| einen Webdienst mit Dokumentation (OpenAlex, Crossref, lobid) | **API Request** | Liefert genau die Felder, die ihr anfragt; mit `select` und Co. klein halten |
| eine Frage, aber keine bestimmte Quelle | **Web Search** (*Web*) | Treffer ändern sich mit der Zeit; Ergebnisse prüfen |
| Interesse an Neuigkeiten | **Web Search** (*News* oder *RSS*) | *RSS* für eine bestimmte Website, *News* für ein Thema |
| noch keine echten Daten | **Mock Data** | Nur zum Ausprobieren |
| eine Datenbank auf einem Server | **SQL Database** | Braucht Adresse und Zugang zu einem Datenbankserver; hier im Lernpfad nicht ausprobierbar, weil Langflow Datenbankdateien auf dem Laptop sperrt |

## 6. Wenn etwas nicht klappt

| Meldung oder Problem | Ursache und Lösung |
| --- | --- |
| *No files to process* | In *Read File* ist keine Datei hochgeladen. Mit *Select files* eine Datei wählen. Ohne Datei bricht der ganze Lauf im Playground ab. |
| *Access to local file paths … is disabled* | Ihr habt einen Pfad eingetippt. Langflow liest nur hochgeladene Dateien. |
| *Invalid URL provided* | Die Adresse enthält Leerzeichen. Sie durch `+` oder `%20` ersetzen. |
| *SSRF Protection: … blocked IP address* | Langflow sperrt Adressen auf dem Laptop und im lokalen Netz. Nur öffentliche Adressen funktionieren. |
| `status_code` 429 bei OpenAlex oder Crossref | Zu viele Anfragen. Kurz warten. Für OpenAlex hilft ein API-Schlüssel (siehe [Anleitung für Teilnehmende](../01_teilnehmende.md#23-zugangsdaten-eintragen)). |
| Die Websuche liefert eine leere Tabelle | Die Suchmaschine hat die Anfrage abgelehnt, oder der RSS-Feed hat eine falsche Adresse. Später noch einmal versuchen oder den Modus wechseln. |
| Im Playground fehlen Ergebnisse | Der Flow hat einen Chat Input (siehe Übung 6). Die übrigen Zweige mit ▶ starten. |

**Weiter:** [L2 Texte aufbereiten](L2_texte_aufbereiten.md) zeigt, wie ihr den Text, den ihr hier geholt habt, säubert und zerlegt.
