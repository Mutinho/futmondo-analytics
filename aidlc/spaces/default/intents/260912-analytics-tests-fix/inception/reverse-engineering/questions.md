# Reverse Engineering — Preguntas

## Decisión de escaneo (Code KB)

Existe una base de conocimiento del código para este repo, pero sus rutas
analizadas han cambiado desde que se construyó (intent de origen:
`analisis-mejoras`), por lo que está desactualizada. Un rescan completo la
reemplaza; un escaneo enfocado se fusiona sobre ella. ¿Cómo debe correr el
escaneo?

- A. Escaneo enfocado — analizar el área de este intent (`AnalyticsService` y sus tests en `backend/`) y extender el store; preservar la prosa previa fuera de esa área.
- B. Rescan completo — reconstruir el store cubriendo todo el repo (reemplaza los 9 artefactos).
- X. Other (please specify)

[Answer]: A
