"""Quellen anreichern: macht aus einem Literaturverzeichnis eine Tabelle mit Metadaten.

Jede Angabe wird über Crossref einer DOI zugeordnet und dann in OpenAlex nachgeschlagen:
Abstract, Thema, Fachgebiet, Zitationen, Open-Access-Status und Link zum Volltext.
Dazu kommt eine kleine Statistik über das ganze Verzeichnis.
"""

import asyncio
import os
import re
import unicodedata
from collections import Counter
from statistics import median

import httpx
from lfx.custom.custom_component.component import Component
from lfx.io import IntInput, MultilineInput, Output
from lfx.schema.dataframe import DataFrame
from lfx.schema.message import Message
from rapidfuzz import fuzz

CROSSREF = "https://api.crossref.org"
OPENALEX = "https://api.openalex.org"
FELDER = ("id,doi,title,publication_year,type,cited_by_count,open_access,primary_location,"
          "best_oa_location,authorships,primary_topic,language,abstract_inverted_index")
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


def abstract_aus_index(index: dict | None) -> str:
    if not index:
        return ""
    woerter = sorted((pos, wort) for wort, positionen in index.items() for pos in positionen)
    return " ".join(wort for _, wort in woerter)


def werk_als_zeile(werk: dict) -> dict:
    quelle = (werk.get("primary_location") or {}).get("source") or {}
    oa = werk.get("open_access") or {}
    bester = werk.get("best_oa_location") or {}
    thema = werk.get("primary_topic") or {}
    autoren = [a["author"]["display_name"] for a in werk.get("authorships", []) if a.get("author")]
    return {
        "titel": werk.get("title") or "",
        "autoren": ", ".join(autoren[:5]) + (" u. a." if len(autoren) > 5 else ""),
        "jahr": werk.get("publication_year") or "",
        "typ": werk.get("type") or "",
        "zeitschrift": quelle.get("display_name") or "",
        "verlag": quelle.get("host_organization_name") or "",
        "doi": (werk.get("doi") or "").replace("https://doi.org/", ""),
        "zitiert": werk.get("cited_by_count") or 0,
        "open_access": bool(oa.get("is_oa")),
        "oa_status": oa.get("oa_status") or "",
        "volltext_url": bester.get("pdf_url") or oa.get("oa_url") or "",
        "thema": thema.get("display_name") or "",
        "fachgebiet": (thema.get("field") or {}).get("display_name") or "",
        "sprache": werk.get("language") or "",
        "abstract": abstract_aus_index(werk.get("abstract_inverted_index")),
        "openalex_id": (werk.get("id") or "").replace("https://openalex.org/", ""),
    }


