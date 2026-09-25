"""Literaturangaben prüfen: Gibt es die zitierten Publikationen wirklich?

Jede Angabe wird bei Crossref gesucht (per DOI oder als Freitext) und mit dem Treffer
verglichen: Titel, Jahr und Erstautor:in. Zurückgezogene Artikel werden markiert.
"""

import asyncio
import os
import re
import unicodedata

import httpx
from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, IntInput, MultilineInput, Output
from lfx.schema.dataframe import DataFrame
from lfx.schema.message import Message
from rapidfuzz import fuzz

CROSSREF = "https://api.crossref.org"
DOI_MUSTER = re.compile(r"10\.\d{4,9}/[^\s\"<>]+", re.IGNORECASE)
JAHR_MUSTER = re.compile(r"\b(19\d{2}|20\d{2})\b")
NUMMER_MUSTER = re.compile(r"^\s*(\[\d{1,3}\]|\(\d{1,3}\)|\d{1,3}[.)])\s+", re.MULTILINE)
AUTOR_ANFANG = re.compile(
    r"^(?:[A-ZÄÖÜ][\w'’\-]+(?: [a-z]{1,3})?,\s*(?:[A-ZÄÖÜ]\.|[A-ZÄÖÜ][a-zäöüß]+)"  # "Müller, K." / "Eco, Umberto"
    r"|[A-ZÄÖÜ][^()\n]{0,80}\((?:19|20)\d{2}[a-z]?\))"  # "Deutsche Forschungsgemeinschaft. (2019)"
)
FORTSETZUNG = re.compile(r"(?:[,&]|\band|\bund|\b[A-ZÄÖÜ]\.)\s*$")  # Zeile endet mitten in der Autorenliste


def literaturangaben_zerlegen(text: str) -> list[str]:
    """Zerlegt ein Literaturverzeichnis in einzelne Angaben.

    Erkennt nummerierte Verzeichnisse ([1], 1., (1)), Angaben mit Leerzeilen dazwischen und
    Verzeichnisse aus PDFs, in denen lange Angaben über mehrere Zeilen umbrochen sind.
    """
    text = text.replace("\r\n", "\n").replace("\u00ad", "")
    if len(NUMMER_MUSTER.findall(text)) >= 2:
        teile = NUMMER_MUSTER.split(text)
        angaben = [teile[i + 1] for i in range(1, len(teile) - 1, 2)]
    else:
        absaetze = [a for a in re.split(r"\n\s*\n", text) if a.strip()]
        zeilenweise: list[str] = []
        for zeile in text.split("\n"):
            if not zeile.strip():
                continue
            neu = AUTOR_ANFANG.match(zeile.strip()) and not (zeilenweise and FORTSETZUNG.search(zeilenweise[-1]))
            if neu or not zeilenweise:
                zeilenweise.append(zeile.strip())
            else:
                zeilenweise[-1] += "\n" + zeile.strip()
        angaben = absaetze if len(absaetze) >= len(zeilenweise) else zeilenweise
    ergebnis = []
    for angabe in angaben:
        angabe = re.sub(r"(\w)-\n(\w)", r"\1\2", angabe.strip())
        angabe = re.sub(r"\s+", " ", angabe)
        if len(angabe) >= 25:
            ergebnis.append(angabe)
    return ergebnis


