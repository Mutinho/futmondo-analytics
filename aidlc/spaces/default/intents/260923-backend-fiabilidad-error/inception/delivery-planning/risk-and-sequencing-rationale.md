# Risk & Sequencing Rationale — Fiabilidad backend (FR3.2 + FR4)

## Heurística de secuenciación

**Dependencia-primero con riesgo-primero dentro de la unidad** (no WSJF: con 2
unidades en cadena lineal, un modelo formal de puntuación sería overhead sin
valor, Q2=A).

- El DAG (2.7) fija la topología: U2 depende de U1. El orden económico (2.9)
  coincide con la topología aquí, porque construir la base de errores (U1) antes
  que las integraciones que se apoyan en ella (U2) es también lo de menor riesgo
  de retrabajo. **Sin desviación del orden topológico.**
- Dentro de U2 se prioriza lo de **mayor riesgo**: el cambio de contrato de
  Futmondo (blast radius alto) empieza por el inventario de llamadores +
  caracterización antes de migrar, y los puntos de corrupción de datos van
  primero (riesgo-primero, alineado con Boehm/Spiral).

## Riesgos y mitigación (Q6=C)

| Riesgo | Mitigación en la secuencia |
|---|---|
| Cambio de contrato de Futmondo (blast radius) | U2 empieza por inventario verificable + characterization-first antes de migrar; migra núcleo, resto deuda |
| Regresión al endurecer capturas (U1) | Bolt 1 va characterization-first, con la suite y el gate CI en verde en cada paso |
| Corrupción de datos en el punto `team_prizes` | Se ataca temprano dentro de U2, con spec que fuerza el fallo y asvera estado todo-o-nada (reemplazo transaccional atómico) |

## Assumptions & Open Questions

None.
