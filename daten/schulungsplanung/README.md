# Use Case: Schulungsplanung automatisieren

**Von:** einer Hochschulbibliothek, deren Studierende überwiegend im Fernstudium sind (anonymisiert)
**Passender Flow:** `05 Schulungsplanung`

## Ziel

Die Hochschulbibliothek möchte ihre Schulungsplanung automatisieren.

## Grundlage

- Eine **Liste der Schulungen** mit ihrem **Turnus**: monatlich, alle zwei Monate oder alle drei Monate.
- Eine **Übersicht, welches Schulungspersonal welche Schulungen hält**.

Beispiel aus der Liste: *Writing Retreat (eng.); monatlich;* drei Personen, die diese Schulung halten.

Die meisten Informationen liegen in **Excel-Dateien im SharePoint** der Bibliothek. Die Bibliothek kann sie bei Bedarf bereitstellen; in diesem Projekt liegen sie noch nicht vor.

## Anforderungen

1. **Unterschiedliche Wochentage und Uhrzeiten.** Die Termine sollen nicht immer am selben Wochentag und zur selben Uhrzeit liegen. Die meisten Studierenden sind im Fernstudium und haben zu unterschiedlichen Zeiten Kapazitäten für eine Schulung.
2. **Urlaubstage berücksichtigen.** Für die Planung sind die Urlaubstage der Person wichtig, die eine Schulung hält. In dieser Zeit sollen keine Schulungen geplant werden. Offene Frage der Bibliothek: Wie lassen sich die Urlaubstage einbinden?
3. **HTML-Tabelle für die Lernplattform.** Wünschenswert ist eine HTML-Tabelle mit den Schulungsdaten, die in die Lernumgebung der Hochschule eingepflegt wird. Den bisherigen Quellcode, den das System erstellt hat, zeigt [`lernplattform_tabelle_vorlage.html`](lernplattform_tabelle_vorlage.html).
4. **Werbe-Mails.** Wenn die Schulungsdaten feststehen, gehen Mails an verschiedene Abteilungen der Hochschule, um für die Schulungen zu werben. Es ist immer dieselbe Vorlage, nur mit anderen Schulungsdaten. Diese Mails sollen ebenfalls erstellt werden können.

## Die Vorlage der Lernplattform

[`lernplattform_tabelle_vorlage.html`](lernplattform_tabelle_vorlage.html) ist der Quellcode der Tabelle „Aktuelle Termine September / Oktober 2026“. Für die Veröffentlichung ist er anonymisiert: Alle Links sind durch Platzhalter ersetzt (z. B. `LINK_ZUM_ZOOM_MEETING` oder `LINK_ZUR_ANMELDUNG`), der Name der Bibliotheksabteilung im Titel „Ersti-Hilfe mit der Bibliothek“ ist verallgemeinert und eine interne Kennung entfernt. Sonst ist der Quellcode unverändert.

Aufbau:

- Überschrift mit dem Zeitraum, darunter der Hinweis zur Dauer: „bitte Beschreibung beachten; ansonsten jeweils 1 Stunde; Sprechstunden 30 Min.“
- Eine Tabelle mit den Spalten **Datum** (z. B. `Do, 17.09.2026`), **Uhrzeit** (z. B. `15:00 Uhr`) und **Veranstaltung**. Der Titel der Veranstaltung ist mit dem Meetingraum verlinkt und trägt oft eine Stufe in Klammern, z. B. `(A1)`, `(B1)`, `(B2)`, `(C1)`.
- Die Zeilen wechseln sich farblich ab (`#f8f9fa` und `#ffffff`), die Kopfzeile ist `#e9ecef`.
- Unter der Tabelle: Anmeldung ab 14 Tagen vor dem Termin (für Termine mit Anmeldung), der Hinweis auf den Zoom-Link im Thema und ein Verweis auf die Videogalerie mit Aufzeichnungen.

Die Tabelle enthält 15 Termine vom 17.09. bis 29.10.2026, montags bis samstags zwischen 9:00 und 18:00 Uhr.

## Noch nicht vorhanden

- Die Excel-Listen mit Schulungen, Turnus und Schulungspersonal
- Die Urlaubstage des Schulungspersonals
- Die Vorlage der Werbe-Mail

Der Flow `05 Schulungsplanung` erwartet diese Daten deshalb als Dateien zum Hochladen.
