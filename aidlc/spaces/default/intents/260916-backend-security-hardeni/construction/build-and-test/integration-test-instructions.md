# Instrucciones de Test de Integración — Backend Security Hardening

## Aplicabilidad

**No se generan tests de integración nuevos en esta etapa.** La estrategia de
test es **Minimal** (scope `security-patch`) y las cinco correcciones se validan
al nivel más estrecho que reproduce cada caso: tests dirigidos por FR ejecutados
en la capa de endpoint/lógica con fakes (sin BD ni red reales). Ver
`security-test-instructions.md`.

Los tests de FR6, FR7 y FR18 ya ejercitan el boundary HTTP montando el router
en una `FastAPI` de prueba con `TestClient`, cubriendo la interacción
endpoint↔middleware↔guarda sin necesidad de un entorno integrado adicional.

## Frontera y no-regresión

La única comprobación de integración relevante es que la suite completa del
backend permanece en verde tras las correcciones (NFR4). Comando (desde
`backend/`):

```bash
python -m pytest -q
```

Resultado en esta etapa: **135 passed**, sin regresiones (baseline 125 + 10
casos netos nuevos/actualizados).
