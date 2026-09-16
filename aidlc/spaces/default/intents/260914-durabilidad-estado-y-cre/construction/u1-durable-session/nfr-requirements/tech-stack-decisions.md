# Tech Stack Decisions — u1-durable-session

> NFR Requirements (Construction). La unidad NO introduce stack nuevo (C1, coste 0€).

## Sources

- codekb/technology-stack.md (FastAPI, Python 3.12, Neon, db_connection sin ORM) [scope]
- requirements.md (C1 mantener stack; C2 Neon vía db_connection; NFR3 coste 0€) [scope]
- team.md (pytest + fakes de persistencia; ruff) [scope]
- nfr-requirements-questions.md (Q5-A) [Q5]

## Decisiones

| Área | Decisión | Justificación |
|------|----------|---------------|
| Lenguaje/framework | **Reutilizar** FastAPI + Python 3.12 | C1 (sin cambio de stack); es el backend existente |
| Persistencia | **Reutilizar** `db_connection` (Neon PostgreSQL), tras una capa estrecha `stores/` | C2/C3; sin ORM nuevo, sin ampliar SQL-en-router |
| Tests | **Reutilizar** pytest + `pytest-cov` + fakes de la capa de persistencia | team.md (patrón de aislamiento afirmado) |
| Protección de credencial | **Diferida a NFR Design (FR5.2)**: cifrado en reposo vs. re-auth. Si cifra, usará una librería estándar del entorno (p. ej. `cryptography`/stdlib) SIN dependencia de pago. | FR5.2, NFR3 (coste 0€) |
| Servicios/infra nuevos | **Ninguno** | NFR3; no se añaden servicios Fly.io ni caché externo |

## Decisiones abiertas (a resolver en NFR Design)

- **FR5.2 — mecanismo de protección de la credencial**: cifrado en reposo con clave gestionada
  como secret de Fly.io, o no persistir la contraseña (re-auth). Ambos a coste 0€. Es la única
  decisión tecnológica pendiente de la unidad y pertenece a NFR Design, no aquí.
