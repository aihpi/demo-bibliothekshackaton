# L7 Verzweigen und absichern

Bisher liefen die Flows immer gleich ab: Jeder Baustein kam einmal dran, in derselben Reihenfolge. In der Auskunft ist das selten so. Eine Frage zur Verlängerung gehört an die Ausleihe, ein VPN-Problem an die IT, eine Recherchefrage an die Fachreferate. Manche Anfragen enthalten Daten, die nicht an einen KI-Dienst gehen sollen, und manche Antworten sollte ein Mensch lesen, bevor sie verschickt werden. Dieser Flow zeigt die Bausteine dafür: Weichen, die Anfragen auf einen von mehreren Wegen schicken, eine Prüfung vor der KI und eine Freigabe durch einen Menschen.

| | |
| --- | --- |
| **Ihr lernt** | Mit einer festen Regel verzweigen (If-Else) und mit einer KI-Entscheidung (Smart Router), Anfragen auf heikle Inhalte prüfen (Guardrails), einen Entwurf von einem Menschen freigeben lassen (Human Input). Und: wann eine Regel reicht und wann die KI entscheiden sollte. |
| **Bausteine** | If-Else, Smart Router, Guardrails, Human Input, dazu Chat Input, Chat Output, Prompt Template und KI-Modell |
| **KI** | ja: für Smart Router und den Antwortentwurf, in Übung 5 auch für Guardrails |
| **Dauer** | etwa 60 Minuten |
| **Testdaten** | `daten/lernpfad/auskunftsanfragen.txt` |

## Inhalt

