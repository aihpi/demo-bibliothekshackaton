# Lernpfad

**Anleitungen:** [`anleitungen/lernpfad/`](../../anleitungen/lernpfad/)
**Flows:** `L1` bis `L9` im *Starter Project*

## Daten

Alle Daten sind ausgedacht oder stammen aus offenen Quellen. Personen, E-Mail-Adressen und Ausweisnummern sind erfunden.

| Datei | Inhalt | Genutzt in |
| --- | --- | --- |
| [`neuerwerbungen.csv`](neuerwerbungen.csv) | 15 Neuerwerbungen einer Bibliothek mit ISBN, Titel, Autor:in, Jahr, Verlag, Fach, Seiten, Preis und Status. Mit eingebauten Fehlern zum Aufräumen: eine doppelte Zeile, ein fehlendes Jahr, ein Fach in Kleinschreibung, Leerzeichen um einen Titel. | L1, L2, L4 |
| [`benutzungsordnung.txt`](benutzungsordnung.txt) | Auszug aus der Benutzungsordnung einer ausgedachten Bibliothek, acht Paragrafen | L1, L2 |
| [`text_aus_pdf.txt`](text_aus_pdf.txt) | Ein ausgedachter Fachartikel, wie er aus einem PDF kopiert wird: Silbentrennung am Zeilenende, Umbrüche mitten im Satz, Kopfzeilen mit Seitenzahl, doppelte Leerzeichen. Enthält drei echte DOIs und zwei ausgedachte E-Mail-Adressen. | L2 |

## So nutzt ihr sie

Langflow liest keine Dateien direkt aus dem Projektordner. Ladet die Dateien im Baustein *Read File* mit **Select files** hoch. Welche Datei in welchen Baustein gehört, steht in der Anleitung des Moduls.
