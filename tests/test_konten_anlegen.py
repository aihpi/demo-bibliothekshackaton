import json

import httpx
import konten_anlegen as ka
import pytest


class FalschesLangflow:
    """Gerade genug von Langflows API: Konten, Anmeldung und Flows je Konto."""

    def __init__(self):
        self.konten = {"orga": {"id": "id-orga", "passwort": "admin", "is_active": True}}
        self.flows: dict[str, list[dict]] = {"orga": []}

    def konto_zum_token(self, request: httpx.Request) -> str:
        return request.headers["Authorization"].removeprefix("Bearer token-")

    def __call__(self, request: httpx.Request) -> httpx.Response:
        pfad, methode = request.url.path, request.method
        if pfad == "/health_check":
            return httpx.Response(200, json={"status": "ok"})
        if pfad == "/api/v1/login":
            daten = dict(x.split("=") for x in request.content.decode().split("&"))
            konto = self.konten.get(daten["username"])
            if konto is None or konto["passwort"] != daten["password"] or not konto["is_active"]:
                return httpx.Response(401)
            return httpx.Response(200, json={"access_token": f"token-{daten['username']}"})
        nutzer = self.konto_zum_token(request)
        if pfad == "/api/v1/users/" and methode == "GET":
            assert nutzer == "orga"
            liste = [{"id": k["id"], "username": n} for n, k in self.konten.items()]
            return httpx.Response(200, json={"total_count": len(liste), "users": liste})
        if pfad == "/api/v1/users/" and methode == "POST":
            daten = json.loads(request.content)
            self.konten[daten["username"]] = {
                "id": f"id-{daten['username']}",
                "passwort": daten["password"],
                "is_active": False,
            }
            self.flows[daten["username"]] = []
            return httpx.Response(201, json={"id": f"id-{daten['username']}"})
        if pfad.startswith("/api/v1/users/") and methode == "PATCH":
            konto = next(k for k in self.konten.values() if k["id"] == pfad.rsplit("/", 1)[1])
            daten = json.loads(request.content)
            konto["passwort"], konto["is_active"] = daten["password"], daten["is_active"]
            return httpx.Response(200, json={})
        if pfad == "/api/v1/flows/" and methode == "GET":
            return httpx.Response(200, json=self.flows[nutzer])
        if pfad == "/api/v1/flows/" and methode == "POST":
            flow = json.loads(request.content)
            assert "id" not in flow
            self.flows[nutzer].append(flow)
            return httpx.Response(201, json=flow)
        return httpx.Response(404)


FLOWS = [{"name": "00 Hallo", "data": {}}, {"name": "01 Checker", "data": {}}]


@pytest.fixture
def langflow():
    falsch = FalschesLangflow()
    return falsch, ka.Langflow("http://langflow", transport=httpx.MockTransport(falsch))


def test_konten_lesen_skips_blank_lines_and_comments():
    text = "\n# Kommentar\ngruppe01: geheim-1\n  gruppe02:pass:mit:doppelpunkt  \n"
    assert ka.konten_lesen(text) == {"gruppe01": "geheim-1", "gruppe02": "pass:mit:doppelpunkt"}


@pytest.mark.parametrize("text", ["gruppe01", "gruppe01:", ":geheim", "gruppe01:a\ngruppe01:b"])
def test_konten_lesen_refuses_broken_lines(text):
    with pytest.raises(ValueError):
        ka.konten_lesen(text)


def test_flows_lesen_drops_the_id_of_the_admin_copy(tmp_path):
    (tmp_path / "00.json").write_text(json.dumps({"id": "abc", "name": "00 Hallo", "data": {}, "folder_id": "x"}))
    assert ka.flows_lesen(tmp_path) == [{"name": "00 Hallo", "data": {}}]


def test_new_account_is_created_activated_and_gets_all_flows(langflow):
    falsch, client = langflow
    admin = client.anmelden("orga", "admin")
    assert client.konto_sicherstellen(admin, "gruppe01", "pw1") == "neu"
    assert falsch.konten["gruppe01"]["is_active"]
    hochgeladen = client.flows_verteilen(client.anmelden("gruppe01", "pw1"), FLOWS)
    assert hochgeladen == ["00 Hallo", "01 Checker"]
    assert falsch.flows["orga"] == []


def test_second_run_keeps_what_the_group_built(langflow):
    falsch, client = langflow
    admin = client.anmelden("orga", "admin")
    client.konto_sicherstellen(admin, "gruppe01", "pw1")
    token = client.anmelden("gruppe01", "pw1")
    client.flows_verteilen(token, FLOWS)
    falsch.flows["gruppe01"][0]["data"] = {"von": "der Gruppe geändert"}
    falsch.flows["gruppe01"].append({"name": "Eigener Flow", "data": {}})

    assert client.konto_sicherstellen(admin, "gruppe01", "pw1") == "aktualisiert"
    assert client.flows_verteilen(token, FLOWS) == []
    assert [f["name"] for f in falsch.flows["gruppe01"]] == ["00 Hallo", "01 Checker", "Eigener Flow"]
    assert falsch.flows["gruppe01"][0]["data"] == {"von": "der Gruppe geändert"}


def test_changed_password_in_the_secret_takes_effect(langflow):
    falsch, client = langflow
    admin = client.anmelden("orga", "admin")
    client.konto_sicherstellen(admin, "gruppe01", "alt")
    client.konto_sicherstellen(admin, "gruppe01", "neu")
    assert falsch.konten["gruppe01"]["passwort"] == "neu"


def test_a_deleted_example_flow_comes_back(langflow):
    falsch, client = langflow
    admin = client.anmelden("orga", "admin")
    client.konto_sicherstellen(admin, "gruppe01", "pw1")
    token = client.anmelden("gruppe01", "pw1")
    client.flows_verteilen(token, FLOWS)
    falsch.flows["gruppe01"].pop(0)
    assert client.flows_verteilen(token, FLOWS) == ["00 Hallo"]


def test_login_waits_when_langflow_limits_logins(monkeypatch):
    antworten = iter(
        [httpx.Response(429, headers={"retry-after": "0"}), httpx.Response(200, json={"access_token": "t"})]
    )
    client = ka.Langflow("http://langflow", transport=httpx.MockTransport(lambda request: next(antworten)))
    monkeypatch.setattr(ka.time, "sleep", lambda sekunden: None)
    assert client.anmelden("gruppe01", "pw") == "t"
