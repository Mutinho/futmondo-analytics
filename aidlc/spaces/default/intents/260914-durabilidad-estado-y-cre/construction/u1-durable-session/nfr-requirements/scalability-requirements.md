# Scalability Requirements — u1-durable-session

> NFR Requirements (Construction). Derivados de NFR5 (no asumir instancia única) y la
> restricción de coste 0€.

## Sources

- requirements.md (NFR5, NFR3) [scope]
- team.md (Fly.io min=max=1; Neon free) [scope]
- nfr-requirements-questions.md (Q3-A, Q5-A) [Q3] [Q5]

## Requisitos de escalabilidad

| ID | Requisito | Target | Fuente |
|----|-----------|--------|--------|
| NFR5.2 (esc.) | El diseño de persistencia **tolera más de una instancia** aunque `fly.toml` fije min=max=1 hoy: la autoridad de estado y de concurrencia (unicidad, locks) reside en la BD, no en memoria de proceso. | Ningún estado autoritativo en memoria compartida entre instancias | NFR5 |

## Notas de capacidad

- **Sin proyecciones de crecimiento nuevas ni triggers de auto-scaling**: el intent es una
  intervención acotada; el volumen de sesiones es el actual (por usuario, TTL 12h) y Neon free
  lo absorbe sin acercarse a límites del tier (assumption de requirements.md).
- **Coste 0€ (NFR3)** acota cualquier estrategia de escalado: no se añaden réplicas, caché
  externo (Redis) ni servicios nuevos. El escalado horizontal futuro, si llegara, funcionaría sin
  rediseño porque la BD es la autoridad (NFR5.2).
- La tabla de sesión es de una fila por usuario (upsert), sin crecimiento no acotado; una purga
  perezosa al leer elimina las expiradas sin job dedicado.
