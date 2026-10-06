#!/usr/bin/env bash
# Startet Langflow für den Bibliothekshackathon (macOS: Doppelklick, Linux: ./starten.command)
cd "$(dirname "$0")" || exit 1

if ! docker info >/dev/null 2>&1; then
  echo "Docker läuft nicht. Bitte zuerst Docker Desktop öffnen und warten, bis es bereit ist."
  read -r -p "Enter drücken zum Schließen …"
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Die Datei .env wurde angelegt. Bitte die Zugangsdaten der Orga eintragen und dann erneut starten."
  open -e .env 2>/dev/null || xdg-open .env 2>/dev/null
  read -r -p "Enter drücken zum Schließen …"
  exit 0
fi

echo "Langflow wird gestartet (beim ersten Mal dauert der Download einige Minuten) …"
docker compose up -d || { read -r -p "Fehler beim Start. Enter drücken zum Schließen …"; exit 1; }

until curl -fs http://localhost:7860/health_check >/dev/null 2>&1; do
  printf "."
  sleep 3
done
echo
echo "Langflow läuft: http://localhost:7860"
open http://localhost:7860 2>/dev/null || xdg-open http://localhost:7860 2>/dev/null
