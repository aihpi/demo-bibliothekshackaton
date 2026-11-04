# Lernpfad: Langflow-Bausteine kennenlernen

Die Beispiel-Flows 00 bis 05 zeigen fertige Lösungen für Aufgaben aus Bibliotheken. Der Lernpfad zeigt, wie man solche Flows selbst baut: Jeder Flow L1 bis L9 dreht sich um **einen Arbeitsschritt**, zum Beispiel Daten holen, Text aufbereiten oder ein Sprachmodell eine Tabelle füllen lassen, und um die Bausteine, die es dafür gibt.

Zu jedem Flow gehört eine Anleitung. Sie geht den Flow Schritt für Schritt durch und hat Übungen, in denen ihr Einstellungen verändert, den Flow neu ausführt und die Ergebnisse vergleicht. So lernt ihr, was ein Baustein tut, welche Einstellungen er hat und wann ihr ihn statt eines ähnlichen nehmt.

Die Nachschlage-Übersicht aller Bausteine mit ihren Eingängen und Ausgängen ist die [Bausteine-Übersicht](../../COMPONENTS.de.md). Der Lernpfad wiederholt sie nicht, sondern zeigt die Bausteine bei der Arbeit.

## Inhalt

1. [Die Module](#1-die-module)
2. [So arbeitet ihr mit dem Lernpfad](#2-so-arbeitet-ihr-mit-dem-lernpfad)
3. [Welcher Baustein wo vorkommt](#3-welcher-baustein-wo-vorkommt)
4. [Testdaten](#4-testdaten)

## 1. Die Module

Die Module bauen aufeinander auf. L1 bis L4 kommen ganz ohne KI aus: Dort geht es um Daten, und was ihr dort lernt, braucht ihr in jedem späteren Flow. Ab L5 kommt das Sprachmodell dazu.

| Modul | Arbeitsschritt | Wichtigste Bausteine | KI | Dauer |
| --- | --- | --- | --- | --- |
| [L1 Daten importieren](L1_daten_importieren.md) | Daten aus Dateien, Webseiten, Webdiensten und der Websuche holen | Read File, URL, API Request, Web Search, Mock Data | nein | 45 Min. |
| [L2 Texte aufbereiten](L2_texte_aufbereiten.md) | Unordentlichen Text säubern, Muster herausziehen und Text in Stücke zerlegen | Data Operations (Text), Split Text, Type Convert | nein | 45 Min. |
| [L3 Tabellen und JSON](L3_tabellen_und_json.md) | Aus der Antwort eines Webdienstes und einer Liste eine saubere Tabelle machen | Data Operations (JSON, Table), Dynamic Create Data, Type Convert, Parser | nein | 60 Min. |
| [L4 Ergebnisse ausgeben](L4_ergebnisse_ausgeben.md) | Ergebnisse als Liste, HTML, Zitate oder Datei ausgeben | Parser, Prompt Template, Chat Output, Write File | nein | 45 Min. |
| [L5 Prompts und Modelle](L5_prompts_und_modelle.md) | Wie Prompt und Modelleinstellungen eine Antwort verändern | Prompt Template, KI-Modell, Language Model, Message History, Current Date, LLM Selector | ja | 60 Min. |
| L6 Strukturierte Antworten | Aus freiem Text mit KI Daten machen, auf vier Wegen im Vergleich | Structured Output, Type Convert, Batch Run, Smart Transform | ja | 60 Min. |
| [L7 Verzweigen und absichern](L7_verzweigen_und_absichern.md) | Anfragen prüfen und auf den passenden Weg schicken | If-Else, Smart Router, Guardrails, Human Input | ja | 60 Min. |
| [L8 Wiederholen mit Loop](L8_wiederholen_mit_loop.md) | Eine Liste Eintrag für Eintrag abarbeiten | Loop, Split Text, API Request, Data Operations, Batch Run | teils | 60 Min. |
| L9 Agenten | Eine KI selbst entscheiden lassen, welche Werkzeuge sie nutzt | Agent, Web Search, URL, Calculator, Current Date, Run Flow | ja | 60 Min. |

**Wer wenig Zeit hat**, nimmt L1, L3, L5 und L6: Daten holen, Daten in Form bringen, ein Modell ansprechen und aus seiner Antwort wieder Daten machen. Das ist das Gerüst fast jedes Flows.

## 2. So arbeitet ihr mit dem Lernpfad

**Kopie anlegen.** Die Lernpfad-Flows liegen wie die Beispiel-Flows im Projekt *Starter Project*. Legt vor den Übungen eine Kopie an (in der Übersicht beim Flow auf die drei Punkte → *Duplicate*) und arbeitet in der Kopie. Bei jedem Start ersetzt Langflow die Originale, Änderungen direkt darin gehen verloren.

**Die Notiz lesen.** Jeder Flow hat auf der Arbeitsfläche eine Notiz, die sagt, was er zeigt und wo ihr anfangt. Die Anleitung erklärt dasselbe ausführlicher.

**Einen Baustein einzeln ausführen.** Jeder Baustein hat oben rechts einen Knopf **▶** (*Run component*). Er führt den Baustein aus, und alle Bausteine davor, die er braucht. Danach zeigt der kleine Knopf am Ausgang (rechts unten am Baustein), was herausgekommen ist, oft als Tabelle. Das ist die wichtigste Technik im ganzen Lernpfad: Ändert eine Einstellung, drückt ▶ und seht nach, was sich ändert.

**Der Playground führt nicht immer alles aus.** Hat ein Flow einen *Chat Input*, führt der Playground nur die Bausteine aus, die von dieser Eingabe abhängen, und das, was diese Bausteine brauchen. Ein Zweig, der nicht mit dem Chat Input verbunden ist, bleibt stehen. Ihn startet ihr mit ▶ an seinem letzten Baustein. Deshalb haben L1 bis L4 keinen Chat Input: Dort läuft im Playground der ganze Flow.

**Die Übungen.** Jede Anleitung hat Übungen in drei Stufen, wie die [Challenges](../02_challenges.md):

- 🟢 **Ausprobieren**: eine Einstellung ändern und beobachten, was passiert
- 🟡 **Umbauen**: Bausteine hinzufügen, austauschen oder anders verbinden
- 🔴 **Selbst bauen**: einen kleinen Flow ohne Vorlage bauen

Zu jeder Übung gibt es eine Lösung zum Aufklappen. Probiert es zuerst selbst; was ihr dabei falsch macht, lehrt am meisten.

**Wann nehme ich was?** Am Ende jeder Anleitung steht eine Tabelle, die ähnliche Bausteine gegenüberstellt, z. B. *Parser* und *Prompt Template* oder *Loop* und *Batch Run*. Sie hilft später beim eigenen Bauplan (siehe [Challenges](../02_challenges.md#bevor-ihr-loslegt-der-bauplan)).

## 3. Welcher Baustein wo vorkommt

Die Bausteine in der Reihenfolge der Leiste *Components*, mit dem Modul, in dem ihr sie kennenlernt. Ein Modul in Klammern heißt: Der Baustein kommt dort noch einmal vor, in einer neuen Rolle.

| Kategorie | Baustein | Modul |
| --- | --- | --- |
| Input & Output | Chat Input | L1, (L5, L7, L9) |
| | Chat Output | L4, (alle) |
| Data Sources | API Request | L1, (L3, L8) |
| | Mock Data | L1 |
| | URL | L1, (L9) |
| | Web Search | L1, (L9) |
| Models & Agents | Agent | L9 |
| | Language Model | L5 |
| | Message History | L5 |
| | Prompt Template | L5, (L4, alle mit KI) |
| LLM Operations | Batch Run | L6, (L8) |
| | Guardrails | L7 |
| | LLM Selector | L5 |
| | Smart Router | L7 |
| | Smart Transform | L6 |
| | Structured Output | L6 |
| Files & Knowledge | Read File | L1, (L2, L3) |
| | Write File | L4 |
| | File System | L9 |
| Processing | Data Operations | L2, L3, (L8) |
| | Dynamic Create Data | L3 |
| | Parser | L3, L4, (L8) |
| | Split Text | L2, (L8) |
| | Type Convert | L2, (L3, L6) |
| Flow Control | Human Input | L7 |
| | If-Else | L7 |
| | Loop | L8 |
| | Run Flow | L9 |
| Utilities | Calculator | L9 |
| | Current Date | L5, (L9) |
| Bibliothek | KI-Modell | L5, (alle mit KI) |

**Nicht im Lernpfad**, und warum:

| Baustein | Grund |
| --- | --- |
| SQL Database | Braucht einen Datenbankserver mit Zugang. Datenbankdateien auf dem Laptop (SQLite) sperrt Langflow. [L1](L1_daten_importieren.md#5-wann-nehme-ich-was) erklärt, wann er sich lohnt. |
| Webhook, A2A Agent | Verbinden Langflow mit anderen Programmen oder Agenten im Netz. Dafür braucht es ein zweites System, das es im Hackathon nicht gibt. |
| Embedding Model, Knowledge, Memory Base | Brauchen einen Embedding-Anbieter, der in diesem Projekt nicht eingerichtet ist (siehe [Bausteine-Übersicht](../../COMPONENTS.de.md#333-embedding-model)). |
| Listen, Notify | In Langflow als *Beta* gekennzeichnet. Was sie leisten, geht mit einer Verbindungslinie einfacher. |
| Python Interpreter | Verlangt Programmieren. Auf der gemeinsamen Instanz ist er außerdem abgeschaltet. |
| Die übrigen Bibliotheks-Bausteine | Sie stecken in den Beispiel-Flows 01 bis 04, die ihr nach dem Lernpfad viel besser versteht. |

## 4. Testdaten

Die Dateien für die Übungen liegen in [`daten/lernpfad/`](../../daten/lernpfad/). Langflow liest keine Dateien direkt aus dem Projektordner: Ladet sie im Baustein *Read File* mit **Select files** hoch. Die Anleitung sagt jeweils, welche Datei wohin gehört.
