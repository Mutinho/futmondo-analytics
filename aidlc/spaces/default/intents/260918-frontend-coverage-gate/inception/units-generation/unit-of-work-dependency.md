# Dependencias entre Unidades — Frontend Coverage Gate

Este artefacto describe la **topología** (qué puede depender de qué). No fija un orden de construcción ni una ruta crítica — eso es decisión económica de Delivery Planning (2.9).

## DAG de dependencias

Una sola unidad, sin dependencias entre unidades:

```
[U1: frontend-coverage-gate]   (depends_on: [])
```

<!-- Text fallback: un único nodo U1 (frontend-coverage-gate) sin aristas de dependencia. -->

## Bloque de aristas (machine-readable)

```yaml
units:
  - name: frontend-coverage-gate
    kind: packaging
    depends_on: []
```

## Puntos de integración entre unidades

No aplica: al haber una sola unidad, no hay contratos entre unidades. La unidad integra con artefactos **existentes** del repo (no unidades nuevas): `angular.json`, `ng test`/builder `@angular/build:unit-test`, `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml` (job `verify`), y `package.json`/`package-lock.json`.

## Oportunidades de desarrollo paralelo

Ninguna entre unidades (solo hay una). El orden interno FR10 → FR17.1 es una secuencia **dentro** de la unidad, no una relación de dependencia entre unidades; Delivery Planning decidirá la secuencia económica de esa entrega.

## Assumptions & Open Questions

- None.
