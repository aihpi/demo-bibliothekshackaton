"""Volltexte holen: lädt frei verfügbare Volltexte (Open Access) herunter und macht Text daraus.

Der Baustein nimmt die Tabelle aus 'Literatursuche (OpenAlex)' oder 'Quellen anreichern'.
Für jede Publikation mit freiem Volltext wird das PDF geladen und der Text ausgelesen.
Gibt es keinen Volltext, wird ersatzweise das Abstract verwendet.
"""

import asyncio
import io
import logging
import os
import re

import httpx
from bs4 import BeautifulSoup
from lfx.custom.custom_component.component import Component
from lfx.io import DataFrameInput, IntInput, Output, SecretStrInput
from lfx.schema.dataframe import DataFrame
from lfx.schema.message import Message
from lfx.utils.secrets import secret_value_to_str
from pypdf import PdfReader

logging.getLogger("pypdf").setLevel(logging.ERROR)  # keine Schrift-Warnungen im Protokoll

MAX_BYTES = 30 * 1024 * 1024
BROWSER = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
LITERATUR = re.compile(r"\n\s*(References|Bibliography|Literatur|Literaturverzeichnis|Works Cited)\s*\n", re.IGNORECASE)


def pdf_zu_text(inhalt: bytes, max_seiten: int = 40) -> str:
    leser = PdfReader(io.BytesIO(inhalt))
    return "\n".join((seite.extract_text() or "") for seite in leser.pages[:max_seiten])


def kuerzen(text: str, max_zeichen: int) -> str:
    """Literaturverzeichnis abschneiden, dann Anfang und Schluss behalten (Einleitung und Fazit)."""
    text = re.sub(r"[ \t]+", " ", text)
    treffer = list(LITERATUR.finditer(text))
    if treffer and treffer[-1].start() > len(text) * 0.5:
        text = text[: treffer[-1].start()]
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) <= max_zeichen:
        return text
    haelfte = max_zeichen // 2
    return text[:haelfte] + "\n[…]\n" + text[-haelfte:]


