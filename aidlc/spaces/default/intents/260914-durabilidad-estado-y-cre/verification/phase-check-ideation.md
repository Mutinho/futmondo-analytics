# Phase Boundary Verification — Ideación → Inception

> Verificación de trazabilidad y consistencia al cierre de la fase de Ideación.

## Consistencia Intent → Scope → Intent Backlog

| Elemento intent | Cubierto en scope | Cubierto en backlog | Estado |
|-----------------|-------------------|---------------------|--------|
| FR1 — durabilidad de tareas de sync | Capacidad 1 (Must) | PU-2 | OK |
| FR1 — durabilidad de sesiones | Capacidad 2 (Must) | PU-3 | OK |
| FR1 — acción clara en vez de 403 | Capacidad 3 (Must) | PU-4 | OK |
| FR5 — contraseña no en claro | Capacidad 4 (Must) | PU-5 | OK |
| (base) persistencia en Neon | Secuenciación paso 1 | PU-1 | OK |

## Respaldo de feasibility para cada ítem de alcance

| Ítem de alcance | Respaldo en feasibility | Estado |
|-----------------|-------------------------|--------|
| Persistencia en Neon (PU-1..PU-4) | Neon ya en el stack; tablas nuevas, coste 0 € | OK |
| FR5 (PU-5) | Dos vías viables coste 0 € (re-auth / cifrado) | OK |

## Cobertura de trazabilidad

- Requisitos del intent (FR1, FR5): 2/2 con alcance y backlog asignados → 100%.
- Proto-Units huérfanas: ninguna (todas trazan a FR1 o FR5).
- Ítems de alcance sin respaldo de feasibility: ninguno.

## Consistencia entre fases

- Sin contradicciones entre intent, feasibility y scope.
- Restricciones (coste 0 €, sin reescrituras, stack actual) preservadas en todos los artefactos.

## Resultado

- **Verificación**: PASA.
- **Cuestiones abiertas trasladadas a Inception**: elección concreta de FR5 (re-auth vs. cifrado); supuesto de límites del tier free de Neon.

- [ ] Aprobación humana (se resuelve en el gate de la etapa)
