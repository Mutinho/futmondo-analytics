# Performance Design — Intent 4 (gate CI/CD hardening)

> Etapa de diseño: patrones y decisiones, no implementación. La implementación
> concreta (ediciones de `ci.yml`/`fly-deploy.yml`/`pytest.ini`, pins) es de
> code-generation / ci-pipeline.

## Alcance

Este intent es **config-only de CI/CD** y no toca el runtime de la aplicación.
Por tanto el rendimiento de la app (latencia de endpoints, throughput,
utilización de CPU/memoria del servicio) **no aplica** y no cambia respecto a la
línea base en producción. La única dimensión de rendimiento relevante es la del
**propio gate de CI**, gobernada por la restricción dura de coste 0 € (free tier
de GitHub Actions).

## Objetivos de diseño

| ID | Objetivo | Diseño |
|----|----------|--------|
| NFR1.1 | Coste del gate dentro del free tier | Ver estrategia de minutos abajo; cuantificación en FR16 (ci-pipeline). |
| NFR1.2 | Sin regresión relevante de duración del pipeline | Ver presupuesto de tiempo abajo. |

## Presupuesto de tiempo del gate (performance budget)

El endurecimiento añade trabajo a dos jobs (`quality` en `ci.yml` y `verify` en
`fly-deploy.yml`). El diseño acota el coste marginal por clase de trabajo:

| Paso añadido/modificado | Clase de trabajo | Coste marginal esperado | Presupuesto |
|-------------------------|------------------|-------------------------|-------------|
| `pip-audit` (entorno instalado) | Consulta a la BD de advisories sobre el venv resuelto | segundos | ≤ ~30 s |
| `npm audit --audit-level=high` | Built-in de npm sobre el árbol ya instalado | segundos | ≤ ~15 s |
| `ruff check` (promoción a bloqueante) | Ya se ejecuta hoy en advisory; la promoción es quitar `continue-on-error` | ~0 (sin coste nuevo) | sin cambio |
| Chequeo de caducidad de la allowlist | Script determinista que parsea fechas | < 1 s | ≤ ~2 s |
| `pytest --cov` en `verify` (paridad backend) | La cobertura ya se mide en `ci.yml`; en `verify` es coste nuevo | overhead de `--cov` sobre la suite existente | ≈ duración de la medición equivalente en `ci.yml` |

**Criterio pass-fail (NFR1.2)**: tras el cambio, la duración de `verify` debe
ser ≈ la de la clase de trabajo equivalente en `ci.yml` (misma medición de
cobertura + audits + lint). La cobertura es el único coste no trivial y ya está
caracterizado en `ci.yml`.

## Estrategias de eficiencia (coste 0 €)

- **Reutilizar el entorno ya instalado**: `pip-audit` corre sobre el venv
  resuelto tras `pip install` (sin `-r`) — no reinstala ni resuelve rangos, así
  que no añade un paso de resolución de dependencias. `npm audit` corre sobre el
  árbol que `npm ci` ya dejó instalado.
- **Cache de dependencias**: apoyarse en el cacheo de dependencias de Actions ya
  existente (pip/npm) para que los pasos de audit no paguen una instalación
  extra. No se introduce cache nueva.
- **Sin duplicar la suite**: la paridad de cobertura en `verify` reusa la misma
  invocación de `pytest` que `ci.yml` (misma suite, mismas fixtures fake
  in-memory), no una segunda pasada.
- **Sin herramientas de pago**: toda medición usa `pytest-cov`, `pip-audit`,
  `npm audit` y el built-in de Actions — OSS, dentro del free tier.

## Estrategia de minutos de GitHub Actions (NFR1.1)

- El coste marginal dominante es medir cobertura backend en **dos** jobs (PR +
  push). El diseño lo acepta como el precio de la paridad de señal (FR17.3):
  sin ella un push directo a `main` eludiría el piso.
- Los audits y el lint son de segundos; su contribución a los minutos mensuales
  es despreciable frente a la cobertura.
- El **umbral que forzaría salir del free tier** (nº de builds/mes × duración
  incremental) se cuantifica y documenta en FR16 (ci-pipeline). Aquí se fija la
  **política de diseño**: si el consumo se acercara al allowance, la palanca es
  reducir la frecuencia de medición de cobertura en el push-gate (nunca eliminar
  el piso ni bajarlo), manteniendo la señal en el PR-gate.

## Runtime de la app — N/A (justificado)

Latencia/throughput de endpoints, utilización de recursos del servicio y
benchmarks de la app: **N/A**. El intent no altera el código de la aplicación
ni su comportamiento en ejecución.

## Trazabilidad

- NFR1.1 → estrategia de minutos + presupuesto de tiempo (cuantificación en FR16).
- NFR1.2 → presupuesto de tiempo del gate.

## Sources

- `../nfr-requirements/performance-requirements.md` (NFR1.1, NFR1.2).
- `../nfr-requirements/tech-stack-decisions.md` (tooling del gate, pins).
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md` (coste 0 €, Actions free tier).

## Assumptions & Open Questions

- El valor concreto de minutos de Actions y el margen de free tier se cuantifican en FR16 (ci-pipeline); no bloquea esta etapa.