class VolltexteHolenComponent(Component):
    display_name = "Volltexte holen (Open Access)"
    description = "Lädt freie Volltexte (PDF) der gefundenen Publikationen herunter. Ohne Volltext wird das Abstract genommen."
    icon = "file-down"
    name = "VolltexteHolen"

    inputs = [
        DataFrameInput(
            name="publikationen",
            display_name="Publikationen",
            info="Tabelle aus 'Literatursuche (OpenAlex)' oder 'Quellen anreichern (OpenAlex)'.",
            required=True,
        ),
        IntInput(name="max_dokumente", display_name="Höchstens Dokumente", value=8,
                 info="Wie viele Publikationen verarbeitet werden."),
        IntInput(name="max_zeichen", display_name="Zeichen pro Dokument", value=3000,
                 info="Längere Texte werden gekürzt (Anfang und Schluss bleiben). Kleine Modelle vertragen wenig Text."),
        SecretStrInput(
            name="kontakt_email",
            display_name="Kontakt-E-Mail",
            info="Für Crossref, OpenAlex und Unpaywall: schnellere Antworten und mehr freie Volltexte. Am einfachsten "
            "einmal als globale Variable KONTAKT_EMAIL anlegen (Settings → Global Variables), dann gilt sie für alle "
            "Bausteine.",
            value="KONTAKT_EMAIL",
            load_from_db=True,
            advanced=True,
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Texte für die KI", name="texte", method="texte_erstellen", group_outputs=True),
        Output(display_name="Tabelle mit Volltexten", name="tabelle", method="tabelle_erstellen", group_outputs=True),
    ]

    _zwischenspeicher: tuple | None = None

    def _kontakt(self) -> str:
        """Kontakt-E-Mail aus der globalen Variable KONTAKT_EMAIL der Gruppe, sonst aus der Umgebung (.env)."""
        wert = secret_value_to_str(self.kontakt_email) if getattr(self, "kontakt_email", None) else ""
        wert = (wert or os.getenv("KONTAKT_EMAIL", "")).strip()
        return wert if "@" in wert else ""

    async def _laden(self, client: httpx.AsyncClient, url: str) -> str:
        antwort = await client.get(url)
        antwort.raise_for_status()
        inhalt = antwort.content[:MAX_BYTES]
        if inhalt[:5] == b"%PDF-" or "pdf" in antwort.headers.get("content-type", ""):
            return await asyncio.to_thread(pdf_zu_text, inhalt)
        seite = BeautifulSoup(inhalt, "html.parser")
        for tag in seite(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        return seite.get_text("\n")

    async def _urls(self, client: httpx.AsyncClient, zeile: dict) -> list[str]:
        urls = [zeile.get("volltext_url")] if zeile.get("volltext_url") else []
        kontakt = self._kontakt()
        if zeile.get("doi") and kontakt:
            try:
                antwort = await client.get(f"https://api.unpaywall.org/v2/{zeile['doi']}", params={"email": kontakt})
                if antwort.status_code == 200:
                    for ort in antwort.json().get("oa_locations") or []:
                        if ort.get("url_for_pdf") and ort["url_for_pdf"] not in urls:
                            urls.append(ort["url_for_pdf"])
            except httpx.HTTPError:
                pass
        return urls

    async def _verarbeiten(self, client: httpx.AsyncClient, zeile: dict) -> dict:
        zeile = dict(zeile)
        zeile["volltext"], zeile["inhalt_quelle"] = "", "Abstract"
        if zeile.get("open_access", True):
            for url in await self._urls(client, zeile):
                try:
                    text = await self._laden(client, url)
                except Exception:  # noqa: BLE001 - nächste Quelle versuchen
                    continue
                if len(text.strip()) > 2000:
                    zeile["volltext"], zeile["inhalt_quelle"] = kuerzen(text, self.max_zeichen), "Volltext"
                    zeile["volltext_von"] = url
                    break
        zeile["inhalt"] = zeile["volltext"] or zeile.get("abstract") or ""
        if not zeile["inhalt"]:
            zeile["inhalt_quelle"] = "kein Text"
        return zeile

    async def _alle(self) -> list[dict]:
        df = self.publikationen
        zeilen = df.to_dict(orient="records") if hasattr(df, "to_dict") else list(df or [])
        zeilen = zeilen[: self.max_dokumente]
        schluessel = (tuple(z.get("doi") or z.get("titel") for z in zeilen), self.max_zeichen)
        if self._zwischenspeicher and self._zwischenspeicher[0] == schluessel:
            return self._zwischenspeicher[1]
        begrenzung = asyncio.Semaphore(4)
        async with httpx.AsyncClient(timeout=40, follow_redirects=True, headers={"User-Agent": BROWSER}) as client:

            async def begrenzt(zeile: dict) -> dict:
                async with begrenzung:
                    return await self._verarbeiten(client, zeile)

            ergebnis = await asyncio.gather(*(begrenzt(z) for z in zeilen))
        self._zwischenspeicher = (schluessel, ergebnis)
        return ergebnis

    async def tabelle_erstellen(self) -> DataFrame:
        zeilen = await self._alle()
        self.status = f"{sum(z['inhalt_quelle'] == 'Volltext' for z in zeilen)} von {len(zeilen)} Volltexten geladen"
        return DataFrame(zeilen)

    async def texte_erstellen(self) -> Message:
        zeilen = await self._alle()
        teile = []
        for i, z in enumerate(zeilen, start=1):
            nr = z.get("nr") or i
            teile.append(f"=== [{nr}] {z.get('autoren', '')} ({z.get('jahr', '')}): {z.get('titel', '')}\n"
                         f"Zeitschrift: {z.get('zeitschrift', '')} | Zitiert: {z.get('zitiert', '')} | "
                         f"Grundlage: {z['inhalt_quelle']}\n{z['inhalt']}")
        volltexte = sum(z["inhalt_quelle"] == "Volltext" for z in zeilen)
        self.status = f"{volltexte} Volltexte, {len(zeilen) - volltexte} nur Abstract"
        return Message(text="\n\n".join(teile))
