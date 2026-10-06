"""Erzeugt die fiktive Beispiel-Masterarbeit daten/beispiel_masterarbeit.pdf.

    uv run --with reportlab scripts/beispieldaten_erzeugen.py

Die Arbeit ist erfunden, das Literaturverzeichnis besteht aber aus echten Publikationen
(plus einem Buch und einem Dokument ohne Crossref-DOI), damit die Flows etwas finden.
"""

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

ZIEL = Path(__file__).resolve().parent.parent / "daten" / "beispiel_masterarbeit.pdf"

TITEL = "Offene Metadaten und KI-gestützte Recherche in wissenschaftlichen Bibliotheken"

KAPITEL = [
    ("1 Einleitung", [
        "Wissenschaftliche Bibliotheken stehen vor einem doppelten Wandel: Offene Metadaten und "
        "Open-Access-Publikationen verändern, wie Literatur gefunden und bereitgestellt wird, und "
        "generative KI verändert, wie Studierende recherchieren und zitieren (Cox et al., 2019; "
        "Lund & Wang, 2023). Diese Arbeit untersucht, welche Chancen und Risiken sich daraus für "
        "Auskunft und Informationskompetenz ergeben.",
        "Ausgangspunkt ist die Beobachtung, dass Sprachmodelle plausibel klingende, aber erfundene "
        "Literaturangaben erzeugen (Walters & Wilder, 2023). Gleichzeitig sind mit offenen "
        "Datenquellen wie Crossref und OpenAlex die Werkzeuge vorhanden, um solche Angaben "
        "automatisch zu prüfen (Hendricks et al., 2020; Visser et al., 2021).",
    ]),
    ("2 Offene Metadaten und Open Access", [
        "Der Anteil frei zugänglicher Artikel wächst seit Jahren (Laakso et al., 2011; Piwowar et al., "
        "2018). Die FAIR-Prinzipien fordern auffindbare, zugängliche, interoperable und nachnutzbare "
        "Daten (Wilkinson et al., 2016). Zugleich konzentriert sich das Publikationswesen auf wenige "
        "große Verlage (Larivière et al., 2015), was die Verhandlungsposition von Bibliotheken schwächt.",
        "Für die Bibliometrie ist entscheidend, welche Datenquelle genutzt wird: Abdeckung und "
        "Qualität unterscheiden sich zwischen Scopus, Web of Science, Dimensions, Crossref und "
        "Google Scholar deutlich (Harzing, 2019; Martín-Martín et al., 2021). Das Wachstum der "
        "wissenschaftlichen Literatur verschärft das Problem der Informationsflut (Bornmann & Mutz, 2015).",
    ]),
    ("3 Generative KI in Auskunft und Lehre", [
        "Große Sprachmodelle können Recherchen unterstützen, Texte zusammenfassen und Suchanfragen "
        "formulieren (Kasneci et al., 2023). Sie ersetzen aber keine Prüfung der Quellen: Erfundene "
        "oder fehlerhafte Zitate sind häufig (Walters & Wilder, 2023). Für systematische "
        "Übersichtsarbeiten bleiben transparente Verfahren wie PRISMA maßgeblich (Page et al., 2021).",
        "Die Leitlinien zur Sicherung guter wissenschaftlicher Praxis (Deutsche Forschungsgemeinschaft, "
        "2019) verlangen, dass verwendete Quellen korrekt nachgewiesen werden – unabhängig davon, "
        "ob KI-Werkzeuge beteiligt waren. Einen praktischen Einstieg in das wissenschaftliche Arbeiten "
        "bietet weiterhin Eco (2010).",
    ]),
    ("4 Fazit", [
        "Offene Metadaten machen die automatische Prüfung und Anreicherung von Literaturangaben "
        "möglich. Bibliotheken können diese Infrastruktur nutzen, um KI-gestützte Recherche "
        "verantwortungsvoll zu begleiten. Offen bleibt, wie sich solche Werkzeuge in bestehende "
        "Beratungsangebote integrieren lassen (Tennant et al., 2016; Cox et al., 2019).",
    ]),
]

