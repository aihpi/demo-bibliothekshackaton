# Challenges

Jede Gruppe wählt eine Challenge. Jede Challenge hat einen fertigen **Start-Flow** und drei Stufen:

- 🟢 **Einstieg**: den Flow verstehen und anpassen, ohne neue Bausteine
- 🟡 **Ausbau**: neue Bausteine hinzufügen und verbinden
- 🔴 **Profi**: etwas Neues bauen, das es so noch nicht gibt

Ihr müsst nicht alle Stufen schaffen. Ein gut durchdachter Flow der Stufe 🟢 mit einer klugen Diskussion ist mehr wert als ein halbfertiger 🔴-Flow.

**Legt vor dem Ändern eine Kopie des Start-Flows an** (drei Punkte → *Duplicate*).

---

## Challenge A: Der Referenz-Checker

> *„Die Studentin schwört, dass es den Artikel gibt – ChatGPT hat ihn doch empfohlen.“*

Sprachmodelle erfinden Literaturangaben, die täuschend echt aussehen. Auch in echten Literaturverzeichnissen stecken Tippfehler, falsche Jahre und zurückgezogene Artikel. Baut ein Werkzeug, mit dem Auskunft, Schreibberatung oder Studierende ein Literaturverzeichnis in einer Minute prüfen können.

**Start-Flow:** `01 Referenz-Checker`

**Testdaten:** `daten/literaturliste_zum_pruefen.txt` (zehn Angaben mit eingebauten Fehlern), `daten/beispiel_masterarbeit.pdf`

### 🟢 Einstieg