def _normal(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", text.lower())


def _kompakt(text: str) -> str:
    """Nur Buchstaben und Ziffern: 'Large-scale' und 'Largescale' (PDF-Umbruch) sind dann gleich."""
    return _normal(text).replace(" ", "")


def titel_aehnlichkeit(titel: str, angabe: str) -> float:
    """Wie gut steckt der Titel in der Angabe? Klammerzusätze wie '(Come si fa una tesi)' zählen nicht."""
    ohne_klammern = re.sub(r"\s*[(\[][^)\]]*[)\]]", "", titel)
    kandidaten = [t for t in {titel, ohne_klammern} if len(t) >= 8]
    return max((fuzz.partial_ratio(_kompakt(t), _kompakt(angabe)) for t in kandidaten), default=0)


def _jahr(eintrag: dict) -> int | None:
    for feld in ("issued", "published-print", "published-online"):
        teile = (eintrag.get(feld) or {}).get("date-parts") or [[None]]
        if teile[0] and teile[0][0]:
            return int(teile[0][0])
    return None


def voller_titel(eintrag: dict) -> str:
    """Crossref speichert Untertitel getrennt: 'The intelligent library' + 'Thought leaders' views ...'."""
    titel = (eintrag.get("title") or [""])[0]
    untertitel = (eintrag.get("subtitle") or [""])[0]
    return f"{titel}: {untertitel}" if untertitel and untertitel.lower() not in titel.lower() else titel


def _erstautor_passt(erstautor: str, angabe: str) -> bool:
    """Steht der/die Erstautor:in von Crossref auch am Anfang der Literaturangabe?"""
    if not erstautor:
        return True
    name = _normal(erstautor).strip()
    anfang = _normal(angabe[:60]).split()
    if not anfang:
        return False
    if len(anfang[0]) <= 2:  # Angabe beginnt mit Initialen, z. B. "J. Smith and ..."
        return name in " ".join(anfang[:6])
    return fuzz.ratio(anfang[0], name.split()[-1] if name else "") >= 80 or anfang[0] in name


def _bewertung(eintrag: dict, angabe: str) -> tuple[float, float, bool, bool]:
    """Wie gut passt ein Crossref-Eintrag zur Angabe? (Gesamtwert, Titelähnlichkeit, Jahr ok, Autor ok)"""
    ohne_hinweis = r"^(RETRACTED|WITHDRAWN)\s*[:\-–]\s*"
    titel = re.sub(ohne_hinweis, "", voller_titel(eintrag), flags=re.IGNORECASE)
    haupttitel = re.sub(ohne_hinweis, "", (eintrag.get("title") or [""])[0], flags=re.IGNORECASE)
    # Viele Angaben lassen den Untertitel weg: dann zählt auch der Haupttitel allein
    aehnlichkeit = max(titel_aehnlichkeit(titel, angabe),
                       titel_aehnlichkeit(haupttitel, angabe) if len(haupttitel) >= 20 else 0)
    jahr = _jahr(eintrag)
    jahre = {int(j) for j in JAHR_MUSTER.findall(angabe)}
    jahr_ok = not jahre or jahr is None or any(abs(j - jahr) <= 1 for j in jahre)
    erstautor = next((a.get("family") or a.get("name", "") for a in eintrag.get("author", [])), "")
    autor_ok = _erstautor_passt(erstautor, angabe)
    # Titel zählt am meisten; bei gleichem Titel lieber den Artikel als den Preprint nehmen
    gesamt = aehnlichkeit + 3 * jahr_ok + 3 * autor_ok + 5 * (eintrag.get("type") != "posted-content")
    return gesamt, aehnlichkeit, jahr_ok, autor_ok


def passt(eintrag: dict, aehnlichkeit: float, jahr_ok: bool, autor_ok: bool) -> bool:
    """Ist der Treffer dieselbe Publikation? Kurze Titel ('Introduction') brauchen Jahr und Autor:in."""
    if len(voller_titel(eintrag)) < 30:
        return aehnlichkeit >= 90 and jahr_ok and autor_ok
    return aehnlichkeit >= 85 and (jahr_ok or autor_ok)


def _autoren(eintrag: dict) -> str:
    namen = [a.get("family") or a.get("name", "") for a in eintrag.get("author", [])]
    return ", ".join(namen[:3]) + (" u. a." if len(namen) > 3 else "")


class ReferenzenPruefenComponent(Component):
    display_name = "Literaturangaben prüfen (Crossref)"
    description = "Prüft, ob zitierte Publikationen existieren und korrekt angegeben sind. Markiert zurückgezogene Artikel."
    icon = "list-checks"
    name = "ReferenzenPruefen"

    inputs = [
        MultilineInput(
            name="literaturangaben",
            display_name="Literaturangaben",
            info="Ein Literaturverzeichnis: nummeriert, durch Leerzeilen getrennt oder eine Angabe pro Zeile.",
            tool_mode=True,
            required=True,
        ),
        IntInput(
            name="max_angaben",
            display_name="Höchstens prüfen",
            info="Wie viele Angaben maximal geprüft werden (schont die Crossref-Schnittstelle).",
            value=40,
        ),
        BoolInput(
            name="rueckzuege_pruefen",
            display_name="Auf zurückgezogene Artikel prüfen",
            info="Fragt bei Crossref / Retraction Watch nach, ob ein Artikel zurückgezogen wurde.",
            value=True,
        ),
    ]

    outputs = [
        Output(display_name="Prüfbericht", name="bericht", method="literaturangaben_pruefen", group_outputs=True),
        Output(display_name="Tabelle", name="tabelle", method="tabelle_erstellen", tool_mode=False, group_outputs=True),
    ]

    _zwischenspeicher: tuple | None = None

    def _kopfzeilen(self) -> dict:
        kontakt = os.getenv("KONTAKT_EMAIL", "")
        agent = "Bibliothekshackathon-Demo (Langflow)" + (f"; mailto:{kontakt}" if kontakt else "")
        return {"User-Agent": agent}

    async def _get(self, client: httpx.AsyncClient, url: str, params: dict | None = None) -> httpx.Response:
        """Anfrage an Crossref; bei Überlastung (HTTP 429) kurz warten und erneut versuchen."""
        for versuch in range(4):
            antwort = await client.get(url, params=params)
            if antwort.status_code not in {429, 503} or versuch == 3:
                return antwort
            await asyncio.sleep(float(antwort.headers.get("retry-after", 0)) or 2 * (versuch + 1))
        return antwort

    async def _datacite(self, client: httpx.AsyncClient, doi: str) -> dict | None:
        """Sucht eine DOI bei DataCite und gibt sie im Crossref-Format zurück."""
        antwort = await client.get(f"https://api.datacite.org/dois/{doi}")
        if antwort.status_code != 200:
            return None
        daten = antwort.json()["data"]["attributes"]
        return {
            "DOI": daten.get("doi", doi),
            "title": [(daten.get("titles") or [{}])[0].get("title", "")],
            "author": [{"family": c.get("familyName") or c.get("name", "")} for c in daten.get("creators", [])],
            "issued": {"date-parts": [[daten.get("publicationYear")]]},
            "container-title": [daten.get("publisher") if isinstance(daten.get("publisher"), str)
                                else (daten.get("publisher") or {}).get("name", "")],
        }

    async def _suchen(self, client: httpx.AsyncClient, angabe: str) -> dict | None:
        antwort = await self._get(
            client,
            f"{CROSSREF}/works",
            params={"query.bibliographic": angabe[:400], "rows": 10,
                    "select": "DOI,title,subtitle,author,issued,container-title,type,score"},
        )
        antwort.raise_for_status()
        treffer = antwort.json()["message"]["items"]
        # Nicht blind den ersten Treffer nehmen: Crossref sortiert oft Werke *über* die Publikation nach vorn
        return max(treffer, key=lambda t: _bewertung(t, angabe)[0]) if treffer else None

    async def _pruefen(self, client: httpx.AsyncClient, nr: int, angabe: str) -> dict:
        zeile = {"nr": nr, "angabe": angabe, "status": "", "hinweise": "", "doi": "",
                 "gefundener_titel": "", "autoren": "", "jahr": "", "zeitschrift": ""}
        hinweise = []
        try:
            eintrag = None
            ueber_doi = False
            doi = DOI_MUSTER.search(angabe)
            if doi:
                doi_text = doi.group(0).rstrip(".,;)")
                antwort = await self._get(client, f"{CROSSREF}/works/{doi_text}")
                if antwort.status_code == 404:
                    # Nicht jede DOI stammt von Crossref: Daten, Software und Berichte oft von DataCite (z. B. Zenodo)
                    eintrag = await self._datacite(client, doi_text)
                    ueber_doi = eintrag is not None
                    if eintrag is None:
                        hinweise.append(f"Die angegebene DOI {doi_text} existiert nicht.")
                else:
                    antwort.raise_for_status()
                    eintrag = antwort.json()["message"]
                    ueber_doi = True
            if eintrag is None:
                eintrag = await self._suchen(client, angabe)

            if eintrag is None:
                zeile["status"] = "❓ nicht gefunden"
                zeile["hinweise"] = " ".join(hinweise) or "Kein Treffer bei Crossref."
                return zeile

            titel = voller_titel(eintrag)
            jahr = _jahr(eintrag)
            zeile.update({
                "doi": eintrag.get("DOI", ""),
                "gefundener_titel": titel,
                "autoren": _autoren(eintrag),
                "jahr": jahr or "",
                "zeitschrift": (eintrag.get("container-title") or [""])[0],
            })

            _, aehnlichkeit, jahr_ok, autor_ok = _bewertung(eintrag, angabe)
            erstautor = next((a.get("family") or a.get("name", "") for a in eintrag.get("author", [])), "")

            if ueber_doi and not passt(eintrag, aehnlichkeit, jahr_ok, autor_ok):
                zeile["status"] = "⚠️ Abweichung"
                hinweise.append(f"Die DOI gibt es, sie gehört aber zu: „{titel}“ ({jahr}).")
            elif not passt(eintrag, aehnlichkeit, jahr_ok, autor_ok):
                zeile["status"] = "❓ nicht gefunden"
                hinweise.append(f"Ähnlichster Treffer passt nicht: „{titel}“.")
                zeile.update({"doi": "", "gefundener_titel": "", "autoren": "", "jahr": "", "zeitschrift": ""})
            else:
                if aehnlichkeit < 95:
                    hinweise.append("Titel weicht ab.")
                if not jahr_ok:
                    buch = eintrag.get("type") in {"book", "monograph", "edited-book", "reference-book"}
                    hinweise.append(f"Jahr laut Crossref: {jahr}" + (" (bei Büchern evtl. eine andere Auflage)." if buch else "."))
                if not autor_ok:
                    hinweise.append(f"Erstautor:in laut Crossref: {erstautor}.")
                zeile["status"] = "✅ bestätigt" if not hinweise else "⚠️ Abweichung"

            if self.rueckzuege_pruefen and zeile["doi"]:
                antwort = await self._get(
                    client,
                    f"{CROSSREF}/works",
                    params={"filter": f"updates:{zeile['doi']}", "select": "DOI,update-to"},
                )
                if antwort.status_code == 200:
                    for notiz in antwort.json()["message"]["items"]:
                        for update in notiz.get("update-to", []):
                            if update.get("type") in {"retraction", "withdrawal", "removal"}:
                                zeile["status"] = "🚫 zurückgezogen"
                                hinweise.append(f"Zurückgezogen, siehe Mitteilung doi:{notiz['DOI']}.")
                                break
        except httpx.HTTPError as fehler:
            zeile["status"] = "⏳ Fehler"
            hinweise.append(f"Crossref nicht erreichbar ({type(fehler).__name__}). Später erneut versuchen.")
        zeile["hinweise"] = " ".join(hinweise)
        return zeile

    async def _alle_pruefen(self) -> list[dict]:
        schluessel = (self.literaturangaben, self.max_angaben, self.rueckzuege_pruefen)
        if self._zwischenspeicher and self._zwischenspeicher[0] == schluessel:
            return self._zwischenspeicher[1]
        angaben = literaturangaben_zerlegen(self.literaturangaben or "")[: self.max_angaben]
        # Crossref erlaubt ohne Kontakt-E-Mail nur eine Anfrage gleichzeitig, mit E-Mail drei
        begrenzung = asyncio.Semaphore(3 if os.getenv("KONTAKT_EMAIL") else 1)

        async with httpx.AsyncClient(headers=self._kopfzeilen(), timeout=30, follow_redirects=True) as client:

            async def begrenzt(nr: int, angabe: str) -> dict:
                async with begrenzung:
                    return await self._pruefen(client, nr, angabe)

            ergebnisse = await asyncio.gather(*(begrenzt(i + 1, a) for i, a in enumerate(angaben)))
        self._zwischenspeicher = (schluessel, ergebnisse)
        return ergebnisse

    async def tabelle_erstellen(self) -> DataFrame:
        ergebnisse = await self._alle_pruefen()
        self.status = f"{len(ergebnisse)} Angaben geprüft"
        return DataFrame(ergebnisse)

    async def literaturangaben_pruefen(self) -> Message:
        ergebnisse = await self._alle_pruefen()
        if not ergebnisse:
            return Message(text="Es wurden keine Literaturangaben erkannt.")
        zaehler: dict[str, int] = {}
        for zeile in ergebnisse:
            zaehler[zeile["status"]] = zaehler.get(zeile["status"], 0) + 1
        zeilen = [f"Geprüfte Angaben: {len(ergebnisse)} — " + ", ".join(f"{s}: {n}" for s, n in zaehler.items()), ""]
        for z in ergebnisse:
            zeilen.append(f"[{z['nr']}] {z['status']} — {z['angabe']}")
            if z["doi"]:
                zeilen.append(f"    Crossref: {z['autoren']} ({z['jahr']}): {z['gefundener_titel']}. "
                              f"{z['zeitschrift']}. https://doi.org/{z['doi']}")
            if z["hinweise"]:
                zeilen.append(f"    Hinweis: {z['hinweise']}")
        text = "\n".join(zeilen)
        self.status = text
        return Message(text=text)
