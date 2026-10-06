# Hosted instance

**English** | [Deutsch](HOSTING.de.md)

Besides running on each group's laptop, the hackathon kit can run as one shared Langflow on the AISC Kubernetes cluster. Groups then only need a browser and a login. That is useful for live demos and for hackathons where participants cannot install Docker.

This guide is for the organisers who set up and run the hosted instance. You need access to the cluster for some steps (`kubectl`, `kubeseal`); everything else happens in GitHub, ArgoCD and the browser.

## Contents

1. [How it works](#1-how-it-works)
2. [What you need](#2-what-you-need)
3. [Credentials](#3-credentials)
4. [Settings](#4-settings)
5. [Register the app in ArgoCD](#5-register-the-app-in-argocd)
6. [Deploy and update](#6-deploy-and-update)
7. [Make it reachable through Caddy](#7-make-it-reachable-through-caddy)
8. [Group accounts](#8-group-accounts)
9. [What to tell participants](#9-what-to-tell-participants)
10. [During and after the event](#10-during-and-after-the-event)
11. [Limits](#11-limits)
12. [Troubleshooting](#12-troubleshooting)

## 1. How it works

```
 browser of a group
   │  https
   ▼
 Caddy (outside the cluster, TLS)
   │
   ▼
 namespace bibliothekshackathon
 ┌────────────────────────────────────────────────────────────┐
 │  Service langflow ──► Langflow (1 pod)  ──► Postgres        │
 │                          │  library blocks, example flows  │
 │  Job konten-anlegen ─────┘  (accounts and flows per group)  │
 └──────────────────────────┼─────────────────────────────────┘
                            ├──► AISC AI Hub (api.aisc.hpi.de)
                            └──► Crossref · OpenAlex · Unpaywall · DataCite · lobid
```

- **One account per group.** Each group logs in with its own account and only sees its own flows, uploaded files and Playground conversations. Two groups can work at the same time without getting in each other's way.
- **Every account starts with its own copy of the example flows.** The job `konten-anlegen` creates the accounts and copies the flows into them.
- **The AI comes from the AISC AI Hub**, the same LiteLLM proxy pilotproject-sentra uses. There is no Ollama in the cluster, so the *Lokal* option in the KI-Modell block does not work here.
- **Nobody can run their own Python on the server.** Groups cannot edit a block's code, and Langflow's Python blocks (Python Interpreter, Smart Transform and the like) are switched off. The library blocks still work.
- **ArgoCD deploys it**, the same way as pilotproject-sentra: it watches the `k8s/` folder on `main` and syncs when someone presses *Sync*.

The files involved:

| Path | Content |
| --- | --- |
| `Dockerfile` | Langflow 1.12.3 plus the library blocks, flows and test data |
| `.github/workflows/docker-publish.yml` | builds the image on every push to `main` and writes the new tag into `k8s/` |
| `k8s/` | the Kubernetes manifests, read by ArgoCD |
| `k8s/secrets/` | credentials: an example, the sealed version, and a script to seal |
| `scripts/konten_anlegen.py` | creates the group accounts, run by the job in `k8s/konten/` |

## 2. What you need

- **Access to the cluster** with `kubectl` and [`kubeseal`](https://github.com/bitnami-labs/sealed-secrets), for sealing the credentials. Only one person needs this.
- **A key for the AI Hub.** Best a key of its own for the hackathon, with a budget and an expiry date, because all groups spend from it.
- **A model on the AI Hub that can call tools**, for the agent in flow 04. The default is `llama-3-3-70b`.
- **A free [OpenAlex API key](https://openalex.org/settings/api).** Strongly recommended: all groups reach OpenAlex from the cluster's single address and would otherwise share one small limit.
- **A contact email address** for Crossref and Unpaywall, ideally a functional address of your institution.
- **A hostname in Caddy**, e.g. `bibliothekshackathon.aisc.hpi.de`.

## 3. Credentials

The credentials live in a Kubernetes secret. Git only ever contains it in sealed form (`k8s/secrets/sealed-secret.yaml`), encrypted with the cluster's public key. Only the cluster can decrypt it.

The plaintext is in `k8s/secrets/secret.yaml`. That file is in `.gitignore` and must never be committed. Whoever sets up the instance keeps it.

| Key | Content |
| --- | --- |
| `AI_HUB_API_KEY` | the AI Hub key. **Required:** without it the Langflow pod does not start and names the missing key. |
| `OPENALEX_API_KEY` | the OpenAlex key, can be empty |
| `DB_PASSWORD` | Postgres password |
| `LANGFLOW_DATABASE_URL` | the same password inside the database address: `postgresql://langflow:<DB_PASSWORD>@langflow-db:5432/langflow` |
| `LANGFLOW_SUPERUSER_PASSWORD` | password of the admin account `orga` |
| `LANGFLOW_SECRET_KEY` | Langflow encrypts stored variables and keys with it |
| `GRUPPEN_KONTEN` | the group accounts, one line each: `name:password` (see [section 8](#8-group-accounts)) |

**First time:** start from the example and fill in the values. Random values for the passwords and the secret key:

```bash
cd k8s/secrets
cp example-secret.yaml secret.yaml
openssl rand -base64 24   # once per password and for the secret key
```

**Seal and commit:**

```bash
./seal.sh                                   # fetches the cluster's public key itself
SEALING_CERT=path/to/cert.pem ./seal.sh     # or with a saved copy of it
git add sealed-secret.yaml && git commit -m "…"
```

Changes to the credentials take effect after the next sync in ArgoCD.

> **Two values must never change on an existing instance:** `DB_PASSWORD`, because Postgres was initialised with it, and `LANGFLOW_SECRET_KEY`, because everything Langflow encrypted becomes unreadable with a new one. If `secret.yaml` is lost, start a fresh instance (see [section 10](#10-during-and-after-the-event)).

## 4. Settings

Everything that is not secret is in `k8s/langflow/configmap.yaml`:

| Setting | Meaning |
| --- | --- |
| `CLUSTER_MODELL` | the standard model of the KI-Modell block. Groups can pick another one in the block. |
| `KONTAKT_EMAIL` | contact address for Crossref and Unpaywall. **Please fill in.** |
| `LANGFLOW_SUPERUSER` | name of the admin account (`orga`) |
| `LANGFLOW_RATE_LIMIT_PER_MINUTE` | how many login attempts per minute Langflow accepts from one address (60). Everybody on the venue's WiFi usually shares one address. |

The other settings switch on multi-user mode and switch off user code. Each one is explained in the file.

## 5. Register the app in ArgoCD

Once, like pilotproject-sentra. In the ArgoCD interface (*New App*) or as a manifest:

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
  # No automated sync: like sentra, a person decides when to deploy.
```

## 6. Deploy and update

**Every update follows the same path:**

1. A change is merged into `main`.
2. If it touches something that is in the image (blocks, flows, test data, the account script), GitHub Actions builds a new image, writes its tag into `k8s/` and commits that. This takes a few minutes. Changes that only touch `k8s/` need no image.
3. In ArgoCD the app shows as *OutOfSync*. Press **Sync**.

ArgoCD then starts Postgres first and Langflow afterwards. When Langflow is ready, it runs the job that creates the group accounts.

**The first deployment** goes the same way, as soon as the sealed secret contains the AI Hub key. Langflow needs one to two minutes for its first start.

**Without ArgoCD**, for example on a test cluster: `kubectl apply -k k8s`

## 7. Make it reachable through Caddy

The service `langflow` is of type `LoadBalancer`, like sentra's frontend. Its address:

```bash
kubectl get service langflow -n bibliothekshackathon
```

In the Caddyfile, a plain reverse proxy is enough:

```
bibliothekshackathon.aisc.hpi.de {
	reverse_proxy <EXTERNAL-IP>:80
}
```

**No `basic_auth` here**, unlike sentra. Langflow's web interface sends its own login token in the same `Authorization` header that basic auth uses, so the two get in each other's way. Langflow's own login protects the instance. Caddy passes the participants' addresses to Langflow in `X-Forwarded-For`, which Langflow needs for its login limit.

## 8. Group accounts

The accounts are in the secret, one line per group:

```yaml
  GRUPPEN_KONTEN: |
    gruppe01:kt7m-q3xp-9wfa
    gruppe02:…
```

After every sync, the job `konten-anlegen` does the following:

- creates every account that does not exist yet,
- sets the password of existing accounts to the one in the secret,
- copies every example flow into each account that does not have a flow with that name.

Running it again is safe. What a group has built or changed is never overwritten. A group that deleted an example flow gets a fresh copy at the next sync.

| What | How |
| --- | --- |
| **Another group** | add a line, seal, commit, sync |
| **New password** | change the line, seal, commit, sync |
| **Remove a group** | delete the line, *and* delete the account (see below) |
| **Look at the job** | `kubectl logs -n bibliothekshackathon job/konten-anlegen` |

Passwords are easiest to hand out on paper, one slip per group.

**Deleting an account.** Langflow 1.12 has no admin page in its interface, so this goes through its API, with the admin account (needs `jq`):

```bash
kubectl port-forward -n bibliothekshackathon svc/langflow 7860:80 &
TOKEN=$(curl -s -X POST localhost:7860/api/v1/login -d "username=orga&password=<ADMIN PASSWORD>" | jq -r .access_token)
curl -s -H "Authorization: Bearer $TOKEN" "localhost:7860/api/v1/users/?limit=1000" | jq -r '.users[] | "\(.id)  \(.username)"'
curl -X DELETE -H "Authorization: Bearer $TOKEN" localhost:7860/api/v1/users/<ID>
```

After that, nobody can log in with the account any more.

## 9. What to tell participants

- **The address**, the **group name** and the **password**. Nothing needs to be installed.
- **One person edits a flow at a time.** Several people from one group can be logged in at once. But if two of them edit *the same* flow at the same time, the last save wins and the other person's changes are gone. Whoever wants to try something makes a copy first (three dots → *Duplicate*).
- **In the KI-Modell block, choose *Standard* or *Cluster*.** *Lokal* does not work on the hosted instance.
- **Test data** (`daten/`) is on GitHub; groups download it and upload it in Langflow.
- In the participant guide, everything about installing, `.env` and Docker can be skipped.

## 10. During and after the event

**Logs:**

```bash
kubectl logs -n bibliothekshackathon deploy/langflow -f
kubectl get pods -n bibliothekshackathon
```

**Collect the groups' results:** log in as the group and export the flows (three dots → *Export*), or ask the groups to export them themselves.

**Back up the database:**

```bash
kubectl exec -n bibliothekshackathon deploy/langflow-db -- pg_dump -U langflow langflow > backup.sql
```

**Start over for the next hackathon** (deletes all accounts, flows and uploads): in ArgoCD delete the app *including its resources*, or:

```bash
kubectl delete namespace bibliothekshackathon
```

Then new values in `secret.yaml` (new passwords, new secret key), seal, commit, sync.

**After the event:** deactivate the AI Hub key, or let it expire.

## 11. Limits

- **One Langflow pod.** It is sized for about 20 to 30 people working at once (up to 4 CPU cores, 8 GB of memory). The AI Hub does the heavy lifting; the pod mainly reads PDFs and waits for answers. More pods would not help: Langflow keeps running flows in its own memory.
- **Same flow, two browsers:** see [section 9](#9-what-to-tell-participants). Langflow has no live collaboration.
- **Shared limits of the outside services.** All requests to Crossref, OpenAlex and Unpaywall come from the cluster's one address. Without an OpenAlex key and a contact email, searches slow down noticeably when many groups are busy.
- **Admin account:** `orga` can create, change and delete all accounts through the API. Keep its password among the organisers.

## 12. Troubleshooting

| Problem | Solution |
| --- | --- |
| Langflow pod hangs in `CreateContainerConfigError` | A key is missing in the secret, usually `AI_HUB_API_KEY`. `kubectl describe pod -n bibliothekshackathon -l app=langflow` names it. Add it, seal, sync. |
| Sync stays at *Progressing* for a few minutes | Normal on the first start: Langflow sets up its database and loads all blocks. |
| Login says "Too many requests" | More than 60 login attempts per minute from one address. Wait a minute, or raise `LANGFLOW_RATE_LIMIT_PER_MINUTE`. |
| A group cannot log in | Is the line in `GRUPPEN_KONTEN` right, and has the secret been sealed and synced since? Look at the job's log. |
| A group does not see the example flows | The job has not run since the account was created. Sync again, or start the job by hand (see the comment in `k8s/konten/job.yaml`). |
| Every flow fails at the KI-Modell with 401 | The AI Hub key is wrong or has expired. |
| The agent (flow 04) answers without searching | The chosen model cannot call tools. Pick another model in the KI-Modell block, or change `CLUSTER_MODELL`. |
| A group has broken an example flow | Delete the flow. At the next sync the group gets a fresh copy. |
