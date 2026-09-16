# Delivery Planning — Preguntas de secuenciación

> Última etapa de Inception (delivery lead + arquitecto). Decidimos el orden de
> los **Bolts** (cada Bolt = una pasada de construcción sobre una o más unidades,
> que termina en algo que funciona). El DAG de Units Generation no tiene aristas
> (U1 y U2 independientes), así que la topología permite cualquier orden; el orden
> económico es una decisión humana. Responde en el tag `[Answer]:`.
> `X. Other (please specify)` siempre disponible.

## Sources

- units-generation/unit-of-work.md (U1 u1-durable-session, U2 u2-durable-sync-tasks; ambas M, kind service) [scope]
- units-generation/unit-of-work-dependency.md (DAG sin aristas; construibles en paralelo) [scope]
- requirements-analysis/requirements.md (FR1/FR5; el 403 opaco de sesión es el dolor más visible) [scope]
- contract-design/contract-summary.md (C1 CredentialProtection intra-U1) [scope]
- team.md/project.md (walking skeleton OFF; trunk-based squash-merge; on-merge a Fly.io; coste 0 €) [scope]

---

## Q1 — ¿Qué construir primero?

Con dos unidades independientes (U1 sesión, U2 tareas), ¿qué las ordena?

- A. **Riesgo/valor primero: U1 (sesión) antes que U2 (tareas)**. El 403 opaco tras
  reinicio y la contraseña en claro (U1: FR1.1/1.2/1.3, FR5) son el dolor más visible
  y el riesgo de seguridad; hacerlo durable primero valida el patrón de persistencia +
  la frontera de credenciales, que U2 luego reutiliza (mismo `db_connection`, mismo patrón).
- B. **U2 (tareas) primero**: las tareas de sync son más simples (sin credenciales) y
  validan el patrón de persistencia con menos riesgo antes de tocar la sesión.
- C. **En paralelo** (dos mobs/pasadas simultáneas), dado que son independientes.

[Answer]: A

---

## Q2 — ¿Modelo de puntuación formal?

¿Rankeamos con un modelo tipo WSJF (valor+urgencia÷tamaño) o basta un argumento cualitativo?

- A. **Argumento cualitativo (risk-first/value-first)**: solo dos unidades de tamaño similar
  (M/M); un modelo formal WSJF añade ceremonia sin señal. Se justifica el orden en prosa.
- B. **WSJF formal**: puntuar ambas unidades con pesos explícitos de valor/urgencia/riesgo÷tamaño.

[Answer]: A

---

## Q3 — Tamaño de Bolt

- A. **Un Bolt por unidad** (2 Bolts: Bolt 1 = U1, Bolt 2 = U2). Coherente con unidades
  independientes y grano grueso; cada Bolt entrega durabilidad de un dominio completo.
- B. **Un solo Bolt** con ambas unidades juntas.
- C. **Bolts que cruzan unidades** (thin slices).

[Answer]: A

---

## Q4 — ¿Bolts en paralelo o en serie?

- A. **En serie** (un Bolt tras otro): equipo pequeño / AI, un solo proceso `futmondo-api`;
  secuencial reduce riesgo de integración y coordinación, y permite reutilizar el patrón de
  persistencia validado en el primer Bolt.
- B. **En paralelo**: son independientes, así que técnicamente podrían construirse a la vez.

[Answer]: A

---

## Q5 — Dependencias externas / bloqueos

¿Algo fuera del equipo puede retrasar el build (APIs, datos, aprobaciones, hand-offs)?

- A. **Nada externo bloquea**: todo es código dentro de `futmondo-api`; Neon ya está
  aprovisionado; no hay hand-offs de otros equipos ni aprobaciones externas. El mapa de
  dependencias externas queda esencialmente vacío.
- B. **Sí, hay bloqueos** (indícalos en Other: quién los posee, duración, qué Bolt bloquean, plan si se retrasa).

[Answer]: A

---

## Q6 — ¿Qué es lo que más te preocupa del build (para atacarlo pronto)?

- A. **La frontera de credenciales / no reintroducir texto plano** (FR5.1): es el riesgo de
  seguridad; atacarlo temprano en U1 con caracterización primero y la interfaz `CredentialProtection`.
- B. **La coherencia caché↔BD y la latencia del camino de sesión** (NFR2): que la persistencia
  no degrade el camino caliente.
- C. **La caracterización antes de refactorizar** (C5): congelar el comportamiento de
  `SessionStore`/`TaskManager` sin romper la suite.
- D. Otra (indícala en Other).

[Answer]: A

---

## Consolidated Summary Confirmation

Plan de entrega que se materializará en los artefactos (`bolt-plan.md`,
`team-allocation.md`, `risk-and-sequencing-rationale.md`, `external-dependency-map.md`):

**Secuencia de Bolts (en serie, un Bolt por unidad):**

| Orden | Bolt | Unidad | Definición de Hecho (resumen) | Hipótesis de confianza |
|-------|------|--------|-------------------------------|------------------------|
| 1 | Bolt 1 — sesión durable | U1 (u1-durable-session) | Sesión Futmondo persistida y reconstruible tras reinicio; sin `password` en claro; caracterización previa; suite verde | Tras un redeploy, la primera petición autenticada NO devuelve 403; el `password` no aparece en claro en BD ni logs |
| 2 | Bolt 2 — tareas durables | U2 (u2-durable-sync-tasks) | Estado de tareas persistido y consultable tras reinicio; unicidad 409 contra BD; marcado interrumpida-por-reinicio; caracterización previa; suite verde | Tras un redeploy, una tarea en curso queda marcada como interrumpida (no huérfana); no se admite doble tarea activa |

- **Orden y heurística (Q1-A, Q2-A):** risk-first + value-first, argumento cualitativo (sin WSJF). U1 primero por ser el mayor valor (403) y riesgo (credenciales); U2 hereda el patrón de persistencia validado.
- **Tamaño (Q3-A):** un Bolt por unidad. **Ejecución (Q4-A):** en serie.
- **Walking skeleton:** OFF (decisión afirmada; sistema ya en producción).
- **Sin desviación del DAG:** el DAG no tiene aristas, así que cualquier orden es topológicamente válido; el orden 1→2 es una elección económica, no una restricción de dependencia.
- **Dependencias externas (Q5-A):** ninguna bloqueante; mapa esencialmente vacío (todo dentro de `futmondo-api`; Neon ya aprovisionado).
- **Mayor riesgo a atacar pronto (Q6-A):** la frontera de credenciales / no reintroducir texto plano (FR5.1), en Bolt 1 con caracterización primero y la interfaz `CredentialProtection`.
- **Staffing:** Team Formation (1.5) no se ejecutó; todos los Bolts los ejecuta `aidlc-developer-agent` (AI).
- **Way of Working:** trunk-based, base/target `main`, squash-merge (cada Bolt = un commit por slug); on-merge a Fly.io.

[Answer]: Looks correct
