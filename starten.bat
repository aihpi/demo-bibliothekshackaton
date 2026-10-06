@echo off
rem Startet Langflow fuer den Bibliothekshackathon (Windows: Doppelklick)
cd /d "%~dp0"
chcp 65001 >nul

docker info >nul 2>&1
if errorlevel 1 (
  echo Docker laeuft nicht. Bitte zuerst Docker Desktop oeffnen und warten, bis es bereit ist.
  pause
  exit /b 1
)

if not exist .env (
  copy .env.example .env >nul
  echo Die Datei .env wurde angelegt. Bitte die Zugangsdaten der Orga eintragen und dann erneut starten.
  notepad .env
  exit /b 0
)

echo Langflow wird gestartet (beim ersten Mal dauert der Download einige Minuten) ...
docker compose up -d
if errorlevel 1 (
  echo Fehler beim Start.
  pause
  exit /b 1
)

:warten
curl -fs http://localhost:7860/health_check >nul 2>&1
if errorlevel 1 (
  timeout /t 3 /nobreak >nul
  goto warten
)
echo Langflow laeuft: http://localhost:7860
start "" http://localhost:7860
