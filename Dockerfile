# Langflow with the library blocks and example flows built in, for the hosted instance (k8s/).
# The local setup does not use this image: docker-compose.yml mounts the same folders instead.
FROM langflowai/langflow:1.12.3

COPY --chown=1000:0 komponenten /app/komponenten
COPY --chown=1000:0 flows /app/flows
COPY --chown=1000:0 daten /app/daten
COPY --chown=1000:0 scripts/konten_anlegen.py /app/scripts/konten_anlegen.py

ENV LANGFLOW_COMPONENTS_PATH=/app/komponenten \
    LANGFLOW_LOAD_FLOWS_PATH=/app/flows \
    DO_NOT_TRACK=true
