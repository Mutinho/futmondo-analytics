# Constraint Register — Durabilidad del estado y credenciales Futmondo

## Restricciones técnicas

| ID | Restricción | Origen | Source |
|----|-------------|--------|--------|
| C-T1 | Mantener el stack actual (Angular + FastAPI + Neon PostgreSQL + Fly.io); sin reescrituras grandes | Intent | [desc] [Q4] |
| C-T2 | La persistencia debe apoyarse en Neon PostgreSQL (ya en el stack); no añadir dependencias nuevas con gasto | Decisión Q1 | [Q1] |
| C-T3 | Preservar el comportamiento de sesión Futmondo (TTL 12h) y la concurrencia con locks por usuario ya existentes | Código actual | [Q5] [desc] |

## Restricciones organizativas / de coste

| ID | Restricción | Origen | Source |
|----|-------------|--------|--------|
| C-O1 | Coste 0 €: solo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free); descartar cualquier gasto recurrente | Regla de proyecto | [memory:M1] [Q4] |
| C-O2 | Sin restricción de plazo formal más allá de las conocidas | Q4 | [Q4] |

## Restricciones regulatorias

| ID | Restricción | Origen | Source |
|----|-------------|--------|--------|
| C-R1 | No hay normativa formal aplicable; rige la buena práctica de no almacenar secretos en claro | Q2 | [Q2] |

## Assumptions & Open Questions

None.