class QuellenAnreichernComponent(Component):
    display_name = "Quellen anreichern (OpenAlex)"
    description = "Ergänzt jede Literaturangabe um Abstract, Thema, Zitationen und Open-Access-Status – plus Statistik."
    icon = "library"
    name = "QuellenAnreichern"

    inputs = [
        MultilineInput(
            name="literaturangaben",
            display_name="Literaturangaben",
            info="Ein Literaturverzeichnis, z. B. aus dem Baustein 'Literaturverzeichnis finden'.",
            tool_mode=True,
            required=True,
        ),
        IntInput(name="max_angaben", display_name="Höchstens anreichern", value=60),
    ]

    outputs = [
        Output(display_name="Überblick (Text)", name="ueberblick", method="quellen_anreichern", group_outputs=True),
        Output(display_name="Quellen (Tabelle)", name="tabelle", method="tabelle_erstellen", tool_mode=False, group_outputs=True),
    ]

    _zwischenspeicher: tuple | None = None

    async def _get(self, client: httpx.AsyncClient, url: str, params: dict | None = None) -> httpx.Response:
        params = dict(params or {})
        if url.startswith(OPENALEX):
            if os.getenv("OPENALEX_API_KEY"):
                params["api_key"] = os.getenv("OPENALEX_API_KEY")
            elif os.getenv("KONTAKT_EMAIL"):
                params["mailto"] = os.getenv("KONTAKT_EMAIL")
        for versuch in range(4):
            antwort = await client.get(url, params=params)
            if antwort.status_code not in {429, 503} or versuch == 3:
                return antwort
            await asyncio.sleep(float(antwort.headers.get("retry-after", 0)) or 2 * (versuch + 1))
        return antwort

    async def _anreichern(self, client: httpx.AsyncClient, nr: int, angabe: str) -> dict:
        zeile = {"nr": nr, "angabe": angabe, "gefunden": False}
        try:
            doi = DOI_MUSTER.search(angabe)
            doi_text = doi.group(0).rstrip(".,;)") if doi else ""
            crossref_titel = ""
            if not doi_text:
                antwort = await self._get(client, f"{CROSSREF}/works", {
                    "query.bibliographic": angabe[:400], "rows": 10, "select": "DOI,title,subtitle,author,issued,type"})
                if antwort.status_code == 200:
                    treffer = antwort.json()["message"]["items"]
                    if treffer:
                        # den am besten passenden Treffer nehmen, nicht blind den ersten
                        bester = max(treffer, key=lambda t: _bewertung(t, angabe)[0])
                        crossref_titel = voller_titel(bester)
                        if passt(bester, *_bewertung(bester, angabe)[1:]):
                            doi_text = bester["DOI"]
            if doi_text:
                antwort = await self._get(client, f"{OPENALEX}/works/doi:{doi_text}", {"select": FELDER})
                if antwort.status_code == 200:
                    zeile.update(werk_als_zeile(antwort.json()))
                    zeile["gefunden"] = True
                else:
                    zeile.update({"doi": doi_text, "titel": crossref_titel})
        except httpx.HTTPError as fehler:
            zeile["fehler"] = str(fehler)
        return zeile

    async def _alle(self) -> list[dict]:
        schluessel = (self.literaturangaben, self.max_angaben)
        if self._zwischenspeicher and self._zwischenspeicher[0] == schluessel:
            return self._zwischenspeicher[1]
        angaben = literaturangaben_zerlegen(self.literaturangaben or "")[: self.max_angaben]
        kontakt = os.getenv("KONTAKT_EMAIL", "")
        # Crossref erlaubt ohne Kontakt-E-Mail nur eine Anfrage gleichzeitig, mit E-Mail drei
        begrenzung = asyncio.Semaphore(3 if kontakt else 1)
        kopf = {"User-Agent": "Bibliothekshackathon-Demo (Langflow)" + (f"; mailto:{kontakt}" if kontakt else "")}
        async with httpx.AsyncClient(timeout=30, headers=kopf) as client:

            async def begrenzt(nr: int, angabe: str) -> dict:
                async with begrenzung:
                    return await self._anreichern(client, nr, angabe)

            zeilen = await asyncio.gather(*(begrenzt(i + 1, a) for i, a in enumerate(angaben)))
        self._zwischenspeicher = (schluessel, zeilen)
        return zeilen

    async def tabelle_erstellen(self) -> DataFrame:
        zeilen = await self._alle()
        self.status = f"{sum(z['gefunden'] for z in zeilen)} von {len(zeilen)} Quellen gefunden"
        return DataFrame(zeilen)

    async def quellen_anreichern(self) -> Message:
        zeilen = await self._alle()
        gefunden = [z for z in zeilen if z["gefunden"]]
        if not gefunden:
            return Message(text=f"{len(zeilen)} Angaben erkannt, aber keine in OpenAlex gefunden.")

        jahre = [int(z["jahr"]) for z in gefunden if z.get("jahr")]
        oa = sum(1 for z in gefunden if z["open_access"])

        def haeufigste(feld: str, n: int = 5) -> str:
            zaehler = Counter(z[feld] for z in gefunden if z.get(feld))
            return "; ".join(f"{name} ({anzahl})" for name, anzahl in zaehler.most_common(n)) or "–"

        meistzitiert = sorted(gefunden, key=lambda z: z["zitiert"], reverse=True)[:5]
        teile = [
            "STATISTIK",
            f"- Angaben im Verzeichnis: {len(zeilen)}, davon in OpenAlex gefunden: {len(gefunden)}",
            f"- Erscheinungsjahre: {min(jahre)}–{max(jahre)}, Median {median(jahre):.0f}" if jahre else "- Jahre: –",
            f"- Open Access: {oa} von {len(gefunden)} ({100 * oa / len(gefunden):.0f} %)",
            f"- Publikationstypen: {haeufigste('typ')}",
            f"- Häufigste Zeitschriften: {haeufigste('zeitschrift')}",
            f"- Häufigste Verlage: {haeufigste('verlag')}",
            f"- Fachgebiete: {haeufigste('fachgebiet')}",
            f"- Themen: {haeufigste('thema', 8)}",
            "- Meistzitiert: " + "; ".join(f"{z['titel']} ({z['jahr']}, {z['zitiert']}×)" for z in meistzitiert),
            "",
            "NICHT GEFUNDEN (oft Bücher, Webseiten oder graue Literatur)",
            *[f"- [{z['nr']}] {z['angabe']}" for z in zeilen if not z["gefunden"]],
            "",
            "QUELLEN",
        ]
        for z in gefunden:
            teile.append(f"[{z['nr']}] {z['autoren']} ({z['jahr']}): {z['titel']}. {z['zeitschrift']}. "
                         f"Thema: {z['thema']}. Zitiert: {z['zitiert']}.\n    Abstract: {z['abstract'][:600] or '–'}")
        text = "\n".join(teile)
        self.status = text
        return Message(text=text)
