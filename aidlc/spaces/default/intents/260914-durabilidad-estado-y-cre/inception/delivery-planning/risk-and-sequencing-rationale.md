# Risk & Sequencing Rationale — Durabilidad del estado y credenciales

> El porqué del orden de los Bolts. El DAG de Units Generation no tiene aristas, así
> que la topología permite cualquier orden; la secuencia 1→2 es una decisión económica.

## Sources

- units-generation/unit-of-work-dependency.md (DAG sin aristas) [scope]
- requirements-analysis/requirements.md (FR1/FR5, C5, NFR2) [scope]
- delivery-planning-questions.md (Q1-A risk/value-first, Q2-A cualitativo, Q6-A credenciales) [Q1] [Q2] [Q6]

## Heurística elegida

**Risk-first + value-first (argumento cualitativo).** No se usa un modelo formal WSJF
(Reinertsen/SAFe): con solo dos unidades de tamaño similar (M/M), un modelo de puntuación
daría precisión falsa; el orden se decide por juicio de valor/riesgo y se justifica aquí
(Q2-A). Referencia conceptual: secuenciar por reducción de riesgo temprano (Boehm, Spiral)
y por valor entregado (Cohn).

## Por qué U1 (sesión) antes que U2 (tareas)

- **Mayor valor:** el 403 opaco tras cada redeploy rompe la experiencia del usuario (fuerza
  re-login) y es el dolor más visible del intent. Resolverlo primero entrega el mayor valor
  percibido antes.
- **Mayor riesgo:** U1 concentra el riesgo de seguridad (contraseña en claro, FR5.1, regla
  dura de `project.md`) y la mayor incertidumbre de diseño (frontera `CredentialProtection`,
  mecanismo FR5.2 diferido). Atacarlo temprano (Q6-A) calibra esas decisiones antes de
  invertir en U2.
- **Reutilización del patrón:** U1 valida el patrón de persistencia sobre `db_connection`
  (capa estrecha `stores/`) y el caché best-effort delante del servicio. U2 hereda ese patrón
  ya probado, reduciendo su riesgo.

## Desviación del orden topológico

- **Ninguna.** El DAG (`unit-of-work-dependency.md`) no tiene aristas: U1 y U2 son
  independientes, por lo que 1→2, 2→1 y en paralelo son todas topológicamente válidas. El
  orden 1→2 es puramente económico (risk/value-first), no viola ninguna dependencia.

## Ejecución en serie (no paralelo)

Aunque las unidades son independientes (podrían ir en paralelo), se ejecutan en serie (Q4-A):
un solo proceso `futmondo-api`, ejecución por AI, y el beneficio de que U2 reutilice el patrón
de persistencia validado en U1 supera al de la concurrencia con dos unidades pequeñas.

## Registro de riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Reintroducir la contraseña en claro al hacer durable la sesión (FR5.1) | Media | Alto | Frontera `CredentialProtection` aislada (C1); caracterización previa; el contrato prohíbe devolver/loggear el plaintext; atacado en Bolt 1. |
| Degradar la latencia del camino de sesión con la persistencia (NFR2) | Media | Medio | Caché best-effort delante del servicio; BD autoridad solo en escritura/miss; medición en build. |
| Romper la suite existente al refactorizar `SessionStore`/`TaskManager` (NFR4/C5) | Media | Medio | Caracterización primero (congelar comportamiento, incluido el de fallo) antes de refactorizar. |
| Reconstrucción de sesión no posible según el mecanismo FR5.2 elegido | Baja | Medio | FR1.2 es condicional; si no hay medio de re-auth, prevalece FR1.3 (401 accionable). Decisión fina en Functional/NFR design. |
