"""Literatursuche in OpenAlex: verlagsübergreifend, frei und ohne Anmeldung.

OpenAlex verzeichnet über 250 Millionen wissenschaftliche Publikationen aller Verlage,
mit Abstracts, Zitationszahlen und Links zu frei verfügbaren Volltexten (Open Access).
"""

import asyncio
import os

import httpx
from lfx.custom.custom_component.component import Component
from lfx.io import BoolInput, DropdownInput, IntInput, MessageTextInput, Output
from lfx.schema.dataframe import DataFrame
from lfx.schema.message import Message

OPENALEX = "https://api.openalex.org"
FELDER = ("id,doi,title,publication_year,type,cited_by_count,open_access,primary_location,"
          "best_oa_location,authorships,primary_topic,language,abstract_inverted_index")
SORTIERUNG = {"Relevanz": None, "Meistzitiert": "cited_by_count:desc", "Neueste zuerst": "publication_date:desc"}


def abstract_aus_index(index: dict | None) -> str:
    """OpenAlex speichert Abstracts als 'invertierten Index' (Wort -> Positionen)."""
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


async def openalex_abfragen(client: httpx.AsyncClient, pfad: str, params: dict) -> httpx.Response:
    """Fragt OpenAlex ab und wartet bei Überlastung (HTTP 429) kurz, bevor es erneut versucht."""
    schluessel = os.getenv("OPENALEX_API_KEY", "")
    if schluessel:
        params["api_key"] = schluessel
    elif os.getenv("KONTAKT_EMAIL"):
        params["mailto"] = os.getenv("KONTAKT_EMAIL")
    for versuch in range(3):
        antwort = await client.get(f"{OPENALEX}{pfad}", params=params)
        if antwort.status_code not in {429, 503} or versuch == 2:
            return antwort
        try:
            warten = float(antwort.json().get("retryAfter", 5))
        except ValueError:
            warten = 5
        await asyncio.sleep(min(warten, 40))
    return antwort


