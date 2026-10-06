# Gehostete Instanz

[English](HOSTING.md) | **Deutsch**

Neben der Installation auf den Laptops der Gruppen kann der Bibliothekshackathon auch als ein gemeinsames Langflow im Kubernetes-Cluster des AISC laufen. Die Gruppen brauchen dann nur einen Browser und Zugangsdaten. Das eignet sich für Live-Demos und für Hackathons, bei denen auf den Laptops kein Docker installiert werden kann.

Diese Anleitung richtet sich an die Orga, die die gehostete Instanz einrichtet und betreut. Für einige Schritte braucht ihr Zugriff auf den Cluster (`kubectl`, `kubeseal`); alles andere geschieht in GitHub, ArgoCD und im Browser.

## Inhalt

1. [Wie es funktioniert](#1-wie-es-funktioniert)
2. [Was ihr braucht](#2-was-ihr-braucht)
3. [Zugangsdaten](#3-zugangsdaten)
4. [Einstellungen](#4-einstellungen)
5. [Die App in ArgoCD anlegen](#5-die-app-in-argocd-anlegen)
6. [Ausrollen und aktualisieren](#6-ausrollen-und-aktualisieren)
7. [Über Caddy erreichbar machen](#7-über-caddy-erreichbar-machen)
8. [Konten der Gruppen](#8-konten-der-gruppen)
9. [Was die Teilnehmenden wissen müssen](#9-was-die-teilnehmenden-wissen-müssen)
10. [Während und nach dem Hackathon](#10-während-und-nach-dem-hackathon)
11. [Grenzen](#11-grenzen)
12. [Wenn etwas nicht klappt](#12-wenn-etwas-nicht-klappt)

## 1. Wie es funktioniert

```
 Browser einer Gruppe
   │  https
   ▼
 Caddy (außerhalb des Clusters, TLS)
   │
   ▼
 Namespace bibliothekshackathon
 ┌────────────────────────────────────────────────────────────┐
 │  Service langflow ──► Langflow (1 Pod)  ──► Postgres        │
 │                          │  Bibliotheks-Bausteine, Flows   │
 │  Job konten-anlegen ─────┘  (Konten und Flows je Gruppe)    │
 └──────────────────────────┼─────────────────────────────────┘
                            ├──► AISC AI Hub (api.aisc.hpi.de)
                            └──► Crossref · OpenAlex · Unpaywall · DataCite · lobid
```

- **Ein Konto pro Gruppe.** Jede Gruppe meldet sich mit einem eigenen Konto an und sieht nur ihre eigenen Flows, hochgeladenen Dateien und Playground-Gespräche. Zwei Gruppen können gleichzeitig arbeiten, ohne sich in die Quere zu kommen.
- **Jedes Konto startet mit einer eigenen Kopie der Beispiel-Flows.** Der Job `konten-anlegen` legt die Konten an und kopiert die Flows hinein.
- **Die KI kommt vom AISC AI Hub**, demselben LiteLLM-Proxy, den auch pilotproject-sentra nutzt. Im Cluster läuft kein Ollama, die Quelle *Lokal* im Baustein KI-Modell funktioniert hier also nicht.
- **Niemand kann eigenes Python auf dem Server ausführen.** Die Gruppen können den Code eines Bausteins nicht ändern, und Langflows Python-Bausteine (Python Interpreter, Smart Transform und ähnliche) sind abgeschaltet. Die Bibliotheks-Bausteine funktionieren weiterhin.
- **ArgoCD rollt aus**, genau wie bei pilotproject-sentra: Es beobachtet den Ordner `k8s/` auf `main` und synchronisiert, wenn jemand auf *Sync* drückt.

Die beteiligten Dateien:

| Pfad | Inhalt |
| --- | --- |
| `Dockerfile` | Langflow 1.12.3 plus Bibliotheks-Bausteine, Flows und Testdaten |
| `.github/workflows/docker-publish.yml` | baut das Image bei jedem Push auf `main` und schreibt den neuen Tag in `k8s/` |
| `k8s/` | die Kubernetes-Manifeste, die ArgoCD liest |
| `k8s/secrets/` | Zugangsdaten: ein Beispiel, die versiegelte Fassung und ein Skript zum Versiegeln |
| `scripts/konten_anlegen.py` | legt die Konten der Gruppen an, ausgeführt vom Job in `k8s/konten/` |

## 2. Was ihr braucht

- **Zugriff auf den Cluster** mit `kubectl` und [`kubeseal`](https://github.com/bitnami-labs/sealed-secrets), um die Zugangsdaten zu versiegeln. Das braucht nur eine Person.
- **Einen Schlüssel für den AI Hub.** Am besten einen eigenen für den Hackathon, mit Budget und Ablaufdatum, denn alle Gruppen verbrauchen davon.
- **Ein Modell auf dem AI Hub, das Werkzeuge aufrufen kann**, für den Agenten in Flow 04. Voreingestellt ist `gpt-oss-120b`. Auch `gemma-4-31b` und `qwen3-8-27b` können Werkzeuge aufrufen; `llama-3-3-70b` nicht, weil der AI Hub es ohne Werkzeugunterstützung betreibt.
- **Einen kostenlosen [OpenAlex-API-Schlüssel](https://openalex.org/settings/api).** Dringend empfohlen: Alle Gruppen erreichen OpenAlex über die eine Adresse des Clusters und teilen sich sonst ein kleines Limit.
- **Einen Hostnamen in Caddy**, z. B. `bibliothekshackathon.aisc.hpi.de`.

## 3. Zugangsdaten

Die Zugangsdaten liegen in einem Kubernetes-Secret. In Git steht es nur versiegelt (`k8s/secrets/sealed-secret.yaml`), verschlüsselt mit dem öffentlichen Schlüssel des Clusters. Entschlüsseln kann es nur der Cluster.

Der Klartext steht in `k8s/secrets/secret.yaml`. Diese Datei ist in `.gitignore` eingetragen und darf nie committet werden. Wer die Instanz einrichtet, bewahrt sie auf.

| Schlüssel | Inhalt |
| --- | --- |
| `AI_HUB_API_KEY` | der Schlüssel für den AI Hub. **Pflicht:** Ohne ihn startet der Langflow-Pod nicht und nennt den fehlenden Schlüssel. |
| `OPENALEX_API_KEY` | der OpenAlex-Schlüssel, darf leer sein |
| `DB_PASSWORD` | Passwort für Postgres |
| `LANGFLOW_DATABASE_URL` | dasselbe Passwort in der Datenbankadresse: `postgresql://langflow:<DB_PASSWORD>@langflow-db:5432/langflow` |
| `LANGFLOW_SUPERUSER_PASSWORD` | Passwort des Admin-Kontos `orga` |
| `LANGFLOW_SECRET_KEY` | damit verschlüsselt Langflow gespeicherte Variablen und Schlüssel |
| `GRUPPEN_KONTEN` | die Konten der Gruppen, eine Zeile pro Gruppe: `name:passwort` (siehe [Abschnitt 8](#8-konten-der-gruppen)) |

**Beim ersten Mal:** vom Beispiel ausgehen und die Werte eintragen. Zufällige Werte für die Passwörter und den Secret Key:

```bash
cd k8s/secrets
cp example-secret.yaml secret.yaml
openssl rand -base64 24   # einmal je Passwort und für den Secret Key
```

**Versiegeln und committen:**

```bash
./seal.sh                                   # holt den öffentlichen Schlüssel selbst vom Cluster
SEALING_CERT=pfad/zum/cert.pem ./seal.sh    # oder mit einer gespeicherten Kopie davon
git add sealed-secret.yaml && git commit -m "…"
```

Geänderte Zugangsdaten wirken nach dem nächsten Sync in ArgoCD.

> **Zwei Werte dürfen sich bei einer bestehenden Instanz nie ändern:** `DB_PASSWORD`, weil Postgres damit eingerichtet wurde, und `LANGFLOW_SECRET_KEY`, weil mit einem neuen alles unlesbar wird, was Langflow verschlüsselt hat. Ist `secret.yaml` verloren, eine neue Instanz aufsetzen (siehe [Abschnitt 10](#10-während-und-nach-dem-hackathon)).

## 4. Einstellungen

Alles, was nicht geheim ist, steht in `k8s/langflow/configmap.yaml`:

| Einstellung | Bedeutung |
| --- | --- |
| `CLUSTER_MODELL` | das Standardmodell des Bausteins KI-Modell. Die Gruppen können im Baustein ein anderes wählen. |
| `KONTAKT_EMAIL` | Kontaktadresse für Crossref und Unpaywall. Bleibt leer: Jede Gruppe trägt ihre eigene in Langflow ein (siehe [Abschnitt 9](#9-was-die-teilnehmenden-wissen-müssen)). Eine Adresse hier gilt nur für Gruppen, die das nicht getan haben. |
| `LANGFLOW_SUPERUSER` | Name des Admin-Kontos (`orga`) |
| `LANGFLOW_RATE_LIMIT_PER_MINUTE` | wie viele Anmeldeversuche pro Minute Langflow von einer Adresse annimmt (60). Alle im WLAN des Veranstaltungsorts teilen sich meist eine Adresse. |

Die übrigen Einstellungen schalten den Mehrbenutzerbetrieb ein und eigenen Code aus. Jede ist in der Datei erklärt.

## 5. Die App in ArgoCD anlegen

Einmalig, wie bei pilotproject-sentra. In der Oberfläche von ArgoCD (*New App*) oder als Manifest:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: bibliothekshackathon
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/aihpi/demo-bibliothekshackaton.git
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: bibliothekshackathon
  # Kein automatischer Sync: Wie bei sentra entscheidet ein Mensch, wann ausgerollt wird.
```

## 6. Ausrollen und aktualisieren

**Jede Aktualisierung läuft gleich ab:**

1. Eine Änderung wird in `main` gemergt.
2. Betrifft sie etwas, das im Image steckt (Bausteine, Flows, Testdaten, das Konten-Skript), baut GitHub Actions ein neues Image, schreibt dessen Tag in `k8s/` und committet das. Das dauert ein paar Minuten. Änderungen nur in `k8s/` brauchen kein neues Image.
3. In ArgoCD steht die App auf *OutOfSync*. Auf **Sync** drücken.

ArgoCD startet dann zuerst Postgres und danach Langflow. Sobald Langflow bereit ist, läuft der Job, der die Konten der Gruppen anlegt.

**Das erste Ausrollen** läuft genauso, sobald das versiegelte Secret den Schlüssel für den AI Hub enthält. Langflow braucht beim ersten Start ein bis zwei Minuten.

**Ohne ArgoCD**, z. B. auf einem Testcluster: `kubectl apply -k k8s`

## 7. Über Caddy erreichbar machen

Der Service `langflow` hat den Typ `LoadBalancer`, wie das Frontend von sentra. Seine Adresse:

```bash
kubectl get service langflow -n bibliothekshackathon
```

Im Caddyfile genügt ein einfacher Reverse Proxy:

```
bibliothekshackathon.aisc.hpi.de {
	reverse_proxy <EXTERNAL-IP>:80
}
```

**Hier kein `basic_auth`**, anders als bei sentra. Die Weboberfläche von Langflow schickt ihr eigenes Anmelde-Token im selben `Authorization`-Header, den auch Basic Auth nutzt, und beides kommt sich in die Quere. Die Anmeldung von Langflow schützt die Instanz. Caddy gibt die Adressen der Teilnehmenden in `X-Forwarded-For` an Langflow weiter; das braucht Langflow für sein Anmeldelimit.

## 8. Konten der Gruppen

Die Konten stehen im Secret, eine Zeile pro Gruppe:

```yaml
  GRUPPEN_KONTEN: |
    gruppe01:kt7m-q3xp-9wfa
    gruppe02:…
```

Nach jedem Sync erledigt der Job `konten-anlegen` Folgendes:

- Er legt jedes Konto an, das es noch nicht gibt.
- Er setzt bei bestehenden Konten das Passwort aus dem Secret.
- Er kopiert jeden Beispiel-Flow in jedes Konto, das noch keinen Flow mit diesem Namen hat.

Mehrfaches Ausführen ist gefahrlos. Was eine Gruppe gebaut oder verändert hat, wird nie überschrieben. Hat eine Gruppe einen Beispiel-Flow gelöscht, bekommt sie beim nächsten Sync eine frische Kopie.

| Was | Wie |
| --- | --- |
| **Weitere Gruppe** | Zeile ergänzen, versiegeln, committen, Sync |
| **Neues Passwort** | Zeile ändern, versiegeln, committen, Sync |
| **Gruppe entfernen** | Zeile löschen *und* das Konto löschen (siehe unten) |
| **Job ansehen** | `kubectl logs -n bibliothekshackathon job/konten-anlegen` |

Die Passwörter verteilt ihr am einfachsten auf Papier, ein Zettel pro Gruppe.

**Ein Konto löschen.** Langflow 1.12 hat in der Oberfläche keine Admin-Seite, darum geht das über die API, mit dem Admin-Konto (braucht `jq`):

```bash
kubectl port-forward -n bibliothekshackathon svc/langflow 7860:80 &
TOKEN=$(curl -s -X POST localhost:7860/api/v1/login -d "username=orga&password=<ADMIN-PASSWORT>" | jq -r .access_token)
curl -s -H "Authorization: Bearer $TOKEN" "localhost:7860/api/v1/users/?limit=1000" | jq -r '.users[] | "\(.id)  \(.username)"'
curl -X DELETE -H "Authorization: Bearer $TOKEN" localhost:7860/api/v1/users/<ID>
```

Danach kann sich niemand mehr mit dem Konto anmelden.

## 9. Was die Teilnehmenden wissen müssen

- **Die Adresse**, den **Gruppennamen** und das **Passwort**. Installiert werden muss nichts.
- **An einem Flow arbeitet immer nur eine Person.** Mehrere Personen einer Gruppe können gleichzeitig angemeldet sein. Bearbeiten aber zwei von ihnen *denselben* Flow gleichzeitig, gewinnt die letzte Speicherung, und die Änderungen der anderen Person sind weg. Wer etwas ausprobieren will, legt vorher eine Kopie an (drei Punkte → *Duplicate*).
- **Eine Kontakt-E-Mail eintragen**, einmal pro Gruppe: Menü oben rechts → *Settings* → *Global Variables* → *Add New*, Name `KONTAKT_EMAIL`, die E-Mail-Adresse als Wert. Crossref antwortet dann schneller, und der Baustein *Volltexte holen* findet zusätzlich Volltexte über Unpaywall. Jede Gruppe hat ihre eigene Adresse, so teilen sich die Gruppen nicht das Limit von Crossref.
- **Im Baustein KI-Modell *Standard* oder *Cluster* wählen.** *Lokal* funktioniert auf der gehosteten Instanz nicht.
- **Die Testdaten** (`daten/`) liegen auf GitHub; die Gruppen laden sie herunter und in Langflow hoch.
- In der Anleitung für Teilnehmende kann alles zu Installation, `.env` und Docker übersprungen werden.

## 10. Während und nach dem Hackathon

**Protokolle:**

```bash
kubectl logs -n bibliothekshackathon deploy/langflow -f
kubectl get pods -n bibliothekshackathon
```

**Ergebnisse der Gruppen einsammeln:** als Gruppe anmelden und die Flows exportieren (drei Punkte → *Export*), oder die Gruppen bitten, sie selbst zu exportieren.

**Die Datenbank sichern:**

```bash
kubectl exec -n bibliothekshackathon deploy/langflow-db -- pg_dump -U langflow langflow > sicherung.sql
```

**Für den nächsten Hackathon neu anfangen** (löscht alle Konten, Flows und Uploads): in ArgoCD die App *samt ihren Ressourcen* löschen, oder:

```bash
kubectl delete namespace bibliothekshackathon
```

Danach neue Werte in `secret.yaml` (neue Passwörter, neuer Secret Key), versiegeln, committen, Sync.

**Nach dem Hackathon:** den Schlüssel für den AI Hub deaktivieren oder ablaufen lassen.

## 11. Grenzen

- **Ein Langflow-Pod.** Er ist für etwa 20 bis 30 gleichzeitig arbeitende Personen ausgelegt (bis zu 4 CPU-Kerne, 8 GB Arbeitsspeicher). Die schwere Arbeit macht der AI Hub; der Pod liest vor allem PDFs und wartet auf Antworten. Mehr Pods würden nicht helfen: Langflow hält laufende Flows im eigenen Arbeitsspeicher.
- **Derselbe Flow in zwei Browsern:** siehe [Abschnitt 9](#9-was-die-teilnehmenden-wissen-müssen). Langflow kennt keine gemeinsame Bearbeitung in Echtzeit.
- **Gemeinsame Limits der externen Dienste.** Alle Anfragen an Crossref, OpenAlex und Unpaywall kommen von der einen Adresse des Clusters. Ohne OpenAlex-Schlüssel, und bei Gruppen ohne Kontakt-E-Mail, werden Suchen spürbar langsamer, wenn viele Gruppen gleichzeitig arbeiten.
- **Admin-Konto:** `orga` kann über die API alle Konten anlegen, ändern und löschen. Das Passwort bleibt bei der Orga.

## 12. Wenn etwas nicht klappt

| Problem | Lösung |
| --- | --- |
| Langflow-Pod hängt in `CreateContainerConfigError` | Im Secret fehlt ein Schlüssel, meist `AI_HUB_API_KEY`. `kubectl describe pod -n bibliothekshackathon -l app=langflow` nennt ihn. Ergänzen, versiegeln, Sync. |
| Der Sync bleibt einige Minuten bei *Progressing* | Beim ersten Start normal: Langflow richtet seine Datenbank ein und lädt alle Bausteine. |
| Anmeldung meldet „Too many requests“ | Mehr als 60 Anmeldeversuche pro Minute von einer Adresse. Eine Minute warten oder `LANGFLOW_RATE_LIMIT_PER_MINUTE` erhöhen. |
| Eine Gruppe kann sich nicht anmelden | Stimmt die Zeile in `GRUPPEN_KONTEN`, und wurde das Secret seitdem versiegelt und synchronisiert? Das Protokoll des Jobs ansehen. |
| Eine Gruppe sieht die Beispiel-Flows nicht | Der Job ist seit dem Anlegen des Kontos nicht gelaufen. Erneut synchronisieren oder den Job von Hand starten (siehe Kommentar in `k8s/konten/job.yaml`). |
| Jeder Flow scheitert am KI-Modell mit 401 | Der Schlüssel für den AI Hub ist falsch oder abgelaufen. |
| Der Agent (Flow 04) antwortet, ohne zu suchen | Das gewählte Modell kann keine Werkzeuge aufrufen. Im Baustein KI-Modell ein anderes Modell wählen oder `CLUSTER_MODELL` ändern. |
| Eine Gruppe hat einen Beispiel-Flow kaputtgemacht | Den Flow löschen. Beim nächsten Sync bekommt die Gruppe eine frische Kopie. |