LITERATUR = [
    "Bornmann, L., & Mutz, R. (2015). Growth rates of modern science: A bibliometric analysis based on the "
    "number of publications and cited references. Journal of the Association for Information Science and "
    "Technology, 66(11), 2215–2222. https://doi.org/10.1002/asi.23329",
    "Cox, A. M., Pinfield, S., & Rutter, S. (2019). The intelligent library: Thought leaders' views on the "
    "likely impact of artificial intelligence on academic libraries. Library Hi Tech, 37(3), 418–435.",
    "Deutsche Forschungsgemeinschaft. (2019). Leitlinien zur Sicherung guter wissenschaftlicher Praxis: "
    "Kodex. Bonn: DFG. https://doi.org/10.5281/zenodo.3923602",
    "Eco, U. (2010). Wie man eine wissenschaftliche Abschlußarbeit schreibt (13. Aufl.). Wien: Facultas.",
    "Harzing, A.-W. (2019). Two new kids on the block: How do Crossref and Dimensions compare with Google "
    "Scholar, Microsoft Academic, Scopus and the Web of Science? Scientometrics, 120(1), 341–349.",
    "Hendricks, G., Tkaczyk, D., Lin, J., & Feeney, P. (2020). Crossref: The sustainable source of "
    "community-owned scholarly metadata. Quantitative Science Studies, 1(1), 414–427.",
    "Kasneci, E., Sessler, K., Küchemann, S., et al. (2023). ChatGPT for good? On opportunities and "
    "challenges of large language models for education. Learning and Individual Differences, 103, 102274.",
    "Laakso, M., Welling, P., Bukvova, H., Nyman, L., Björk, B.-C., & Hedlund, T. (2011). The development "
    "of open access journal publishing from 1993 to 2009. PLoS ONE, 6(6), e20961.",
    "Larivière, V., Haustein, S., & Mongeon, P. (2015). The oligopoly of academic publishers in the "
    "digital era. PLoS ONE, 10(6), e0127502. https://doi.org/10.1371/journal.pone.0127502",
    "Lund, B. D., & Wang, T. (2023). Chatting about ChatGPT: How may AI and GPT impact academia and "
    "libraries? Library Hi Tech News, 40(3), 26–29.",
    "Martín-Martín, A., Thelwall, M., Orduna-Malea, E., & Delgado López-Cózar, E. (2021). Google Scholar, "
    "Microsoft Academic, Scopus, Dimensions, Web of Science, and OpenCitations' COCI: A multidisciplinary "
    "comparison of coverage via citations. Scientometrics, 126(1), 871–906.",
    "Page, M. J., McKenzie, J. E., Bossuyt, P. M., et al. (2021). The PRISMA 2020 statement: An updated "
    "guideline for reporting systematic reviews. BMJ, 372, n71. https://doi.org/10.1136/bmj.n71",
    "Piwowar, H., Priem, J., Larivière, V., et al. (2018). The state of OA: A large-scale analysis of the "
    "prevalence and impact of Open Access articles. PeerJ, 6, e4375. https://doi.org/10.7717/peerj.4375",
    "Tennant, J. P., Waldner, F., Jacques, D. C., Masuzzo, P., Collister, L. B., & Hartgerink, C. H. J. "
    "(2016). The academic, economic and societal impacts of Open Access: An evidence-based review. "
    "F1000Research, 5, 632.",
    "Visser, M., van Eck, N. J., & Waltman, L. (2021). Large-scale comparison of bibliographic data "
    "sources: Scopus, Web of Science, Dimensions, Crossref, and Microsoft Academic. Quantitative Science "
    "Studies, 2(1), 20–41.",
    "Walters, W. H., & Wilder, E. I. (2023). Fabrication and errors in the bibliographic citations "
    "generated by ChatGPT. Scientific Reports, 13, 14045. https://doi.org/10.1038/s41598-023-41032-5",
    "Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., et al. (2016). The FAIR Guiding Principles for "
    "scientific data management and stewardship. Scientific Data, 3, 160018.",
]


def main() -> None:
    stile = getSampleStyleSheet()
    text = ParagraphStyle("text", parent=stile["BodyText"], fontSize=11, leading=16, spaceAfter=8)
    quelle = ParagraphStyle("quelle", parent=text, leftIndent=1 * cm, firstLineIndent=-1 * cm, spaceAfter=6)
    klein = ParagraphStyle("klein", parent=text, fontSize=9, textColor="#666666")

    inhalt = [
        Spacer(1, 3 * cm),
        Paragraph(TITEL, stile["Title"]),
        Paragraph("Masterarbeit im Studiengang Bibliotheks- und Informationswissenschaft", stile["Heading3"]),
        Spacer(1, 1 * cm),
        Paragraph("vorgelegt von: Alex Beispiel", text),
        Paragraph("Fiktives Beispiel für den Bibliothekshackathon – kein echtes Dokument.", klein),
        PageBreak(),
        Paragraph("Inhaltsverzeichnis", stile["Heading1"]),
        *[Paragraph(titel, text) for titel, _ in KAPITEL],
        Paragraph("Literaturverzeichnis", text),
        Paragraph("Eidesstattliche Erklärung", text),
        PageBreak(),
    ]
    for titel, absaetze in KAPITEL:
        inhalt.append(Paragraph(titel, stile["Heading1"]))
        inhalt.extend(Paragraph(a, text) for a in absaetze)
    inhalt += [PageBreak(), Paragraph("Literaturverzeichnis", stile["Heading1"])]
    inhalt.extend(Paragraph(angabe, quelle) for angabe in LITERATUR)
    inhalt += [
        PageBreak(),
        Paragraph("Eidesstattliche Erklärung", stile["Heading1"]),
        Paragraph("Ich versichere, dass ich die vorliegende Arbeit selbstständig verfasst habe. "
                  "(Fiktiver Text für den Hackathon.)", text),
    ]

    SimpleDocTemplate(str(ZIEL), pagesize=A4, title=TITEL, author="Alex Beispiel (fiktiv)",
                      leftMargin=2.5 * cm, rightMargin=2.5 * cm).build(inhalt)
    print(f"geschrieben: {ZIEL}")


if __name__ == "__main__":
    main()
