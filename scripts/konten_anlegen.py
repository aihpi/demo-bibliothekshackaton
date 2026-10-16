"""Legt die Konten der Gruppen an und gibt jedem Konto eine eigene Kopie der Beispiel-Flows.

Für die gemeinsame Instanz im Cluster (k8s/konten/job.yaml). Langflow lädt die Flows aus
LANGFLOW_LOAD_FLOWS_PATH nur für das Admin-Konto, darum geht dieses Skript über die API:
als Admin die Konten anlegen, dann als jede Gruppe die Flows hochladen, die ihr noch fehlen.

Mehrfach ausführen ist gefahrlos: Bestehende Konten bekommen nur das Passwort aus dem Secret,
und ein Flow wird nur hochgeladen, wenn das Konto noch keinen mit diesem Namen hat. Was eine
Gruppe gebaut oder verändert hat, bleibt also unberührt.

Umgebungsvariablen:
    LANGFLOW_URL                  z. B. http://langflow (der Service im Cluster)
    LANGFLOW_SUPERUSER            Admin-Konto
    LANGFLOW_SUPERUSER_PASSWORD
    GRUPPEN_KONTEN                eine Zeile pro Gruppe: "name:passwort"
    FLOWS_PFAD                    Ordner mit den Flows (Standard: /app/flows)
"""

import json
import os
import sys
import time
from pathlib import Path

import httpx

# Nur diese Felder einer exportierten Flow-Datei gehen an die API. Die id ist in der ganzen
# Datenbank eindeutig und gehört dem Admin-Konto; jede Gruppe bekommt eine neue.
FLOW_FELDER = ("name", "description", "icon", "tags", "data", "is_component")


def konten_lesen(text: str) -> dict[str, str]:
    """Liest "name:passwort" je Zeile. Leere Zeilen und Zeilen mit # werden übersprungen."""
    konten: dict[str, str] = {}
    for nummer, zeile in enumerate(text.splitlines(), start=1):
        zeile = zeile.strip()
        if not zeile or zeile.startswith("#"):
            continue
        name, trenner, passwort = zeile.partition(":")
        name, passwort = name.strip(), passwort.strip()
        if not trenner or not name or not passwort:
            msg = f"GRUPPEN_KONTEN, Zeile {nummer}: erwartet 'name:passwort'"
            raise ValueError(msg)
        if name in konten:
            msg = f"GRUPPEN_KONTEN: Konto '{name}' steht doppelt drin"
            raise ValueError(msg)
        konten[name] = passwort
    return konten


def flows_lesen(ordner: Path) -> list[dict]:
    flows = []
    for datei in sorted(ordner.glob("*.json")):
        flow = json.loads(datei.read_text(encoding="utf-8"))
        flows.append({feld: flow[feld] for feld in FLOW_FELDER if feld in flow})
    return flows


def fehlende_flows(flows: list[dict], vorhandene_namen: set[str]) -> list[dict]:
    return [flow for flow in flows if flow["name"] not in vorhandene_namen]


class Langflow:
    def __init__(self, url: str, transport: httpx.BaseTransport | None = None):
        self.url = url
        self.transport = transport

    def _client(self, token: str | None = None) -> httpx.Client:
        kopf = {"Authorization": f"Bearer {token}"} if token else {}
        return httpx.Client(base_url=self.url, headers=kopf, timeout=60, transport=self.transport)

    def warten(self, sekunden: float = 600, pause: float = 5) -> None:
        """Wartet, bis Langflow antwortet. Der Job kann vor Langflow starten (kubectl apply ohne ArgoCD)."""
        ende = time.monotonic() + sekunden
        while True:
            try:
                with self._client() as client:
                    if client.get("/health_check").status_code == 200:
                        return
            except httpx.HTTPError:
                pass
            if time.monotonic() > ende:
                msg = f"Langflow unter {self.url} antwortet nicht"
                raise TimeoutError(msg)
            time.sleep(pause)

    def anmelden(self, name: str, passwort: str, versuche: int = 6, pause: float = 15) -> str:
        # Langflow begrenzt Anmeldungen je IP-Adresse (LANGFLOW_RATE_LIMIT_PER_MINUTE). Bei vielen
        # Gruppen kommt das Skript an die Grenze und wartet dann kurz.
        with self._client() as client:
            for versuch in range(versuche):
                antwort = client.post("/api/v1/login", data={"username": name, "password": passwort})
                if antwort.status_code != 429 or versuch == versuche - 1:
                    break
                time.sleep(float(antwort.headers.get("retry-after", pause)))
        antwort.raise_for_status()
        return antwort.json()["access_token"]

    def konto_sicherstellen(self, admin_token: str, name: str, passwort: str) -> str:
        """Legt das Konto an oder setzt bei einem bestehenden Passwort und Aktivierung. Gibt 'neu' oder 'aktualisiert'."""
        with self._client(admin_token) as client:
            antwort = client.get("/api/v1/users/", params={"limit": 10000})
            antwort.raise_for_status()
            bestehend = next((u for u in antwort.json()["users"] if u["username"] == name), None)
            if bestehend is None:
                antwort = client.post("/api/v1/users/", json={"username": name, "password": passwort})
                antwort.raise_for_status()
                konto_id, ergebnis = antwort.json()["id"], "neu"
            else:
                konto_id, ergebnis = bestehend["id"], "aktualisiert"
            # Auch bei neuen Konten: ob sie aktiv angelegt werden, hängt von LANGFLOW_NEW_USER_IS_ACTIVE ab.
            antwort = client.patch(f"/api/v1/users/{konto_id}", json={"password": passwort, "is_active": True})
            antwort.raise_for_status()
        return ergebnis

    def flows_verteilen(self, token: str, flows: list[dict]) -> list[str]:
        """Lädt die Flows hoch, die das Konto noch nicht hat. Gibt ihre Namen zurück."""
        with self._client(token) as client:
            antwort = client.get("/api/v1/flows/", params={"get_all": True, "header_flows": True})
            antwort.raise_for_status()
            vorhanden = {flow["name"] for flow in antwort.json()}
            neu = fehlende_flows(flows, vorhanden)
            for flow in neu:
                client.post("/api/v1/flows/", json=flow).raise_for_status()
        return [flow["name"] for flow in neu]


def main() -> int:
    langflow = Langflow(os.environ.get("LANGFLOW_URL", "http://langflow"))
    konten = konten_lesen(os.environ["GRUPPEN_KONTEN"])
    flows = flows_lesen(Path(os.environ.get("FLOWS_PFAD", "/app/flows")))
    print(f"{len(konten)} Konten, {len(flows)} Flows")

    langflow.warten()
    admin = langflow.anmelden(os.environ["LANGFLOW_SUPERUSER"], os.environ["LANGFLOW_SUPERUSER_PASSWORD"])
    for name, passwort in konten.items():
        ergebnis = langflow.konto_sicherstellen(admin, name, passwort)
        hochgeladen = langflow.flows_verteilen(langflow.anmelden(name, passwort), flows)
        print(f"{name}: Konto {ergebnis}, {len(hochgeladen)} Flows hochgeladen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
