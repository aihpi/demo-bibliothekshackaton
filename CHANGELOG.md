# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.0] - 2026-09-24

### Added

- Langflow 1.12.3 in Docker Compose, optional mit lokalem Ollama (`--profile lokal`)
- Bibliotheks-Bausteine: KI-Modell (LiteLLM/Ollama), Literaturangaben prüfen (Crossref, DataCite,
  Retraction Watch), Literaturverzeichnis finden, Quellen anreichern (OpenAlex), Literatursuche (OpenAlex),
  Volltexte holen (Open Access), Katalogsuche (hbz / lobid)
- Beispiel-Flows: Hallo KI, Referenz-Checker, Masterarbeit-Quellenanalyse, Literaturreview, Recherche-Agent
- Testdaten: Literaturliste mit eingebauten Fehlern, fiktive Masterarbeit (PDF)
- Anleitungen für Teilnehmende, Challenges und Leitfaden für die Orga
- Startskripte für Windows und macOS
- `scripts/flows_bauen.py` zum reproduzierbaren Bauen und Testen der Flows
