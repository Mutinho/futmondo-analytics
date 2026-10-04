# Reverse Engineering — Questions

## Q1. Alcance del escaneo del código (Code KB)

Ya existe una base de conocimiento del código para este repositorio, construida
por el intent `261001-sync-god-file-resto`, pero está **desactualizada** (STALE):
las rutas analizadas han cambiado desde que se construyó. En concreto:

- `backend/app/services/data_sync_service.py`
- `backend/app/services/sync/`
- `backend/app/services/prizes/`
- `backend/app/api/v1/endpoints/sync.py`

Un **re-escaneo completo** reemplaza las 9 artefactos cubriendo todo el repo.
Un **escaneo focalizado** escanea el área de este intent (la descomposición de
los dominios de sync que siguen inline en `data_sync_service.py`) y la fusiona
en el store existente, preservando la prosa previa fuera de esa área.

El área de este intent coincide exactamente con las rutas marcadas como stale,
por lo que un escaneo focalizado encaja de forma natural y es más barato.

- A. Full rescan — Rebuild the store covering the whole repo (replaces all 9 artifacts)
- B. Focused scan (Recommended) — Scan this intent's area and extend the store; preserve prior prose outside it, demoting unverifiable deep coverage to shallow
- X. Other (please specify)

[Answer]: B. Focused scan
