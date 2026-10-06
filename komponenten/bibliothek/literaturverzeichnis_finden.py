"""Literaturverzeichnis finden: schneidet das Literaturverzeichnis aus einem langen Text aus,
z. B. aus einer hochgeladenen Masterarbeit (PDF, Word, Text)."""

import re

from lfx.custom.custom_component.component import Component
from lfx.io import MultilineInput, Output
from lfx.schema.message import Message

UEBERSCHRIFT = re.compile(
    r"^\s*(?:\d{1,2}\.?\s+|[IVX]+\.?\s+)?"
    r"(Literaturverzeichnis|Literatur|Quellenverzeichnis|Quellen|Bibliographie|Bibliografie|"
    r"Referenzen|References|Bibliography|Works Cited|Reference List)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
ENDE = re.compile(
    r"^\s*(?:\d{1,2}\.?\s+|[A-Z]\.?\s+)?(Anhang|Anhänge|Appendix|Appendices|Abbildungsverzeichnis|"
    r"Eidesstattliche Erklärung|Selbstständigkeitserklärung|Selbständigkeitserklärung|Erklärung)\b",
    re.IGNORECASE | re.MULTILINE,
)


class LiteraturverzeichnisFindenComponent(Component):
    display_name = "Literaturverzeichnis finden"
    description = "Schneidet das Literaturverzeichnis aus einem langen Dokument aus (z. B. einer Abschlussarbeit)."
    icon = "scissors"
    name = "LiteraturverzeichnisFinden"

    inputs = [
        MultilineInput(
            name="dokument",
            display_name="Dokumenttext",
            info="Der vollständige Text, z. B. aus dem Baustein 'Read File'.",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Literaturverzeichnis", name="verzeichnis", method="verzeichnis_finden"),
    ]

    def verzeichnis_finden(self) -> Message:
        text = self.dokument or ""
        treffer = list(UEBERSCHRIFT.finditer(text))
        if not treffer:
            self.status = "Keine Überschrift 'Literaturverzeichnis' gefunden – der ganze Text wird weitergegeben."
            return Message(text=text)
        # Die letzte passende Überschrift nehmen: das Inhaltsverzeichnis nennt sie auch schon am Anfang
        rest = text[treffer[-1].end():]
        ende = ENDE.search(rest)
        verzeichnis = rest[: ende.start()] if ende else rest
        self.status = f"Literaturverzeichnis gefunden ({len(verzeichnis)} Zeichen)."
        return Message(text=verzeichnis.strip())