1. Den Flow mit den Testdaten ausführen. Welche Fehler werden gefunden? Stimmt das Ergebnis? Prüft zwei Angaben selbst im Katalog oder bei [doi.org](https://doi.org).
2. Den Prompt so umschreiben, dass der Bericht **direkt an die Studentin** geht: freundlich, per Du oder Sie, mit konkreten Korrekturen.
3. Das Ergebnis mit einem eigenen Literaturverzeichnis ausprobieren (z. B. aus einer Publikation eures Hauses).

### 🟡 Ausbau

4. **PDF statt Text:** *Read File* und *Literaturverzeichnis finden* vor den Prüf-Baustein setzen. Jetzt reicht es, eine Abschlussarbeit hochzuladen.
5. **Zitierstil prüfen:** Ein zweiter KI-Schritt prüft, ob alle Angaben einheitlich einem Stil folgen (z. B. APA 7) und schlägt die korrigierte Fassung vor.
6. **Bücher nachschlagen:** Für Angaben mit ❓ die *Katalogsuche* nutzen. Tipp: Das geht am einfachsten mit einem *Agent*, der *Literaturangaben prüfen* und *Katalogsuche* als Werkzeuge bekommt (siehe Flow 04).

### 🔴 Profi

7. **Nur wenn nötig:** Mit *If-Else* oder *Smart Router* nur dann einen ausführlichen Bericht schreiben, wenn es Probleme gibt, sonst eine kurze Bestätigung.
8. **Bericht speichern:** Den Prüfbericht mit *Write File* als Datei ablegen.
9. **Bewertung:** Wie zuverlässig ist der Checker? Erfindet selbst mit einem Chatbot zehn Literaturangaben und lasst sie prüfen. Wie viele werden erkannt?

### Zum Diskutieren

- Darf man Abschlussarbeiten durch einen externen KI-Dienst schicken? Was ändert sich mit einem lokalen Modell?
- „Nicht gefunden“ heißt nicht „erfunden“. Wie kommuniziert man das Ergebnis, ohne jemanden vorschnell zu beschuldigen?

---

## Challenge B: Die Quellen einer Masterarbeit analysieren

> *„Auf welche Literatur stützt sich diese Arbeit eigentlich? Ist die aktuell? Ist die zugänglich?“*

Wer Abschlussarbeiten betreut, begutachtet oder in der Schreibberatung sitzt, will schnell einen Überblick über die verwendete Literatur. Baut einen Flow, der aus einer Arbeit alle Quellen herauszieht, anreichert und analysiert.

**Start-Flow:** `02 Masterarbeit – Quellen analysieren`

**Testdaten:** `daten/beispiel_masterarbeit.pdf` (fiktive Arbeit mit 17 echten Quellen)

### 🟢 Einstieg

1. Im Baustein *Abschlussarbeit (PDF)* die Beispiel-Arbeit hochladen und im Playground einen Auftrag geben, z. B. *Analysiere die Quellen dieser Arbeit.*
2. Verschiedene Aufträge ausprobieren: *Welche Quellen sind älter als zehn Jahre?*, *Welche Quellen sind nicht frei zugänglich?*, *Fehlen wichtige Themen?*
3. Den Prompt an eine Zielgruppe anpassen: Gutachter:in, Studierende, Erwerbung.

### 🟡 Ausbau

4. **Tabelle exportieren:** Den Ausgang *Quellen (Tabelle)* mit *Write File* verbinden und als CSV speichern. Die Datei öffnet sich in Excel.
5. **Volltexte:** *Volltexte holen* an die Tabelle hängen und die KI prüfen lassen, worum es in den frei verfügbaren Quellen wirklich geht.
6. **Prüfung einbauen:** Zusätzlich *Literaturangaben prüfen* anschließen, damit fehlerhafte Angaben auffallen.

### 🔴 Profi

7. **Literatur empfehlen:** Aus dem Überblick die Hauptthemen der Arbeit ableiten (KI-Schritt), daraus Suchbegriffe machen und mit *Literatursuche (OpenAlex)* aktuelle Literatur finden, die in der Arbeit fehlt.
8. **Erwerbungsvorschläge:** Nicht frei zugängliche Quellen, die häufig vorkommen, als Liste für die Erwerbung ausgeben.
9. **Vergleich:** Zwei Arbeiten hochladen und die Quellenbasis vergleichen.

### Zum Diskutieren

- Welche Kennzahlen aus der Statistik sind aussagekräftig, welche irreführend (z. B. Zitationszahlen)?
- Wo ist die Grenze zwischen Beratung und Bewertung einer Arbeit?

---

## Challenge C: Literaturüberblick und Forschungslücken (Text- und Data-Mining)

> *„Ich brauche für meinen Antrag einen Überblick über die Forschung zu … – verlagsübergreifend, bis Freitag.“*

Für einen systematischen Literaturüberblick muss man Publikationen vieler Verlage sammeln, die Volltexte lesen und vergleichen. Baut einen Flow, der zu einer Forschungsfrage Literatur zusammenträgt, freie Volltexte auswertet und Forschungslücken benennt.

**Start-Flow:** `03 Literaturreview – Forschungslücken finden`

**Beispielfrage:** *Wie verändern Sprachmodelle die Auskunft in wissenschaftlichen Bibliotheken?*

### 🟢 Einstieg

1. Den Flow mit der Beispielfrage und dann mit einer eigenen Frage aus eurem Fachgebiet ausführen.
2. Die Filter der *Literatursuche* ändern: nur die letzten fünf Jahre, nur Open Access, nach Zitationen sortiert. Wie verändert sich das Ergebnis?
3. Prüfen: Passen die gefundenen Publikationen zur Frage? Wenn nicht, den Prompt für die Suchbegriffe verbessern.

### 🟡 Ausbau

4. **Jede Publikation einzeln:** Mit *Batch Run* jede Publikation nach einem festen Schema zusammenfassen lassen (Fragestellung, Methode, Ergebnis, Einschränkungen). Das Ergebnis ist eine Tabelle.
5. **Ein- und Ausschluss:** Die KI entscheidet für jede Publikation mit Begründung, ob sie zur Frage passt, ähnlich wie bei PRISMA.
6. **Mehrere Suchen:** Die KI mehrere Suchanfragen mit Synonymen erzeugen lassen und die Ergebnisse zusammenführen.

### 🔴 Profi

7. **Review als Datei:** Den fertigen Überblick als Markdown-Datei mit Literaturliste speichern (*Write File*).
8. **Qualität vergleichen:** Denselben Flow mit dem lokalen Modell und dem Cluster-Modell laufen lassen. Was ändert sich?
9. **Agent-Variante:** Einen Agenten bauen, der selbst entscheidet, wann er genug Literatur gefunden hat.

### Zum Diskutieren

- Text- und Data-Mining ist in Deutschland für die wissenschaftliche Forschung erlaubt (§ 60d UrhG, allgemein § 44b UrhG). Was bedeutet das für Bibliotheken als Dienstleister?
- Welche Verzerrungen entstehen, wenn nur frei zugängliche Volltexte ausgewertet werden?
- Kann eine KI eine Forschungslücke erkennen, oder nur eine Lücke in den gefundenen Texten?

---

## Challenge D: Eure eigene Idee

Ihr habt ein Problem aus dem Bibliotheksalltag, das euch schon lange ärgert? Baut dafür einen Flow. Ein paar Anregungen:

- **Anfragen beantworten:** Aus einer E-Mail-Anfrage einen Antwortentwurf machen, der passende Bücher aus dem Katalog nennt.
- **Metadaten aus dem Titelblatt:** Aus dem PDF einer Dissertation Titel, Autor:in, Jahr, Institution und Schlagwörter für die Katalogisierung herausziehen (*Structured Output*).
- **Leichte Sprache:** Benutzungsordnung oder Webseite der Bibliothek in Leichte Sprache übersetzen (*URL* + *KI-Modell*).
- **Neuerwerbungen vorstellen:** Aus einer Liste von ISBNs kurze Buchvorstellungen für Social Media schreiben.
- **Open-Access-Beratung:** Zu einer Liste von DOIs prüfen, welche frei verfügbar sind und wo.

---

## Präsentation (5 Minuten pro Gruppe)

1. **Problem:** Wer hat das Problem, und warum ist es wichtig? (1 Minute)
2. **Demo:** Den Flow live zeigen, mit einem echten Beispiel. (2 Minuten)
3. **Grenzen:** Was klappt noch nicht? Wo irrt die KI? (1 Minute)
4. **Ausblick:** Würdet ihr das im Alltag einsetzen? Was bräuchte es dafür? (1 Minute)

Worauf die Jury achtet:

| Kriterium | Frage |
|---|---|
| Nutzen | Löst der Flow ein echtes Problem aus dem Bibliotheksalltag? |
| Funktion | Läuft er, und kommt ein brauchbares Ergebnis heraus? |
| Verlässlichkeit | Wie geht der Flow mit Fehlern der KI um? Wird geprüft statt geraten? |
| Verantwortung | Wurden Datenschutz, Urheberrecht und Transparenz bedacht? |
| Kreativität | Gibt es eine überraschende Idee oder Kombination? |
