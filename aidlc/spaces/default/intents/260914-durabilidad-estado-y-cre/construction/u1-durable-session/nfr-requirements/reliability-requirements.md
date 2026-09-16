# Reliability Requirements — u1-durable-session

> NFR Requirements (Construction), perspectiva calidad. Derivados de NFR5 (durabilidad y
> robustez multi-instancia) y de la fiabilidad de la sesión.

## Sources

- requirements.md (NFR5, NFR4) [scope]
- functional-design/functional-spec.md (máquina de estados; rehidratación) [scope]
- team.md (caracterización primero; fakes de persistencia) [scope]
- nfr-requirements-questions.md (Q3-A) [Q3]

## Requisitos de fiabilidad

| ID | Requisito | Target | Método de validación | Fuente |
|----|-----------|--------|----------------------|--------|
| NFR5.1 | La sesión persistida **sobrevive a un reinicio/redeploy** del proceso y es reconstruible. | 100% de sesiones válidas reconstruibles tras reinicio (si hay medio de re-auth) | Test caracterización (reinicio pierde sesión hoy) + test nuevo contrato (reconstruida) con fake de persistencia | NFR5, FR1.2 |
| NFR5.2 | El acceso a la sesión **no asume instancia única**; la BD es la autoridad de estado/concurrencia. | 0 dependencias de estado en memoria de proceso como autoridad | Revisión de diseño + test con almacén compartido simulado | NFR5 |
| NFR5.3 | Cuando la sesión no puede reconstruirse, el sistema **degrada de forma controlada** a 401 accionable (nunca 403 opaco ni cuelgue). | 401 accionable en 100% de los casos unrecoverable | Test del camino unrecoverable | FR1.3 |
| NFR4.1 | La suite de tests existente **permanece en verde** tras los cambios (no regresión). | Suite verde | `pytest` + `ng test` en el gate de CI | NFR4 |

## Notas

- **Sin SLA/SLO de disponibilidad numérico nuevo**: el servicio ya cuenta con healthcheck
  `/health` y smoke test on-merge; este intent no cambia esos objetivos. La fiabilidad que
  aporta es cualitativa (la sesión ya no se pierde con el reinicio), verificada por
  comportamiento, no por un porcentaje de uptime.
- **RPO/RTO**: no aplican como objetivos nuevos; la durabilidad de la sesión se apoya en Neon
  (ya en producción) sin backup/recovery adicional para este estado (TTL 12h lo acota).
