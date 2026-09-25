# Scalability Requirements — u2-integrations (Integraciones)

U2 **no cambia la escalabilidad ni la topología** del sistema. Es una
intervención de fiabilidad acotada sobre la ruta de integración existente; la
carga, el crecimiento de datos y la estrategia de escalado se heredan sin
modificación. Se documenta así en lugar de inventar objetivos de escala.

Consume: `functional-spec.md`, `requirements.md`, `technology-stack.md`.

## Requisitos de escalabilidad (derivados)

| ID | Requisito | Fuente | Verificación |
|----|-----------|--------|--------------|
| NFR-scale.1 | El endurecimiento de errores **no altera** el modelo de carga ni la concurrencia del sync; el volumen de datos y el número de campeonatos/usuarios no cambian por este intent. | NFR4, alcance del intent | Revisión: sin cambios de topología ni de límites |

## Sin cambio (heredado)

- **Topología Fly.io**: dos apps `min=max=1`, `shared-cpu-1x`/256 MB — **sin cambio**. No hay auto-scaling; la escala es fija por diseño (coste 0 €).
- **Neon PostgreSQL** (tier free): límites del tier free — **sin cambio**; U2 no aumenta el volumen ni la frecuencia de escritura (sólo endurece el manejo de fallo).
- **Crons de sync** (04:30 / 05:00 UTC, máquinas one-shot): cadencia **sin cambio**.
- **Sin proyección de crecimiento nueva**: no aplica a esta intervención de fiabilidad; no se inventan multiplicadores de capacidad.

## Assumptions & Open Questions

None.
