# Lernpfad

**Anleitungen:** [`anleitungen/lernpfad/`](../../anleitungen/lernpfad/)
**Flows:** `L1` bis `L9` im *Starter Project*

## Daten

Alle Daten sind ausgedacht oder stammen aus offenen Quellen. Personen, E-Mail-Adressen und Ausweisnummern sind erfunden.

| Datei | Inhalt | Genutzt in |
| --- | --- | --- |
| [`neuerwerbungen.csv`](neuerwerbungen.csv) | 15 Neuerwerbungen einer Bibliothek mit ISBN, Titel, Autor:in, Jahr, Verlag, Fach, Seiten, Preis und Status. Mit eingebauten Fehlern zum Aufräumen: eine doppelte Zeile, ein fehlendes Jahr, ein Fach in Kleinschreibung, Leerzeichen um einen Titel. | L1, L2, L3, L4, L5 |
| [`benutzungsordnung.txt`](benutzungsordnung.txt) | Auszug aus der Benutzungsordnung einer ausgedachten Bibliothek, acht Paragrafen | L1, L2, L5 |
| [`text_aus_pdf.txt`](text_aus_pdf.txt) | Ein ausgedachter Fachartikel, wie er aus einem PDF kopiert wird: Silbentrennung am Zeilenende, Umbrüche mitten im Satz, Kopfzeilen mit Seitenzahl, doppelte Leerzeichen. Enthält drei echte DOIs und zwei ausgedachte E-Mail-Adressen. | L2 |
| [`fachreferate.csv`](fachreferate.csv) | Fachreferat und Standort für sieben Fächer, zum Verbinden mit den Neuerwerbungen (Merge). Für das Fach `Allgemein` gibt es mit Absicht keinen Eintrag. | L3 |
| [`neuerwerbungen_nachtrag.csv`](neuerwerbungen_nachtrag.csv) | Drei weitere Neuerwerbungen mit denselben Spalten wie `neuerwerbungen.csv`, zum Anhängen (Concatenate) | L3 |
| [`dois.txt`](dois.txt) | Neun DOIs, eine pro Zeile: sieben bei Crossref verzeichnet (eine davon zu einem zurückgezogenen Artikel), eine DataCite-DOI (Zenodo) und eine ausgedachte | L8 |
| [`auskunftsanfragen.txt`](auskunftsanfragen.txt) | Zehn ausgedachte Auskunftsanfragen zum Einfügen in den Playground: Ausleihe, Recherche, Technik, Fernleihe, eine ohne passende Kategorie, dazu Anfragen mit erfundener E-Mail-Adresse und Ausweisnummer, mit einem Passwort und mit einem Manipulationsversuch | L7 |

## So nutzt ihr sie

Langflow liest keine Dateien direkt aus dem Projektordner. Ladet die Dateien im Baustein *Read File* mit **Select files** hoch. Welche Datei in welchen Baustein gehört, steht in der Anleitung des Moduls.
