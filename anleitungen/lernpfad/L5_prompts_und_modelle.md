# L5 Prompts und Modelle

Ab diesem Modul arbeitet ein Sprachmodell mit. Was es antwortet, hängt von zwei Dingen ab: vom **Prompt**, also dem Text, den es bekommt, und von den **Einstellungen des Modells**. Dieser Flow beantwortet Fragen zur Benutzungsordnung einer Bibliothek. Ihr verändert Schritt für Schritt Prompt und Einstellungen und seht, was sich an der Antwort ändert.

| | |
| --- | --- |
| **Ihr lernt** | Prompts mit mehreren Platzhaltern bauen, das KI-Modell einstellen (Quelle, Kreativität, Antwortlänge, System Message), den Standard-Baustein Language Model nutzen, einem Flow ein Gedächtnis geben, das Datum mitschicken. Und: wie ihr das Modell dazu bringt, nichts zu erfinden. |
| **Bausteine** | Chat Input, Prompt Template, KI-Modell, Language Model, Message History, Current Date, Chat Output, LLM Selector (Übung) |
| **KI** | ja |
| **Dauer** | etwa 60 Minuten |
| **Testdaten** | `daten/lernpfad/benutzungsordnung.txt` (steckt schon im Flow) |

## Inhalt

1. [Der Flow im Überblick](#1-der-flow-im-überblick)
2. [Vorbereiten](#2-vorbereiten)
3. [Schritt für Schritt](#3-schritt-für-schritt)
4. [Übungen](#4-übungen)
5. [Wann nehme ich was?](#5-wann-nehme-ich-was)
6. [Wenn etwas nicht klappt](#6-wenn-etwas-nicht-klappt)

## 1. Der Flow im Überblick

Eine Nutzerin fragt im Playground etwas zur Bibliothek, z. B. *Wie lange darf ich ein Buch behalten?* Der Flow baut daraus einen Prompt und lässt ihn zweimal beantworten:

| Schritt | Baustein | Was er tut |
| --- | --- | --- |
| 1 | **Frage (Chat)** – Chat Input | nimmt die Frage aus dem Playground |
| 2 | **Heutiges Datum** – Current Date | liefert Datum und Uhrzeit |
| 3 | **Bisheriges Gespräch** – Message History | liefert die letzten Nachrichten dieser Sitzung |
| 4 | **Prompt: Auskunft** – Prompt Template | setzt Benutzungsordnung, Datum, Gespräch, Zielgruppe und Frage zu einem Text zusammen |
| 5 | **KI-Modell (Auskunft)** – KI-Modell | beantwortet den Prompt; die Antwort erscheint oben im Playground |
| 6 | **Language Model (Leichte Sprache)** – Language Model | beantwortet denselben Prompt mit demselben Modell, aber mit einer eigenen Anweisung: in Leichter Sprache |

Alle Bausteine hängen am Chat Input oder liefern etwas an einen Baustein, der daran hängt. Darum läuft im Playground der ganze Flow (siehe [L1](L1_daten_importieren.md), Übung 6).

## 2. Vorbereiten

1. In der Übersicht beim Flow **L5 Prompts und Modelle** auf die drei Punkte → *Duplicate*. Arbeitet in der Kopie.
2. **Playground** öffnen und fragen: *Wie lange darf ich ein Buch behalten, und was kostet es, wenn ich es zu spät zurückbringe?*
3. Nach einigen Sekunden erscheinen zwei Antworten: oben vom KI-Modell, darunter in Leichter Sprache. Beide nennen die Paragrafen 3 und 5.
4. Fragt nach: *Und wie oft kann ich verlängern?* Der Flow kennt das bisherige Gespräch.

**Welches Modell antwortet?** Der Baustein *KI-Modell* steht auf *Standard (aus .env)*. Was das heißt, legt die Orga in der Datei `.env` fest: den Cluster oder ein lokales Modell auf dem Laptop. Für dieses Modul empfehlen wir den **Cluster**: Stellt im KI-Modell die **Quelle** auf *Cluster (LiteLLM)*. Ein kleines lokales Modell braucht für jede Antwort deutlich länger, und die Übungen dauern dann sehr lange.

**Nach jeder Änderung neu fragen.** Ein Baustein lässt sich auch hier mit ▶ einzeln ausführen. Für das Modell braucht er aber eine Frage aus dem Playground. Am einfachsten ist es, nach jeder Änderung im Playground eine Frage abzuschicken. Den fertigen Prompt seht ihr danach am Ausgang des Bausteins *Prompt: Auskunft*: Klickt auf das kleine Symbol rechts unten am Baustein.

## 3. Schritt für Schritt

### 3.1 Prompt Template: der Text für das Modell

Der Prompt ist alles, was das Modell über die Aufgabe weiß. *Prompt Template* setzt ihn aus festem Text und **Platzhaltern** in geschweiften Klammern zusammen. Für jeden Platzhalter bekommt der Baustein links einen **Eingang** mit demselben Namen. Der Prompt in diesem Flow hat fünf:

| Platzhalter | Woher der Inhalt kommt |
| --- | --- |
| `{ordnung}` | fester Text, direkt im Feld eingetragen: die Benutzungsordnung |
| `{heute}` | verbunden mit *Heutiges Datum* |
| `{verlauf}` | verbunden mit *Bisheriges Gespräch* |
| `{zielgruppe}` | fester Text: *Studierende im ersten Semester* |
| `{frage}` | verbunden mit *Frage (Chat)* |

Ein Platzhalter kann also **verbunden** sein oder einen **festen Text** haben, den ihr direkt in sein Feld tippt. Ist eine Linie angeschlossen, zählt nur die Linie; das Feld zeigt dann *Receiving input*.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Template** | am Baustein | Der Text mit Platzhaltern. Ein Klick öffnet ein großes Eingabefeld. Neuer Platzhalter = neuer Eingang. |
| *ein Feld pro Platzhalter* | am Baustein | Fester Text oder eine Verbindung |
| **Use Double Brackets** | *Parameters* | Platzhalter in doppelten Klammern `{{frage}}` statt `{frage}`. Nötig, wenn der Prompt selbst geschweifte Klammern enthält, z. B. ein JSON-Beispiel (Übung 9). |

**Der Aufbau des Prompts.** Oben stehen die Daten (Benutzungsordnung, Datum, Gespräch), darunter nach `---` die Anweisung, ganz unten die Frage. Bei langen Daten wirkt eine Anweisung am Schluss zuverlässiger als eine am Anfang, die das Modell nach vielen Seiten Text aus dem Blick verliert. Die Anweisung enthält vier Bausteine, die in fast jeden guten Prompt gehören:

- **Rolle:** *Du bist Auskunftsperson der Musterbibliothek.*
- **Aufgabe und Zielgruppe:** *Beantworte die NEUE FRAGE für {zielgruppe}.*
- **Grenzen:** *Stütze dich nur auf die Benutzungsordnung … Steht die Antwort nicht darin, sag das ehrlich … Erfinde nichts.*
- **Format:** *Antworte auf Deutsch in höchstens vier Sätzen.*

### 3.2 KI-Modell: das Sprachmodell

*KI-Modell* (Kategorie *Bibliothek*) schickt den Prompt an ein Sprachmodell und gibt die Antwort als Message weiter. Adresse und Schlüssel kommen aus der `.env`; ihr müsst nichts eintragen.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Quelle** | am Baustein | *Standard (aus .env)*, *Cluster (LiteLLM)* oder *Lokal (Ollama)* |
| **Modell** | am Baustein | Leer: das Standardmodell der Quelle. Mit dem Pfeil-Knopf daneben die verfügbaren Modelle laden und eines wählen. |
| **Kreativität (Temperatur)** | am Baustein | 0 = sachlich, möglichst gleiche Antworten; 1 = abwechslungsreich. Standard: 0,1. |
| **System Message** | am Baustein | Eine Anweisung, die getrennt vom Prompt mitgeht, siehe 3.4 |
| **Maximale Antwortlänge (Tokens)** | *Parameters* | Höchstens so viele Tokens (etwa ¾ Wort pro Token). 0 = keine Grenze. Was darüber hinausgeht, wird abgeschnitten. |
| **Nachdenken erlauben** | *Parameters* | Erlaubt lokalen „Reasoning“-Modellen, vor der Antwort nachzudenken. Genauer, aber langsamer. Wirkt **nur bei Quelle Lokal**; das Cluster-Modell entscheidet selbst. |
| **Zeitlimit (Sekunden)** | *Parameters* | Wie lange auf eine Antwort gewartet wird. Standard: 600. |
| **Adresse**, **API-Schlüssel** (überschreiben) | *Parameters* | Nur, um ein anderes Modell als das aus der `.env` anzuschließen, z. B. einen KI-Zugang eurer Einrichtung |

Der Baustein hat zwei Ausgänge: **Model Response** ist die Antwort als Text. **Language Model** ist das eingerichtete Modell selbst, ohne Antwort. Diesen Ausgang verbindet ihr mit Bausteinen, die selbst ein Modell brauchen: Language Model (3.3), Agent, Batch Run, Structured Output, Smart Router und andere.

### 3.3 Language Model: der Standard-Baustein

*Language Model* (Kategorie *Models & Agents*) ist Langflows eigener Baustein für Sprachmodelle. Er hat dieselben Ausgänge wie KI-Modell. Seine Anbieter (OpenAI, Anthropic, Google und andere) brauchen aber jeweils ein eigenes Konto und einen Schlüssel, und die sind in diesem Projekt **nicht eingerichtet**.

Trotzdem könnt ihr ihn nutzen: Sein Feld **Language Model** nimmt auch eine Verbindung an. Im Flow ist dort der Ausgang *Language Model* von **KI-Modell (Auskunft)** angeschlossen. Wählt ihr das Feld in einem neuen Language Model aus, findet ihr dafür in der Liste den Eintrag *Connect other models*.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Language Model** | am Baustein | Anbieter und Modell, oder eine Verbindung von KI-Modell |
| **Input** | am Baustein | Der Prompt |
| **System Message** | am Baustein | Wie bei KI-Modell. Im Flow: *Du schreibst in Leichter Sprache …* |
| **Temperature**, **Max Tokens** | *Parameters* | Gelten nur für die eigenen Anbieter. Ist ein KI-Modell angeschlossen, zählen **dessen** Kreativität und Antwortlänge (Übung 7). |

Wozu dann zwei Bausteine? So seht ihr, wie die Standard-Bausteine ein Modell bekommen, und könnt eine Antwort mit einer anderen System Message vergleichen, ohne ein zweites Modell einzurichten. Wo ihr einfach eine Antwort braucht, ist KI-Modell der einfachere Weg.

### 3.4 System Message oder Prompt?

Beide gehen an das Modell, aber in getrennten Rollen. Die **System Message** sagt, *wie* das Modell grundsätzlich arbeiten soll: Rolle, Ton, Sprache, Stil. Der **Prompt** sagt, *was* es jetzt tun soll, mit den Daten dafür. Modelle behandeln die System Message meist als übergeordnete Regel; widerspricht sie dem Prompt, gewinnt oft die System Message (Übung 6).

Im Flow bekommen beide Bausteine denselben Prompt. Der Unterschied der beiden Antworten kommt nur von der System Message des Language Model.

### 3.5 Message History: ein Gedächtnis für das Gespräch

Ein Sprachmodell erinnert sich an nichts: Jede Anfrage beginnt bei null. Damit eine Nachfrage wie *Und was kostet das?* verstanden wird, muss das bisherige Gespräch im Prompt stehen. Das liefert *Message History*.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Mode** | am Baustein | *Retrieve* liest gespeicherte Nachrichten (so im Flow). *Store* speichert eine Nachricht. |
| **Number of Messages** | *Parameters* | Wie viele der letzten Nachrichten. Im Flow 10, Standard 100. |
| **Sender Type** | *Parameters* | Nur Nachrichten der Nutzer:innen (*User*), nur die des Modells (*Machine*) oder beide |
| **Order** | *Parameters* | Älteste zuerst (*Ascending*) oder neueste zuerst |
| **Session ID** | *Parameters* | Aus welcher Sitzung. Leer: die aktuelle Sitzung im Playground. |

Zwei Ausgänge: **Messages** (Text, z. B. `User: …` und `KI-Modell: …` untereinander, für den Prompt) und **Table**.

**Was wird gespeichert?** Chat Input und Chat Output speichern jede Nachricht (*Store Messages* in ihren *Parameters*, standardmäßig an). Message History liest sie wieder aus. Im Flow speichert *Antwort (Leichte Sprache)* nicht, sonst stünde jede Antwort doppelt im Gespräch. Die aktuelle Frage steht übrigens schon im Verlauf, weil der Chat Input sie speichert, bevor Message History liest.

**Sitzungen.** Der Verlauf gehört zu einer **Sitzung** (*Session*). Im Playground startet ihr mit **+** links eine neue Sitzung: Der Verlauf ist dann leer.

### 3.6 Current Date: das heutige Datum

Ein Sprachmodell kennt das heutige Datum nicht von sich aus. Fragen wie *Bis wann muss ich das Buch zurückgeben?* braucht es aber. *Current Date* liefert Datum und Uhrzeit als Text.

| Einstellung | Wo | Was sie bewirkt |
| --- | --- | --- |
| **Timezone** | am Baustein | Die Zeitzone. Im Flow `Europe/Berlin`, Standard ist `UTC`. |

## 4. Übungen

🟢 Ausprobieren · 🟡 Umbauen · 🔴 Selbst bauen. Die Lösungen lassen sich aufklappen. Bei Sprachmodellen gibt es keine einzig richtige Antwort; die Lösungen beschreiben, was wir beim Ausprobieren beobachtet haben.

### 🟢 1. Kreativität

Fragt dreimal hintereinander, jeweils in einer neuen Sitzung (**+**): *Schreib einen einzigen Satz, der Studierende für die Fernleihe begeistert.* Stellt dann im KI-Modell die **Kreativität** auf *1* und fragt wieder dreimal. Danach zurück auf *0*.

<details>
<summary>Lösung</summary>

Mit dem Cluster-Modell sind die Sätze schon bei 0 nicht wörtlich gleich, und bei 1 wechseln Wortwahl und Anrede (du oder Sie) etwas stärker. Der Unterschied ist bei diesem Modell klein: Große Modelle, die vor der Antwort nachdenken, reagieren weniger auf die Temperatur. Die Fakten bleiben gleich, alle Sätze nennen die 1,50 Euro aus § 4.

Faustregel: für Auskünfte, Prüfungen und Daten eine niedrige Kreativität (0 bis 0,2), für Werbetexte und Ideen eine höhere (0,6 bis 1). Hohe Werte machen Erfindungen wahrscheinlicher.

</details>

### 🟢 2. Antwortlänge begrenzen

Öffnet im KI-Modell *Parameters* und setzt **Maximale Antwortlänge (Tokens)** auf `300`. Fragt: *Erkläre mir alle Gebühren ausführlich.* Setzt sie dann auf `30` und fragt *Wie lange darf ich ein Buch behalten?* Zum Schluss wieder `0`.

<details>
<summary>Lösung</summary>

Bei 300 bricht die Antwort mitten im Satz ab, oft mitten im Wort. Das Modell kürzt nicht klug, es wird einfach abgeschnitten. Bei 30 bleibt die Antwort des Cluster-Modells **leer**: Es denkt vor der Antwort nach, und das Nachdenken verbraucht die 30 Tokens, bevor ein Wort Antwort entsteht.

Die Antwortlänge ist also eine Notbremse, z. B. gegen ein kleines Modell, das endlos weiterschreibt (Flow 05 nutzt sie dafür). Kurze Antworten bekommt ihr über den Prompt: *in höchstens zwei Sätzen*.

</details>

### 🟢 3. Eine andere Zielgruppe

Ändert im *Prompt: Auskunft* das Feld **zielgruppe** und fragt jeweils: *Darf ich in der Bibliothek etwas essen?*

1. `Kinder im Grundschulalter`
2. `internationale Gastwissenschaftler:innen, auf Englisch`

<details>
<summary>Lösung</summary>

1. Die Antwort duzt, wird einfacher und erklärt mehr, z. B. dass Getränke in verschließbaren Flaschen erlaubt sind.
2. Die Antwort bleibt **deutsch**. Im Prompt steht weiter unten *Antworte auf Deutsch*, und diese feste Regel gewinnt gegen den Wunsch in der Zielgruppe. Widersprüchliche Anweisungen sind eine häufige Ursache für „das Modell ignoriert mich“. Ändert die letzte Zeile in *Antworte in der Sprache der Zielgruppe*, dann klappt es.

</details>

### 🟢 4. Wenn die Antwort nicht in den Daten steht

Fragt: *Hat die Bibliothek sonntags geöffnet?* Die Benutzungsordnung sagt dazu nichts.

Löscht dann im Template die beiden Sätze von *Stütze dich nur auf die Benutzungsordnung* bis *Erfinde nichts.* und fragt noch einmal, in einer neuen Sitzung.

<details>
<summary>Lösung</summary>

Mit der Regel sagt das Modell, dass die Benutzungsordnung keine Öffnungszeiten enthält, und verweist an die Information. Ohne die Regel antwortet es überzeugt, die Bibliothek sei sonntags „in der Regel geschlossen“, und schlägt Dinge vor, die nirgends stehen, z. B. eine E-Mail an ein Service-Team. Das ist eine **Halluzination**: erfunden, aber glaubwürdig formuliert.

Darum gehört in jeden Prompt, der mit eigenen Daten arbeitet, eine Grenze: *Verwende nur … Wenn etwas fehlt, sag es.* Und auch dann gilt: Stichproben prüfen. Setzt die Sätze danach wieder ein.

</details>

### 🟢 5. Das Gedächtnis

1. Fragt: *Kann ich ein Buch bestellen, das die Bibliothek nicht hat?*
2. Dann: *Und was kostet das?*
3. Startet mit **+** eine neue Sitzung und fragt nur *Und was kostet das?*

Seht euch nach Schritt 2 den Ausgang von *Bisheriges Gespräch* an.

<details>
<summary>Lösung</summary>

In Schritt 2 weiß das Modell, dass „das“ die Fernleihe ist, und nennt 1,50 Euro. Am Ausgang von *Bisheriges Gespräch* steht das ganze Gespräch, die aktuelle Frage eingeschlossen. In der neuen Sitzung ist der Verlauf leer: Das Modell rät, was gemeint ist, und zählt alle Gebühren der Benutzungsordnung auf.

</details>

### 🟡 6. System Message gegen Prompt

Tragt im **KI-Modell (Auskunft)** in das Feld **System Message** ein: `Antworte immer als Gedicht in vier Zeilen.` Fragt: *Wie lange darf ich ein Buch behalten?* Löscht die System Message danach wieder.

Probiert auch das Umgekehrte: Schreibt die Rolle (*Du bist Auskunftsperson der Musterbibliothek.*) aus dem Prompt in die System Message.

<details>
<summary>Lösung</summary>

Die Antwort kommt als Gedicht, mit den richtigen Fakten aus § 3. Die System Message setzt sich gegen *in höchstens vier Sätzen* aus dem Prompt durch. Die Antwort in Leichter Sprache bleibt normal: Das Language Model hat seine eigene System Message.

Die Rolle in der System Message wirkt wie im Prompt. Eine gute Aufteilung für eigene Flows: In die System Message, was für jede Anfrage gilt (Rolle, Ton, Sprache), in den Prompt die Daten und die konkrete Aufgabe.

</details>

### 🟡 7. Wer bestimmt die Einstellungen?

Öffnet im **Language Model (Leichte Sprache)** *Parameters* und setzt **Temperature** auf `1`. Fragt etwas. Setzt dann stattdessen im **KI-Modell (Auskunft)** die **Kreativität** auf `1`.

Wie findet ihr heraus, welche Temperatur wirklich gilt? Tipp: Seht euch nach dem Lauf den Ausgang *Language Model* des Language Model an.

<details>
<summary>Lösung</summary>

Der Ausgang *Language Model* zeigt die Einstellungen des Modells, das tatsächlich benutzt wird, darunter `temperature`. Dort steht der Wert aus dem **KI-Modell**, nicht der aus dem Language Model. Ist ein Modell angeschlossen, bringt es seine Einstellungen mit; *Temperature* und *Max Tokens* des Language Model gelten nur für dessen eigene Anbieter. Dasselbe gilt für alle Bausteine mit einem Eingang *Language Model*, etwa Agent oder Batch Run: Kreativität und Antwortlänge stellt ihr im KI-Modell ein.

</details>

### 🟡 8. Die Benutzungsordnung aus einer Datei

Im Flow steht die Benutzungsordnung als fester Text im Platzhalter `{ordnung}`. Ersetzt ihn durch eine Datei: Setzt **Read File** auf die Arbeitsfläche, ladet `daten/lernpfad/benutzungsordnung.txt` hoch und verbindet *Raw Content* mit dem Eingang **ordnung** des Prompts. Ändert in der Datei auf eurem Rechner vorher eine Regel, z. B. die Leihfrist auf drei Wochen, und ladet sie dann hoch.

<details>
<summary>Lösung</summary>

Das Modell nennt jetzt drei Wochen: Es weiß nur, was im Prompt steht. Read File liefert an den Prompt, und der Prompt hängt am Chat Input, darum läuft Read File im Playground mit (siehe [L1](L1_daten_importieren.md), Übung 6). Der Vorteil einer Datei: Wird die Ordnung geändert, ladet ihr die neue Fassung hoch, ohne den Prompt anzufassen. Der Nachteil: Ohne hochgeladene Datei bricht der Flow mit *No files to process* ab.

</details>

### 🟡 9. Geschweifte Klammern im Prompt

Ihr wollt die Antwort in einem festen Format. Ändert das Ende des Templates in:

```text
Antworte nur als JSON wie {"paragraf": "§ 3", "antwort": "..."}

NEUE FRAGE: {frage}
```

Was passiert links am Baustein? Schaltet dann unter *Parameters* **Use Double Brackets** ein und schreibt alle echten Platzhalter mit doppelten Klammern: `{{ordnung}}`, `{{heute}}`, `{{verlauf}}`, `{{zielgruppe}}`, `{{frage}}`.

<details>
<summary>Lösung</summary>

Mit einfachen Klammern hält Langflow `{"paragraf": "§ 3", "antwort": "..."}` für einen Platzhalter und legt links einen unsinnigen Eingang `"paragraf"` an. Mit *Use Double Brackets* sind nur noch Namen in `{{…}}` Platzhalter, das JSON-Beispiel bleibt normaler Text und geht so an das Modell. Wie ihr aus einer JSON-Antwort echte Daten macht, zeigt [L6](L6_strukturierte_antworten.md).

</details>

### 🟡 10. Ohne Datum

Löscht die Linie von *Heutiges Datum* zum Prompt und tragt in das Feld **heute** nichts ein. Fragt in einer neuen Sitzung: *Ich leihe heute ein Buch aus. An welchem Datum muss ich es spätestens zurückgeben?* Wenn ihr ein lokales Modell habt, stellt die **Quelle** auf *Lokal (Ollama)* und fragt noch einmal.

<details>
<summary>Lösung</summary>

Das Cluster-Modell nennt trotzdem das richtige Datum: Der Cluster schickt das heutige Datum von sich aus mit. Darauf könnt ihr euch aber nicht verlassen, andere Dienste und lokale Modelle tun das nicht. Ein lokales Modell kennt nur den Stand seiner Trainingsdaten. Beim Ausprobieren nannte das lokale Modell ohne Zögern ein falsches Rückgabedatum, das sogar schon in der Vergangenheit lag. Mit *Current Date* im Prompt stimmt die Rechnung unabhängig vom Modell. Verbindet die Linie danach wieder.

</details>

### 🔴 11. Zwei Modelle, eines wählt aus: LLM Selector

*LLM Selector* (Kategorie *LLM Operations*) lässt ein Modell entscheiden, welches von mehreren Modellen eine Anfrage beantwortet. Baut einen kleinen Flow:

1. **Chat Input** an den Eingang **Input** des LLM Selector.
2. Zwei **KI-Modell**-Bausteine mit Quelle *Cluster* und zwei verschiedenen Modellen (mit dem Pfeil-Knopf neben **Modell** laden). Beide Ausgänge *Language Model* an den Eingang **Language Models**.
3. Ein drittes **KI-Modell** an **Judge LLM**: Es entscheidet.
4. Die Ausgänge **Output** und **Routing Decision** an je einen **Chat Output**.

Fragt *Schreib einen Haiku über eine Bibliothek* und stellt **Optimization** von *balanced* auf *quality* und *speed*.

<details>
<summary>Lösung</summary>

*Output* ist die Antwort des gewählten Modells. *Routing Decision* erklärt die Wahl: welches Modell, nach welchem Ziel (*quality*, *speed*, *cost* oder *balanced*) und auf Grundlage welcher Angaben. Die Angaben über die Modelle holt der Baustein aus einem öffentlichen Verzeichnis (*Use OpenRouter Specs* unter *Parameters*). Für den Hackathon ist das eher ein Blick in die Werkstatt: Ihr seht, dass sich Modelle in Qualität, Tempo und Kosten unterscheiden, und dass man die Wahl automatisieren kann.

</details>

### 🔴 12. Ein eigener Flow: Klappentexte für Neuerwerbungen

Baut ohne Vorlage einen Flow, der zu einem Buch aus `daten/lernpfad/neuerwerbungen.csv` einen kurzen Klappentext für den Social-Media-Kanal der Bibliothek schreibt. Titel und Fach kommen aus dem Playground, z. B. *Metadaten in der Praxis, Bibliothekswissenschaft*. Überlegt: Welche Kreativität? Was muss in den Prompt, damit das Modell keinen Inhalt des Buches erfindet?

<details>
<summary>Lösung</summary>

**Chat Input** → **Prompt Template** → **KI-Modell** → **Chat Output**. Ein mögliches Template:

```text
BUCH: {buch}

Du betreust den Social-Media-Kanal einer Hochschulbibliothek. Schreibe zu dem Buch oben einen Beitrag mit zwei Sätzen, der neugierig macht, und drei passende Hashtags.
Du kennst nur Titel und Fach, nicht den Inhalt. Behaupte nichts über den Inhalt, was nicht aus dem Titel folgt.
```

Kreativität etwa 0,7: Werbetexte dürfen abwechslungsreich sein. Der Satz über den Inhalt ist die Grenze aus Übung 4. Wer mag, setzt *Message History* dazu, um im Playground nachzubessern: *Kürzer, bitte, und ohne Ausrufezeichen.*

</details>

## 5. Wann nehme ich was?

| Ihr wollt … | Nehmt … | Hinweis |
| --- | --- | --- |
| eine Antwort von einem Sprachmodell | **KI-Modell** | Der einfachste Weg; Quelle und Modell aus der `.env` |
| ein Modell für Agent, Batch Run, Structured Output und Co. | den Ausgang **Language Model** von **KI-Modell** | Kreativität und Antwortlänge stellt ihr im KI-Modell ein |
| einen Standard-Baustein mit eigenem Anbieter (OpenAI, Anthropic …) | **Language Model** | Braucht ein Konto und einen Schlüssel beim Anbieter; hier nicht eingerichtet |
| Rolle, Ton und Sprache für jede Anfrage festlegen | **System Message** | Setzt sich meist gegen den Prompt durch |
| Daten und die konkrete Aufgabe übergeben | **Prompt Template** | Daten oben, Anweisung unten |
| einen festen Text in den Prompt (Regeln, Vorlage) | ein **Platzhalter mit festem Text** | Läuft ohne Upload; für Texte, die sich oft ändern, besser **Read File** |
| geschweifte Klammern im Prompt (JSON-Beispiel) | **Use Double Brackets** | Platzhalter dann als `{{name}}` |
| dass Nachfragen verstanden werden | **Message History** | Nur Ausgaben speichern lassen, die ins Gespräch gehören |
| Fragen mit Datum und Fristen | **Current Date** | Auch wenn ein Modell das Datum zu kennen scheint |
| mehrere Modelle vergleichen oder automatisch wählen | **LLM Selector** | Eher zum Ausprobieren |
| sachliche, wiederholbare Antworten | **Kreativität** 0 bis 0,2 | Für Auskunft, Prüfung, Daten |
| abwechslungsreiche Texte | **Kreativität** 0,6 bis 1 | Für Werbung und Ideen; Fakten prüfen |

**Cluster oder lokal?** Lokale Modelle halten die Daten auf dem Laptop, z. B. für Anfragen mit personenbezogenen Daten. Sie sind aber klein: Sie antworten langsamer, halten sich schlechter an Anweisungen wie *nenne den Paragrafen* und erfinden eher. Mehr dazu in der [Anleitung für Teilnehmende](../01_teilnehmende.md#7-cluster-oder-lokales-modell).

## 6. Wenn etwas nicht klappt

| Meldung oder Problem | Ursache und Lösung |
| --- | --- |
| *Keine Adresse für das KI-Modell* | In der `.env` fehlt `CLUSTER_BASE_URL`. Bei der Orga nachfragen oder die Quelle *Lokal* wählen. |
| *Kein Modell gewählt* | Im KI-Modell ein Modell wählen (Pfeil-Knopf) oder in der `.env` `CLUSTER_MODELL` bzw. `LOKAL_MODELL` setzen. |
| *Connection refused* bei Quelle Lokal | Ollama läuft nicht. Siehe [Anleitung für Teilnehmende](../01_teilnehmende.md#9-wenn-etwas-nicht-klappt). |
| Die Antwort ist leer | Die *Maximale Antwortlänge* ist zu klein für ein Modell, das vor der Antwort nachdenkt (Übung 2). Auf 0 setzen. |
| Die Antwort bricht mitten im Satz ab | Ebenfalls die *Maximale Antwortlänge*. |
| Language Model meldet *A model selection is required* | Im Feld *Language Model* ist weder ein Anbieter noch eine Verbindung. Den Ausgang *Language Model* eines KI-Modell anschließen. |
| Das Modell ignoriert eine Anweisung | Widersprüchliche Anweisungen im Prompt oder in der System Message suchen (Übung 3). Bei kleinen Modellen die Anweisung ans Ende stellen und kürzen. |
| Ein unerwarteter Eingang erscheint am Prompt Template | Im Template stehen geschweifte Klammern, die kein Platzhalter sein sollen (Übung 9). |
| Der Flow erinnert sich an alte Fragen | Im Playground mit **+** eine neue Sitzung starten. |
| Der Flow vergisst die vorige Frage | Neue Sitzung gestartet, oder *Number of Messages* in Message History zu klein. |

**Weiter:** [L6 Strukturierte Antworten](L6_strukturierte_antworten.md) zeigt, wie ihr aus der Antwort eines Modells wieder Daten macht: Felder, Tabellen und JSON.
