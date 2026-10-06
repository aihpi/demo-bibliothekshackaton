"""KI-Modell: ein Sprachmodell aus dem Cluster (LiteLLM) oder lokal (Ollama).

Adressen, Schlüssel und Standardmodelle kommen aus der Datei .env, damit Teilnehmende
nichts eintragen müssen.
"""

import os

import httpx
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from lfx.base.models.model import LCModelComponent
from lfx.field_typing import LanguageModel
from lfx.field_typing.range_spec import RangeSpec
from lfx.inputs.inputs import BoolInput, DropdownInput, IntInput, SecretStrInput, SliderInput, StrInput
from lfx.utils.secrets import secret_value_to_str

STANDARD = "Standard (aus .env)"
CLUSTER = "Cluster (LiteLLM)"
LOKAL = "Lokal (Ollama)"


class KIModellComponent(LCModelComponent):
    display_name = "KI-Modell"
    description = "Sprachmodell aus dem Cluster (LiteLLM) oder lokal auf dem Laptop (Ollama)."
    icon = "brain"
    name = "KIModell"

    inputs = [
        *LCModelComponent.get_base_inputs(),
        DropdownInput(
            name="quelle",
            display_name="Quelle",
            info="Woher das Modell kommt. 'Standard' nimmt die Einstellung KI_STANDARD aus der Datei .env.",
            options=[STANDARD, CLUSTER, LOKAL],
            value=STANDARD,
            real_time_refresh=True,
        ),
        DropdownInput(
            name="model_name",
            display_name="Modell",
            info="Leer lassen für das Standardmodell. Mit dem Pfeil-Knopf die verfügbaren Modelle laden.",
            options=[],
            value="",
            combobox=True,
            refresh_button=True,
        ),
        SliderInput(
            name="temperature",
            display_name="Kreativität (Temperatur)",
            info="0 = sachlich und wiederholbar, 1 = kreativ und abwechslungsreich.",
            value=0.1,
            range_spec=RangeSpec(min=0, max=1, step=0.05),
        ),
        BoolInput(
            name="denken",
            display_name="Nachdenken erlauben",
            info="Erlaubt 'Reasoning'-Modellen, vor der Antwort nachzudenken. Genauer, aber deutlich langsamer.",
            value=False,
            advanced=True,
        ),
        IntInput(
            name="max_tokens",
            display_name="Maximale Antwortlänge (Tokens)",
            info="0 = keine Begrenzung.",
            value=0,
            advanced=True,
        ),
        StrInput(
            name="base_url",
            display_name="Adresse (überschreiben)",
            info="Nur ausfüllen, um die Adresse aus der .env zu überschreiben, z. B. http://host.docker.internal:11434/v1",
            advanced=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="API-Schlüssel (überschreiben)",
            info="Nur ausfüllen, um den Schlüssel aus der .env zu überschreiben.",
            value="",
            load_from_db=False,
            advanced=True,
        ),
        IntInput(
            name="timeout",
            display_name="Zeitlimit (Sekunden)",
            value=600,
            advanced=True,
        ),
    ]

    def _quelle(self, quelle: str | None = None) -> str:
        quelle = quelle or self.quelle
        if quelle == STANDARD:
            return LOKAL if os.getenv("KI_STANDARD", "cluster").strip().lower().startswith("lokal") else CLUSTER
        return quelle

    def _verbindung(self, quelle: str | None = None) -> tuple[str, str, str]:
        """Adresse, Schlüssel und Standardmodell der gewählten Quelle."""
        if self._quelle(quelle) == LOKAL:
            url = os.getenv("LOKAL_BASE_URL", "http://host.docker.internal:11434/v1")
            key = os.getenv("LOKAL_API_KEY", "ollama")
            modell = os.getenv("LOKAL_MODELL", "qwen3.5:4b")
        else:
            url = os.getenv("CLUSTER_BASE_URL", "")
            key = os.getenv("CLUSTER_API_KEY", "")
            modell = os.getenv("CLUSTER_MODELL", "")
        if getattr(self, "base_url", None):
            url = self.base_url
        if getattr(self, "api_key", None):
            key = secret_value_to_str(self.api_key)
        return url.rstrip("/"), key or "kein-schluessel", modell

    def build_model(self) -> LanguageModel:  # type: ignore[type-var]
        url, key, standardmodell = self._verbindung()
        modell = (self.model_name or "").strip() or standardmodell
        if not url:
            msg = "Keine Adresse für das KI-Modell. Bitte CLUSTER_BASE_URL in der Datei .env eintragen oder 'Lokal' wählen."
            raise ValueError(msg)
        if not modell:
            msg = "Kein Modell gewählt. Bitte ein Modell auswählen oder CLUSTER_MODELL / LOKAL_MODELL in der .env setzen."
            raise ValueError(msg)

        if self._quelle() == LOKAL:
            # Ollamas eigene Schnittstelle statt der OpenAI-kompatiblen: nur dort lässt sich die
            # Kontextlänge setzen. Sonst schneidet Ollama lange Texte stillschweigend bei 4096 Tokens ab.
            return ChatOllama(
                model=modell,
                base_url=url.removesuffix("/v1"),
                temperature=self.temperature,
                num_ctx=int(os.getenv("LOKAL_KONTEXT", "16384")),
                num_predict=self.max_tokens or None,
                reasoning=self.denken,
                client_kwargs={"timeout": self.timeout},
            )
        return ChatOpenAI(
            model=modell,
            base_url=url,
            api_key=key,
            temperature=self.temperature,
            max_tokens=self.max_tokens or None,
            timeout=self.timeout,
            max_retries=2,
        )

    def _modelle_laden(self, quelle: str) -> list[str]:
        url, key, _ = self._verbindung(quelle)
        if not url:
            return []
        try:
            antwort = httpx.get(f"{url}/models", headers={"Authorization": f"Bearer {key}"}, timeout=10)
            antwort.raise_for_status()
            return sorted(m["id"] for m in antwort.json().get("data", []))
        except Exception:  # noqa: BLE001 - Liste bleibt dann einfach leer
            return []

    def update_build_config(self, build_config: dict, field_value, field_name: str | None = None):
        if field_name in {"quelle", "model_name"}:
            quelle = field_value if field_name == "quelle" else build_config["quelle"]["value"]
            build_config["model_name"]["options"] = self._modelle_laden(quelle)
        return build_config
