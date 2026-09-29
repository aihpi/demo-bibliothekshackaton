# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added

- Beispiel-Flow 01b: Referenz-Checker nur aus Standard-Bausteinen, zum Vergleich mit Flow 01

### Changed

- Literatur-APIs (Crossref, OpenAlex, Unpaywall, DataCite, lobid) in `LANGFLOW_SSRF_ALLOWED_HOSTS`, damit der
  Baustein *API Request* sie erreicht

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
