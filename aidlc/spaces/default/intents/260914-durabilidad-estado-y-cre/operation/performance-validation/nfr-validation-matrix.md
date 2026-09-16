# NFR Validation Matrix — Durabilidad del estado

> Etapa Performance Validation (Operation). Matriz target-vs-actual de los NFR, consistente con la
> Target Verification Matrix de build-and-test. El foco de esta etapa es el rendimiento (NFR2); el
> resto se incluye para trazabilidad de estado.

## Matriz

| NFR | Target | Actual | Método | Owner / etapa | Verdict |
|-----|--------|--------|--------|---------------|---------|
| NFR2 — Rendimiento | Sin degradación perceptible (SIN umbral numérico) | No medido bajo carga; análisis cualitativo = impacto bajo/acotado | Cualitativo (diseño + suite < 1s); carga formal no ejecutada | performance-validation (diferido) | **Unverified (diferido)** |
| NFR5 — Multi-instancia | No asumir instancia única; tolerar reinicio/escalado | BD autoridad; lock por usuario (u1); marca interrumpida al arranque (u2). Ventana SELECT→INSERT en `/trigger` no atómica (R-01, estrecha con min=max=1) | Diseño + tests; carga concurrente no ejecutada | build-and-test / seguimiento R-01 | Met (con R-01 como mejora de seguimiento) |
| NFR1 — Seguridad | Password nunca en claro en reposo; guard JWT | Cifrado Fernet; repr redactado; guard activo | Tests (test_durable_session_*, test_jwt_startup) | build-and-test | Met |
| NFR3 — Coste | Coste 0 € | Sin servicios de pago nuevos | Revisión de deps/infra | build-and-test | Met |
| NFR4 — No regresión | Suite en verde | 125 passed, 0 regresiones | `pytest` | build-and-test | Met |

## Nota sobre NFR2 (diferido)

NFR2 permanece **Unverified**: no hay umbral numérico contra el que medir ni entorno de carga a coste
0 €. No es un fallo — es un diferimiento consciente. Para cerrarlo:

1. Fijar un umbral medible en `nfr-requirements` (p. ej. p95 del camino de sesión).
2. Ejecutar el `load-test-plan.md` (k6/locust contra staging efímero) — coste 0 € si se usa una máquina
   Fly one-shot / entorno temporal.

Owner: dueño del proyecto, en una intervención futura si el rendimiento pasa a ser una preocupación
observada en producción (vía `fly logs` / dashboard de Fly.io).

## Escalabilidad / capacidad

- Topología actual `min=max=1`; sin objetivo de concurrencia/throughput numérico. Si se observa
  saturación (memoria 256 MB, CPU) en el dashboard de Fly.io, la vía a coste 0 € es `fly scale memory`
  dentro del free allowance antes de considerar escalado horizontal (que reactivaría la relevancia de
  R-01).