class OpenAlexSucheComponent(Component):
    display_name = "Literatursuche (OpenAlex)"
    description = "Sucht wissenschaftliche Publikationen verlagsübergreifend in OpenAlex – mit Abstracts und Open-Access-Links."
    icon = "search"
    name = "OpenAlexSuche"

    inputs = [
        MessageTextInput(
            name="suchanfrage",
            display_name="Suchanfrage",
            info="Suchbegriffe, am besten auf Englisch, z. B. 'large language models academic libraries'.",
            tool_mode=True,
            required=True,
        ),
        IntInput(name="anzahl", display_name="Anzahl Treffer", value=10, info="Höchstens 50."),
        IntInput(name="jahr_von", display_name="Erscheinungsjahr ab", value=0, info="0 = keine Einschränkung."),
        IntInput(name="jahr_bis", display_name="Erscheinungsjahr bis", value=0, info="0 = keine Einschränkung."),
        BoolInput(name="nur_open_access", display_name="Nur Open Access", value=False,
                  info="Nur Publikationen mit frei verfügbarem Volltext."),
        BoolInput(name="nur_mit_abstract", display_name="Nur mit Abstract", value=True, advanced=True),
        DropdownInput(name="sortierung", display_name="Sortierung", options=list(SORTIERUNG), value="Relevanz"),
    ]

    outputs = [
        Output(display_name="Treffer (Tabelle)", name="tabelle", method="tabelle_erstellen", tool_mode=False, group_outputs=True),
        Output(display_name="Trefferliste (Text)", name="liste", method="literatur_suchen", group_outputs=True),
    ]

    _zwischenspeicher: tuple | None = None
    _hinweis = ""

    async def _suchen(self) -> list[dict]:
        suche = (self.suchanfrage or "").strip().strip('"')
        schluessel = (suche, self.anzahl, self.jahr_von, self.jahr_bis, self.nur_open_access,
                      self.nur_mit_abstract, self.sortierung)
        if self._zwischenspeicher and self._zwischenspeicher[0] == schluessel:
            return self._zwischenspeicher[1]

        filter_teile = []
        if self.jahr_von:
            filter_teile.append(f"from_publication_date:{self.jahr_von}-01-01")
        if self.jahr_bis:
            filter_teile.append(f"to_publication_date:{self.jahr_bis}-12-31")
        if self.nur_open_access:
            filter_teile.append("is_oa:true")
        if self.nur_mit_abstract:
            filter_teile.append("has_abstract:true")
        params = {"search": suche, "per_page": max(1, min(int(self.anzahl or 10), 50)), "select": FELDER}
        if filter_teile:
            params["filter"] = ",".join(filter_teile)
        if SORTIERUNG.get(self.sortierung):
            params["sort"] = SORTIERUNG[self.sortierung]

        async with httpx.AsyncClient(timeout=30) as client:
            antwort = await openalex_abfragen(client, "/works", params)
            if antwort.status_code in {429, 503} and not os.getenv("OPENALEX_API_KEY"):
                # Ohne Schlüssel sperrt OpenAlex die Suche bei hoher Last. Ersatz: über Crossref suchen
                # und die Treffer per DOI in OpenAlex nachschlagen (das ist auch ohne Schlüssel erlaubt).
                werke = await self._ersatzsuche(client, suche)
                self._hinweis = ("Hinweis: OpenAlex-Suche ohne API-Schlüssel gerade gesperrt, Ersatzsuche über "
                                 "Crossref (weniger genau). Abhilfe: OPENALEX_API_KEY in der Datei .env eintragen.")
            elif antwort.status_code != 200:
                msg = f"OpenAlex antwortet mit Fehler {antwort.status_code}: {antwort.text[:300]}"
                raise ValueError(msg)
            else:
                werke = antwort.json().get("results", [])
                self._hinweis = ""
        zeilen = [werk_als_zeile(w) for w in werke]
        for nr, zeile in enumerate(zeilen, start=1):
            zeile["nr"] = nr
        self._zwischenspeicher = (schluessel, zeilen)
        return zeilen

    async def _ersatzsuche(self, client: httpx.AsyncClient, suche: str) -> list[dict]:
        anzahl = max(1, min(int(self.anzahl or 10), 50))
        filter_teile = ["type:journal-article"]
        if self.jahr_von:
            filter_teile.append(f"from-pub-date:{self.jahr_von}")
        if self.jahr_bis:
            filter_teile.append(f"until-pub-date:{self.jahr_bis}")
        if self.nur_mit_abstract:
            filter_teile.append("has-abstract:true")
        sortierung = {"Meistzitiert": "is-referenced-by-count", "Neueste zuerst": "published"}.get(self.sortierung)
        params = {"query": suche, "rows": min(anzahl * 3, 100), "select": "DOI", "filter": ",".join(filter_teile)}
        if sortierung:
            params |= {"sort": sortierung, "order": "desc"}
        antwort = await client.get("https://api.crossref.org/works", params=params)
        antwort.raise_for_status()
        dois = [t["DOI"].lower() for t in antwort.json()["message"]["items"]]
        if not dois:
            return []
        antwort = await openalex_abfragen(client, "/works", {
            "filter": "doi:" + "|".join(dois[:50]), "per_page": 50, "select": FELDER})
        antwort.raise_for_status()
        nach_doi = {(w.get("doi") or "").replace("https://doi.org/", "").lower(): w for w in antwort.json()["results"]}
        werke = [nach_doi[d] for d in dois if d in nach_doi]
        if self.nur_open_access:
            werke = [w for w in werke if (w.get("open_access") or {}).get("is_oa")]
        return werke[:anzahl]

    async def tabelle_erstellen(self) -> DataFrame:
        zeilen = await self._suchen()
        self.status = f"{len(zeilen)} Treffer für „{self.suchanfrage}“. {self._hinweis}".strip()
        return DataFrame(zeilen)

    async def literatur_suchen(self) -> Message:
        zeilen = await self._suchen()
        if not zeilen:
            return Message(text=f"Keine Treffer für „{self.suchanfrage}“.")
        teile = []
        for z in zeilen:
            oa = "Open Access" if z["open_access"] else "kein freier Volltext"
            teile.append(
                f"[{z['nr']}] {z['autoren']} ({z['jahr']}): {z['titel']}. {z['zeitschrift']}. "
                f"Zitiert: {z['zitiert']}. {oa}. DOI: {z['doi'] or '–'}\n"
                f"Abstract: {z['abstract'][:1200] or '–'}"
            )
        text = "\n\n".join(teile)
        if self._hinweis:
            text = f"({self._hinweis})\n\n{text}"
        self.status = text
        return Message(text=text)