1. [Der Flow im Überblick](#1-der-flow-im-überblick)
2. [Vorbereiten](#2-vorbereiten)
3. [Schritt für Schritt](#3-schritt-für-schritt)
4. [Übungen](#4-übungen)
5. [Wann nehme ich was?](#5-wann-nehme-ich-was)
6. [Wenn etwas nicht klappt](#6-wenn-etwas-nicht-klappt)

## 1. Der Flow im Überblick

Eine Anfrage kommt über den **Chat Input** in den Flow und läuft dann zwei Wege gleichzeitig. So könnt ihr die Regel und die KI an derselben Anfrage vergleichen. Die Bausteine tragen ihre Standardnamen; wo zwei gleiche Bausteine Verschiedenes tun, sagt eine kleine gelbe Notiz darüber, wofür sie da sind.

**Oben: eine feste Regel.**

| Baustein | Was er tut |
| --- | --- |
| **If-Else** (Notiz *Regel: Fernleihe?*) | Prüft, ob in der Anfrage das Wort *Fernleihe* vorkommt, und schickt sie auf den Weg *True* oder *False* |
| zwei **Chat Output** (Absender *Regel (If-Else)*) | Zeigen, welcher Weg genommen wurde: der obere hängt an *True*, der untere an *False* |

**Unten: die Auskunfts-Weiche.**

| Baustein | Was er tut |
| --- | --- |
| **Guardrails** | Hält Anfragen mit E-Mail-Adressen, Zugangsdaten oder Manipulationsversuchen an (Ausgang *Fail*), alle anderen gehen weiter (Ausgang *Pass*) |
| **Smart Router** | Lässt die KI entscheiden, ob die Anfrage zu *Ausleihe*, *Recherche*, *Technik* oder zu keiner davon gehört (*Else*) |
| **KI-Modell** (Notiz *Modell für die Weiche*) | Das Modell, mit dem der Smart Router entscheidet |
| drei **Chat Output** (Absender *Weg: Ausleihe*, *Weg: Technik*, *Weg: Sonstiges*) | Zeigen die Anfrage auf ihrem Weg. Bei *Technik* steht dort ein fester Text für die Weiterleitung. |
| **Prompt Template** + **KI-Modell** (Notiz *Modell für den Antwortentwurf*) | Schreiben bei *Recherche* einen Antwortentwurf |
| **Human Input** | Hält den Flow an, zeigt euch den Entwurf und wartet, bis ihr *Freigeben* oder *Ablehnen* wählt |
| zwei **Chat Output** (Absender *Freigegeben* und *Abgelehnt*) | Zeigen den Entwurf auf dem gewählten Weg |

Wichtig für das ganze Modul: **Ein Weg, der nicht genommen wird, läuft gar nicht.** Seine Bausteine werden nicht ausgeführt, und sein Chat Output zeigt im Playground nichts. Darum erscheinen pro Anfrage meist nur zwei Nachrichten: eine von der Regel und eine von der Weiche.

## 2. Vorbereiten

1. In der Übersicht von Langflow beim Flow **L7 Verzweigen und absichern** auf die drei Punkte klicken → *Duplicate*. Arbeitet in der Kopie.
2. Öffnet `daten/lernpfad/auskunftsanfragen.txt` im Texteditor. Die Datei enthält zehn ausgedachte Anfragen, jede mit einer Nummer in eckigen Klammern. Die Übungen nennen sie nach dieser Nummer, z. B. Anfrage [3].
3. Oben rechts auf **Playground** klicken, Anfrage [1] (ohne die Zeile mit der Nummer) einfügen und abschicken. Es erscheinen zwei Nachrichten: *Regel trifft nicht zu …* und die Anfrage selbst unter dem Absender *Weg: Ausleihe*.

Die KI-Modelle stehen auf *Standard (aus .env)*. Mit einem kleinen lokalen Modell entscheidet die Weiche unzuverlässiger; nehmt für dieses Modul am besten den Cluster (im KI-Modell die **Quelle** auf *Cluster (LiteLLM)* stellen, in beiden KI-Modell-Bausteinen).

Für jede neue Anfrage im Playground links mit **+** eine neue Sitzung beginnen, dann bleiben die Ergebnisse übersichtlich.

## 3. Schritt für Schritt

### 3.1 If-Else: eine feste Regel

*If-Else* vergleicht einen Text mit einem Wert und schickt ihn auf einen von zwei Wegen: **True**, wenn die Bedingung erfüllt ist, sonst **False**. Es ist keine KI beteiligt. Dieselbe Anfrage nimmt also immer denselben Weg, und das kostet nichts und geht sofort.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Text Input** | am Baustein | Der zu prüfende Text, hier die Anfrage |
| **Operator** | am Baustein | Wie verglichen wird: *equals* (genau gleich), *not equals*, *contains* (enthält), *starts with*, *ends with*, *regex* (ein Suchmuster) oder für Zahlen *less than*, *less than or equal*, *greater than*, *greater than or equal* |
| **Match Text** | am Baustein | Womit verglichen wird, hier `Fernleihe` |
| **Case Sensitive** | *Parameters* | Groß- und Kleinschreibung beachten. Standard: an. Bei *regex* verschwindet die Einstellung; dort zählt die Schreibung immer. |
| **Case True** / **Case False** | *Parameters* | Ein eigener Text, der statt der Anfrage weitergegeben wird. Leer: die Anfrage selbst geht weiter. Im Flow stehen dort die Sätze *Regel trifft zu …* und *Regel trifft nicht zu …*. |
| **Max Iterations**, **Default Route** | *Parameters* | Nur wichtig, wenn ein Flow im Kreis über If-Else zurückläuft: Nach so vielen Runden geht er auf dem *Default Route* weiter. Im Lernpfad ohne Wirkung. |

**Zahlen vergleichen:** Bei den Zahl-Operatoren müssen beide Seiten Zahlen sein, z. B. `25` und `40`. Steht etwas anderes im Text, etwa `25 Bücher`, ist die Bedingung nicht erfüllt, und es geht über *False* weiter.

**Suchmuster (regex):** Ein regulärer Ausdruck beschreibt ein Muster, z. B. `\d{4}` für vier Ziffern hintereinander. Langflow prüft das Muster **ab dem Anfang des Textes**. Steht das Gesuchte irgendwo mitten im Text, setzt ihr `.*` davor (`.*` heißt „beliebig viele beliebige Zeichen“).

### 3.2 Smart Router: die KI entscheidet

*Smart Router* gibt die Anfrage zusammen mit euren Kategorien an ein KI-Modell und fragt: Welche Kategorie passt? Jede Kategorie bekommt einen eigenen Ausgang. Anders als If-Else versteht die KI den Sinn einer Anfrage, auch wenn ein bestimmtes Wort fehlt. Dafür kostet jede Entscheidung einen Modellaufruf, und das Ergebnis kann sich von Lauf zu Lauf unterscheiden.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Language Model** | am Baustein | Hier ist der Ausgang *Language Model* vom **KI-Modell** für die Weiche angeschlossen. Ohne Modell kann die Weiche nicht entscheiden. |
| **Input** | am Baustein | Der einzuordnende Text |
| **Routes** | am Baustein, *Open table* | Die Kategorien, eine pro Zeile (siehe unten) |
| **Include Else Output** | *Parameters* | Ein zusätzlicher Ausgang *Else* für Anfragen, die zu keiner Kategorie passen. Im Flow eingeschaltet. |
| **Additional Instructions** | *Parameters* | Zusätzliche Regeln für die Entscheidung, in euren eigenen Worten. Geschweifte Klammern nur für die Platzhalter `{input_text}` (die Anfrage) und `{routes}` (die Kategorien) verwenden. |
| **Override Output** | *Parameters* | Ein Text, der auf **jedem** Weg statt der Anfrage weitergegeben wird |

Die Tabelle **Routes** hat drei Spalten:

| Spalte | Was hineingehört |
| --- | --- |
| **Route Name** | Der Name der Kategorie, z. B. *Ausleihe*. Er wird auch der Name des Ausgangs. |
| **Route Description** | Wann die Kategorie passt, z. B. *Fragen zu Ausleihe, Verlängerung, Vormerkung, Gebühren, Konto und Bibliotheksausweis*. Davon hängt die Entscheidung am meisten ab. |
| **Route Message (Optional)** | Ein fester Text, der statt der Anfrage weitergegeben wird. Im Flow bei *Technik*: der Hinweis auf den IT-Service. Leer: die Anfrage geht weiter. |

**Ohne Else-Ausgang** passiert bei einer Anfrage, die in keine Kategorie passt, gar nichts: Kein Ausgang gibt etwas weiter, und im Playground erscheint von der Weiche keine Nachricht.

Das **KI-Modell** für die Weiche steht auf *Kreativität* 0. Für Entscheidungen ist das richtig: Das Modell soll bei derselben Anfrage möglichst dasselbe sagen.

### 3.3 Guardrails: prüfen, bevor die KI die Anfrage sieht

Anfragen von Nutzer:innen enthalten oft Namen, E-Mail-Adressen oder Ausweisnummern. Bevor so etwas an einen externen KI-Dienst geht, sollte es auffallen. *Guardrails* prüft einen Text auf solche Inhalte und gibt ihn dann an einem von zwei Ausgängen weiter.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Input Text** | am Baustein | Der zu prüfende Text |
| **Guardrails** | am Baustein | Worauf geprüft wird: *PII* (personenbezogene Daten), *Tokens/Passwords* (Zugangsdaten), *Jailbreak* und *Prompt Injection* (Versuche, die KI zu manipulieren), *Offensive Content*, *Malicious Code* und weitere. Im Flow die ersten vier. |
| **Checking Method** | am Baustein | *Rules only*: feste Muster, ohne KI. *AI checks*: ein KI-Modell beurteilt den Text. *Rules + AI*: zuerst die Muster, dann das Modell. Im Flow: *Rules only*. |
| **Language Model** | am Baustein | Nur bei *AI checks* und *Rules + AI* nötig und sichtbar. Ohne Modell meldet der Baustein *Select or connect a Language Model, or choose Rules only*. |
| **Action for Flagged Text** | *Parameters*, nur bei *Rules only* und *Rules + AI* | Was mit einem auffälligen, aber nicht eindeutigen Fund geschieht: *block* (anhalten, Standard), *sanitize* (die gefundene Stelle unkenntlich machen und weitergeben) oder *pass_through* (unverändert weitergeben) |
| **Strictness** | *Parameters* | Wie schnell der Baustein anhält. Die Voreinstellung passt für den Anfang. |

Die Ausgänge:

| Ausgang | Was herauskommt |
| --- | --- |
| **Pass** | Die Anfrage selbst, wenn nichts gefunden wurde |
| **Fail** | Nicht die Anfrage, sondern eine Begründung auf Englisch, z. B. *PII: The input contains personal identifiable information …* |
| **Result Data** | Einzelheiten als JSON: Punktzahl je Prüfung, was gefunden wurde, ob ein Modell beteiligt war |

**Die drei Prüfmethoden unterscheiden sich deutlich.** Wir haben sie mit den Testanfragen ausprobiert:

| Anfrage | Rules only | Rules + AI und AI checks |
| --- | --- | --- |
| [7] mit E-Mail-Adresse und Ausweisnummer | angehalten (die E-Mail-Adresse; die Ausweisnummer erkennt keine Regel) | angehalten |
| [8] mit dem Passwort *Sommer2026!* | geht durch | angehalten |
| [9] Manipulationsversuch auf Deutsch | geht durch | angehalten |
| eine Anfrage, die nur einen Namen enthält | geht durch | angehalten |
| [1] ohne persönliche Daten | geht durch | geht durch |

*Rules only* kennt nur feste Muster wie E-Mail-Adressen und typische Schlüssel. Was nicht in ein Muster passt, rutscht durch. Die KI-Methoden finden mehr, halten aber auch Anfragen an, die nur einen Namen enthalten, also fast jede echte Anfrage mit Unterschrift. Wie streng ihr prüft, ist eine Entscheidung eures Hauses, keine technische.

### 3.4 Human Input: ein Mensch entscheidet

*Human Input* hält den Flow an und lässt einen Menschen entscheiden. Er zeigt einen Text, hier den Antwortentwurf der KI, und bietet Knöpfe zur Auswahl an. Erst wenn jemand einen Knopf drückt, geht es weiter, und zwar nur am Ausgang der gewählten Antwort.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Input** | am Baustein | Was sich der Mensch ansehen soll, hier der Entwurf aus dem **KI-Modell** für den Antwortentwurf |
| **User Choices** | am Baustein | Die möglichen Antworten. Standard: *Approve* und *Reject*; im Flow *Freigeben* und *Ablehnen*. Jede Antwort wird ein eigener Ausgang. Eigene lassen sich eintippen. |
| **Enable Fallback** | *Parameters* | Ein zusätzlicher Ausgang *fallback* für den Fall, dass niemand rechtzeitig antwortet. Dann erscheint auch **Timeout** (Standard: 3 Tage). |

Über welchen Ausgang der Entwurf weitergeht, entscheidet allein der Knopf. Der Text bleibt derselbe: Auch der **Chat Output** *Abgelehnt* zeigt den Entwurf, nur eben auf dem Weg für Ablehnungen. In einem echten Flow hinge dort z. B. ein zweiter Versuch mit anderem Prompt oder eine Weiterleitung an eine Person.

## 4. Übungen

🟢 Ausprobieren · 🟡 Umbauen · 🔴 Selbst bauen. Die Lösungen lassen sich aufklappen. Die Ergebnisse der KI können bei euch etwas anders ausfallen.

### 🟢 1. Regel und KI an denselben Anfragen

Schickt nacheinander die Anfragen [4], [5] und [6] ab (jede in einer neuen Sitzung). Was sagt die Regel, was die Weiche? Wo liegt die Regel falsch?

<details>
<summary>Lösung</summary>

- [4] *Geht das über die Fernleihe?*: Die Regel trifft zu. Die Weiche schickt die Anfrage zu *Ausleihe*, weil es keine Kategorie *Fernleihe* gibt und die Fernleihe der Ausleihe am nächsten liegt.
- [5] *wie lange dauert eine fernleihe*: Die Regel trifft **nicht** zu, weil *fernleihe* kleingeschrieben ist und *Case Sensitive* an ist. Die Weiche erkennt die Frage trotzdem (*Ausleihe*).
- [6] *Das Formular für die Fernleihe lädt nicht*: Die Regel trifft zu, obwohl es eigentlich ein technisches Problem ist. Die Weiche schickt die Anfrage richtig zu *Technik*.

Eine Regel prüft Wörter, die KI den Sinn. Die Regel irrt sich vorhersehbar, die KI manchmal überraschend.

</details>

### 🟢 2. Groß- und Kleinschreibung

Schaltet im **If-Else** unter *Parameters* **Case Sensitive** aus und schickt Anfrage [5] noch einmal ab.

<details>
<summary>Lösung</summary>

Jetzt trifft die Regel zu: Text und *Match Text* werden vor dem Vergleich in Kleinbuchstaben umgewandelt. Für Wörter in Anfragen von Menschen ist *Case Sensitive* aus fast immer die bessere Wahl. Für Codes, Signaturen oder Abkürzungen, bei denen die Schreibung etwas bedeutet, lasst es an.

</details>

### 🟢 3. Was Guardrails findet

Schickt die Anfragen [7], [8] und [9] ab. Welche hält *Guardrails* an? Klickt nach [7] am Baustein **Guardrails** auf das Ausgabe-Symbol von **Result Data** und seht nach, was gefunden wurde.

<details>
<summary>Lösung</summary>

Nur [7] wird angehalten: Unter dem Absender *Guardrails* erscheint die englische Begründung *PII: The input contains personal identifiable information …*. In *Result Data* steht bei *PII* der Fund `EMAIL`; die Ausweisnummer hat keine Regel erkannt.

[8] und [9] gehen durch: *Rules only* kennt kein Muster für ein ausgedachtes Passwort wie *Sommer2026!* und keine deutschsprachigen Manipulationsversuche. [8] landet bei *Ausleihe*, [9] meist bei *Technik*. Das Passwort ginge also an die KI weiter.

</details>

### 🟢 4. Freigeben und ablehnen

Schickt Anfrage [2] (Recherche) ab. Lest den Entwurf und klickt auf **Freigeben**. Schickt dieselbe Anfrage in einer neuen Sitzung noch einmal ab und klickt diesmal auf **Ablehnen**.

<details>
<summary>Lösung</summary>

Der Flow hält beim **Human Input** an und zeigt den Entwurf. Nach *Freigeben* erscheint er unter dem Absender *Freigegeben*, nach *Ablehnen* unter *Abgelehnt*. Der Text ist beide Male der Entwurf; was sich ändert, ist der Weg. Außerdem: Der zweite Entwurf ist anders formuliert als der erste. Das Modell schreibt bei jedem Lauf neu.

</details>

### 🟡 5. Guardrails mit KI

1. Verbindet den Ausgang **Language Model** vom **KI-Modell** für die Weiche zusätzlich mit dem Eingang **Language Model** von **Guardrails**. Ein Ausgang darf mehrere Linien haben.
2. Stellt **Checking Method** auf *Rules + AI*.
3. Schickt [7], [8], [9] und [1] ab, dann diese Anfrage: *Mein Name ist Jonas Muster. Wann hat die Bibliothek samstags geöffnet?*

<details>
<summary>Lösung</summary>

[7], [8] und [9] werden jetzt alle angehalten, [1] geht durch. Die Anfrage mit dem Namen wird ebenfalls angehalten: Für die KI ist schon ein Name eine personenbezogene Angabe.

Das ist die eigentliche Frage dieser Übung: Wollt ihr jede Anfrage mit Namen anhalten? Mögliche Antworten: *PII* aus der Liste nehmen und nur Zugangsdaten und Manipulation prüfen; personenbezogene Daten vorher entfernen (Übung 6); oder für solche Anfragen ein lokales Modell nehmen, damit die Daten den Laptop nicht verlassen. Beachtet auch: Bei *AI checks* und *Rules + AI* liest das Modell die Anfrage, um sie zu prüfen. Die Prüfung schickt sie also selbst an den KI-Dienst.

</details>

### 🟡 6. Unkenntlich machen statt anhalten

Stellt *Guardrails* zurück auf *Rules only* (die Linie vom Modell könnt ihr lassen). Stellt unter *Parameters* **Action for Flagged Text** auf *sanitize* und schickt Anfrage [7] ab.

<details>
<summary>Lösung</summary>

Die Anfrage wird nicht mehr angehalten. Sie geht über *Pass* an die Weiche, aber die E-Mail-Adresse ist durch `[REDACTED:EMAIL]` ersetzt. Die Ausweisnummer steht noch da, weil keine Regel sie erkennt. Wie ihr sie selbst findet, zeigt Übung 9.

</details>

### 🟡 7. Eine neue Kategorie

1. Öffnet im **Smart Router** die Tabelle **Routes** (*Open table*) und fügt eine Zeile hinzu: *Route Name* `Fernleihe`, *Route Description* `Bestellungen von Medien aus anderen Bibliotheken`.
2. Am Baustein erscheint ein neuer Ausgang *Fernleihe*. Verbindet ihn mit einem neuen *Chat Output*.
3. Schickt [4] und [6] ab.
4. Tragt unter *Parameters* bei **Additional Instructions** ein: `Alles, was mit der Fernleihe zu tun hat, gehört zu Fernleihe, auch technische Probleme.` Schickt [6] noch einmal ab.

<details>
<summary>Lösung</summary>

[4] geht jetzt zu *Fernleihe*. [6] bleibt zunächst bei *Technik*, weil die Beschreibung von *Technik* (*Formulare*) besser passt. Mit der zusätzlichen Anweisung landet [6] bei *Fernleihe*. Beschreibungen und Anweisungen steuern die KI-Weiche; ihr formuliert sie in normaler Sprache, wie für eine neue Kollegin. Ob [6] zur Fernleihe oder zur IT gehört, ist übrigens keine Frage der KI, sondern eurer Abläufe.

</details>

### 🟡 8. Was weitergegeben wird

Leert im **If-Else** unter *Parameters* die Felder **Case True** und **Case False** und schickt [4] ab. Tragt danach im **Smart Router** unter *Parameters* bei **Override Output** `Danke, wir kümmern uns.` ein und schickt [3] ab.

<details>
<summary>Lösung</summary>

Ohne *Case True* gibt die Regel die Anfrage selbst weiter statt des Satzes *Regel trifft zu …*. Mit *Override Output* gibt die Weiche auf **jedem** Weg denselben Text weiter, auch bei *Technik*, wo sonst der Hinweis auf den IT-Service stand. *Override Output* ist darum selten das, was man will; für einen Text pro Weg ist *Route Message* in der Tabelle *Routes* da. Leert *Override Output* wieder.

</details>

### 🔴 9. Eine Regel für Ausweisnummern

Die Ausweisnummern der Musterbibliothek haben die Form `4711-0815-23`: vier Ziffern, Bindestrich, vier Ziffern, Bindestrich, zwei Ziffern. Baut mit einem zweiten *If-Else* eine Regel, die Anfragen mit einer solchen Nummer erkennt. Testet mit [7] und [1].

<details>
<summary>Lösung</summary>

Neuer *If-Else*, *Text Input* vom Chat Input, **Operator** *regex*, **Match Text** `.*\d{4}-\d{4}-\d{2}`, die Ausgänge *True* und *False* an je einen *Chat Output*. [7] geht über *True*, [1] über *False*.

`\d{4}` heißt „vier Ziffern“. Das `.*` am Anfang ist nötig, weil Langflow das Muster ab dem Anfang des Textes prüft; ohne `.*` passt es nur, wenn die Anfrage mit der Nummer beginnt.

Wer möchte, setzt diesen *If-Else* vor die *Guardrails*: *False* geht weiter an *Guardrails*, *True* an einen Chat Output *Bitte ohne Ausweisnummer schreiben*. So kombiniert ihr eine eigene Regel mit der fertigen Prüfung.

</details>

### 🔴 10. Zahlen vergleichen

Baut einen kleinen Flow: Im Playground tippt jemand ein, wie viele Medien er oder sie ausleihen möchte. Ist die Zahl größer als 40 (die Grenze aus `daten/lernpfad/benutzungsordnung.txt`), soll *Leider sind höchstens 40 Medien gleichzeitig möglich.* erscheinen, sonst *Das geht.* Probiert `12`, `41` und `41 Bücher`.

<details>
<summary>Lösung</summary>

**Chat Input** → **If-Else** mit **Operator** *greater than*, **Match Text** `40`, unter *Parameters* **Case True** `Leider sind höchstens 40 Medien gleichzeitig möglich.` und **Case False** `Das geht.` → *True* und *False* an je einen **Chat Output**.

`12` ergibt *Das geht.*, `41` die Absage. `41 Bücher` ergibt ebenfalls *Das geht.*, weil der Text keine reine Zahl ist und der Vergleich dann als nicht erfüllt gilt. Feste Regeln brauchen saubere Eingaben. Wie ihr die Zahl aus einem Satz herauszieht, zeigen [L2](L2_texte_aufbereiten.md) (*Text Extract*) und [L6](L6_strukturierte_antworten.md).

</details>

### 🔴 11. Eine dritte Wahl

Fügt im **Human Input** bei **User Choices** die Antwort `Überarbeiten` hinzu. Verbindet den neuen Ausgang mit einem **Prompt Template**, einem neuen **KI-Modell** und einem **Chat Output**. Das Template:

```text
Überarbeite diesen Antwortentwurf: kürzer, freundlicher, mit einer Rückfrage am Ende.

{entwurf}
```

Probiert es mit Anfrage [2].

<details>
<summary>Lösung</summary>

Am Baustein erscheint ein dritter Ausgang *Überarbeiten*. Nach einem Klick auf *Überarbeiten* läuft nur dieser Weg: Der Entwurf geht an den Prompt, das Modell schreibt eine neue Fassung, und sie erscheint im neuen Chat Output. Die neue Fassung wird nicht noch einmal geprüft. Wer das will, hängt hinter das zweite KI-Modell einen zweiten *Human Input*.

</details>

## 5. Wann nehme ich was?

| Ihr wollt … | Baustein | Hinweis |
| --- | --- | --- |
| nach einem Wort, einem Anfang oder einem Muster verzweigen | **If-Else** | Schnell, kostenlos, immer gleich. Erkennt aber nur, was ihr genau beschreiben könnt. |
| nach einer Zahl verzweigen | **If-Else** mit *greater than* usw. | Der Text muss eine reine Zahl sein |
| nach dem Sinn einer Anfrage verzweigen | **Smart Router** | Versteht Umschreibungen und Tippfehler. Kostet einen Modellaufruf pro Anfrage und kann sich irren. *Include Else Output* einschalten. |
| zwischen genau zwei Wegen nach dem Sinn wählen | **Smart Router** mit zwei Kategorien | If-Else kann den Sinn nicht prüfen |
| bekannte heikle Muster finden (E-Mail-Adressen, Schlüssel) | **Guardrails** mit *Rules only* | Ohne KI, nichts verlässt den Laptop. Findet nur bekannte Muster. |
| auch Umschreibungen und Manipulationsversuche finden | **Guardrails** mit *Rules + AI* oder *AI checks* | Das Modell liest die Anfrage selbst. Sehr streng bei Namen. |
| eigene Muster finden (Ausweisnummern, Signaturen) | **If-Else** mit *regex* | Mit `.*` davor, wenn das Muster mitten im Text steht |
| dass ein Mensch vor dem Versenden entscheidet | **Human Input** | Hält den Flow an, bis jemand wählt |

**Regel oder KI?** Lässt sich die Bedingung so genau beschreiben, dass ihr sie einer Aushilfe als Liste von Wörtern geben könntet, reicht If-Else. Müsstet ihr der Aushilfe erklären, *worum es geht*, braucht ihr den Smart Router. Oft ist die Kombination am besten: zuerst feste Regeln für die klaren Fälle, danach die KI für den Rest.

## 6. Wenn etwas nicht klappt

| Meldung oder Problem | Ursache und Lösung |
| --- | --- |
| Von der Weiche erscheint keine Nachricht | Die Anfrage passt in keine Kategorie, und *Include Else Output* ist aus. Einschalten und den Ausgang *Else* verbinden. Oder *Guardrails* hat die Anfrage angehalten: Dann steht etwas unter dem Absender *Guardrails*. |
| Ein Chat Output bleibt leer | Sein Weg wurde nicht genommen. Das ist so gewollt. |
| *Select or connect a Language Model, or choose Rules only …* | *Guardrails* steht auf *AI checks* oder *Rules + AI*, aber kein Modell ist angeschlossen |
| Die Weiche entscheidet anders als erwartet | Die *Route Description* genauer formulieren oder *Additional Instructions* ergänzen. Mit einem kleinen lokalen Modell den Cluster nehmen. |
| Eine neue Kategorie kommt nie an | Ihr neuer Ausgang am Smart Router ist noch nicht mit einem Chat Output verbunden. Ohne *Route Name* heißt der Ausgang *Category* mit einer Nummer. |
| Die Regel mit *regex* greift nie | Das Muster wird ab dem Textanfang geprüft: `.*` davorsetzen |
| Der Vergleich mit *greater than* stimmt nicht | Im Text steht mehr als eine Zahl |
| Der Flow hält an und es geht nicht weiter | *Human Input* wartet auf eure Wahl. Im Playground den Knopf *Freigeben* oder *Ablehnen* drücken. |
| Die Begründung von *Guardrails* ist englisch | Das ist fest eingebaut. Für eine deutsche Antwort setzt ein *Prompt Template* zwischen *Fail* und den Chat Output, z. B. mit dem Template `Ihre Anfrage enthält Angaben, die wir nicht weitergeben. Bitte schreiben Sie uns ohne persönliche Daten. (Grund: {grund})`. Der Platzhalter ist nötig, damit das Template am Ausgang *Fail* hängt und nur auf diesem Weg läuft. |

**Weiter:** [L8 Wiederholen mit Loop](L8_wiederholen_mit_loop.md) zeigt, wie ein Flow eine ganze Liste Eintrag für Eintrag abarbeitet.
