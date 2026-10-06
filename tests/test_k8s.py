"""Consistency checks for the manifests under k8s/, which no test cluster runs in CI."""

import re
from pathlib import Path

import yaml

WURZEL = Path(__file__).resolve().parent.parent
K8S = WURZEL / "k8s"


def _dokumente() -> list[dict]:
    dokumente = []
    for datei in sorted(K8S.rglob("*.yaml")):
        if datei.name == "secret.yaml":  # plaintext, gitignored, not part of the deployment
            continue
        dokumente.extend(d for d in yaml.safe_load_all(datei.read_text()) if d)
    return dokumente


def _secret_keys_referenziert() -> set[str]:
    text = "\n".join(p.read_text() for p in K8S.rglob("*.yaml") if p.name != "secret.yaml")
    return set(re.findall(r"secretKeyRef:\s*\n\s*name: bibliothekshackathon-secret\s*\n\s*key: (\w+)", text))


def test_every_referenced_secret_key_is_documented_in_the_example():
    beispiel = yaml.safe_load((K8S / "secrets" / "example-secret.yaml").read_text())
    fehlend = _secret_keys_referenziert() - set(beispiel["stringData"])
    assert not fehlend, f"in example-secret.yaml nicht dokumentiert: {fehlend}"


def test_every_resource_is_listed_in_the_kustomization():
    kustomization = yaml.safe_load((K8S / "kustomization.yaml").read_text())
    gelistet = set(kustomization["resources"])
    vorhanden = {
        str(p.relative_to(K8S))
        for p in K8S.rglob("*.yaml")
        if p.name not in {"kustomization.yaml", "secret.yaml", "example-secret.yaml"}
    }
    assert vorhanden == gelistet


def test_ci_rewrites_the_image_that_the_manifests_run():
    workflow = (WURZEL / ".github" / "workflows" / "docker-publish.yml").read_text()
    image = re.search(r"IMAGE: ghcr.io/\$\{\{ github.repository \}\}/(\S+)", workflow).group(1)
    eigene = [
        container["image"]
        for d in _dokumente()
        if d["kind"] in {"Deployment", "Job"}
        for container in d["spec"]["template"]["spec"]["containers"]
        if "postgres" not in container["image"]
    ]
    assert eigene
    assert all(i.startswith(f"ghcr.io/aihpi/demo-bibliothekshackaton/{image}:") for i in eigene)


def test_langflow_runs_in_multi_user_mode_without_user_code():
    config = next(d for d in _dokumente() if d["kind"] == "ConfigMap" and d["metadata"]["name"] == "langflow-config")
    daten = config["data"]
    assert daten["LANGFLOW_AUTO_LOGIN"] == "false"
    assert daten["LANGFLOW_ENABLE_SIGNUP"] == "false"
    assert daten["LANGFLOW_ALLOW_CUSTOM_COMPONENTS"] == "false"
    assert daten["LANGFLOW_BLOCK_CODE_INTERPRETER_COMPONENTS"] == "true"
