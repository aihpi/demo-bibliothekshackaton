"""Katalogsuche: sucht Bücher und andere Medien im Verbundkatalog des hbz (lobid.org).

Crossref und OpenAlex kennen vor allem Zeitschriftenartikel. Bücher, Sammelbände und
deutschsprachige Literatur findet man besser im Bibliothekskatalog.
"""

import httpx
from lfx.custom.custom_component.component import Component
from lfx.io import IntInput, MessageTextInput, Output
from lfx.schema.dataframe import DataFrame
from lfx.schema.message import Message

LOBID = "https://lobid.org/resources/search"


def _eintrag(treffer: dict) -> dict:
    beteiligte = [b.get("agent", {}).get("label", "") for b in treffer.get("contribution", [])]
    veroeffentlichung = (treffer.get("publication") or [{}])[0]
    verlag = ", ".join(veroeffentlichung.get("publishedBy", []) or [])
    return {
        "titel": treffer.get("title", ""),
        "autoren": "; ".join(b for b in beteiligte[:4] if b),
        "jahr": veroeffentlichung.get("startDate", ""),
        "verlag": verlag,
        "isbn": ", ".join((treffer.get("isbn") or [])[:2]),
        "medium": ", ".join(m.get("label", "") for m in treffer.get("medium", [])[:2]),
        "link": (treffer.get("id") or "").split("#")[0],
    }


class KatalogsucheComponent(Component):
    display_name = "Katalogsuche (hbz / lobid)"
    description = "Sucht Bücher und Medien im hbz-Verbundkatalog – gut für Literatur ohne DOI."
    icon = "book-open"
    name = "Katalogsuche"

    inputs = [
        MessageTextInput(
            name="suchanfrage",
            display_name="Suchanfrage",
            info="Titel, Autor:in oder Stichwörter, z. B. 'Umberto Eco Wie man eine wissenschaftliche Abschlussarbeit schreibt'.",
            tool_mode=True,
            required=True,
        ),
        IntInput(name="anzahl", display_name="Anzahl Treffer", value=5),
    ]

    outputs = [
        Output(display_name="Treffer (Text)", name="liste", method="katalog_durchsuchen", group_outputs=True),
        Output(display_name="Treffer (Tabelle)", name="tabelle", method="tabelle_erstellen", tool_mode=False, group_outputs=True),
    ]

    def _suchen(self) -> list[dict]:
        antwort = httpx.get(LOBID, params={"q": self.suchanfrage, "format": "json", "size": self.anzahl}, timeout=30)
        antwort.raise_for_status()
        return [_eintrag(t) for t in antwort.json().get("member", [])]

    def tabelle_erstellen(self) -> DataFrame:
        return DataFrame(self._suchen())

    def katalog_durchsuchen(self) -> Message:
        treffer = self._suchen()
        if not treffer:
            return Message(text=f"Keine Treffer im Katalog für „{self.suchanfrage}“.")
        text = "\n".join(
            f"- {t['autoren']}: {t['titel']} ({t['jahr']}, {t['verlag']}). ISBN {t['isbn'] or '–'}. {t['link']}"
            for t in treffer
        )
        self.status = text
        return Message(text=text)
