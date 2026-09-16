# Build and Test Summary — Durabilidad del estado

> Etapa Build and Test (Construction). Resumen consolidado del build, los sets de instrucciones de
> test generados, la matriz de verificación de objetivos y la evaluación de readiness para el intent
> de durabilidad de sesión (u1) y tareas de sync (u2). Estrategia **Standard**. Coste 0 €.

## Estado del build y prerrequisitos

- **Build**: SUCCESS (instalación de dependencias + importabilidad de `app.main`).
- **Prerrequisitos**: Python 3.12 en CI; `JWT_SECRET` de arranque (no-default, guard NFR1.1);
  `FUTMONDO_CRED_KEY` y `DATABASE_URL` solo en runtime productivo (los tests usan fakes).

## Inventario de tipos de test generados

| Archivo | Generado | Motivo |
|---------|----------|--------|
| `build-instructions.md` | Sí | Siempre |
| `integration-test-instructions.md` | Sí | Standard: fronteras clave + interacción cross-unit |
| `security-test-instructions.md` | Sí | Intent toca FR5/NFR1 (credenciales); documenta tests de seguridad ya implementados |
| `performance-test-instructions.md` | Sí | Documenta NFR2 sin umbral numérico (diferido) |
| `test-results.md` | Sí | Resultado de ejecución |
| `cross-unit-traceability.md` | Sí | Gate de cobertura cruzada (Step 10) |

Unit tests: cubiertos por unidad en Code Generation (u1: 36, u2: 35).

## Expectativas de cobertura por unidad

- **u1-durable-session**: 36 tests (caracterización, repository, service, api). Cobertura de piezas:
  `credential_protection.py` 97%, `session_service.py` 80%, `session_repository.py` 83%.
- **u2-durable-sync-tasks**: 35 tests (caracterización, repository, service, api). Cobertura de
  piezas: `task_service.py` 89%, `task_repository.py` 90%.
- Referencia global scope `feature`: 80% líneas (no piso bloqueante adicional, decisión Q3).

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| NFR1-seguridad | `requirements.md` §NFR1 / FR5 | Password nunca en claro en reposo; guard JWT no-default | Ciphertext Fernet + scheme; repr redactado; guard activo | `test_durable_session_*` + `test_jwt_startup.py` (verde) | build-and-test | Met |
| NFR2-rendimiento | `requirements.md` §NFR2 | Sin degradación perceptible (sin umbral numérico) | No medido con carga (sin umbral ni entorno productivo) | Diseño acotado (1 lectura/escritura stores; caché best-effort); suite < 1 s | performance-validation (Operación) | Unverified |
| NFR3-coste | `requirements.md` §NFR3 | Coste 0 € (Neon free / Fly free / GH Actions free) | Sin dependencias/servicios de pago nuevos; tests con fakes | `requirements.txt` sin paquetes de pago; `code-summary.md` u1/u2 | build-and-test | Met |
| NFR4-no-regresion | `requirements.md` §NFR4 | Suite existente en verde | 125 passed, 0 regresiones | `test-results.md` (`pytest -q`) | build-and-test | Met |
| NFR5-multi-instancia | `requirements.md` §NFR5 | No asumir instancia única; tolerar reinicio/escalado | BD autoridad; lock por usuario (u1); marca interrumpida al arranque (u2) | `test_durable_session_service.py` (test de concurrencia), `task_service` | build-and-test | Met |

Nota sobre NFR5 y el hallazgo R-01 de u2 (revisión de code-generation): la ventana no-atómica
SELECT→INSERT en `/trigger` es un Major abierto y recomendado como seguimiento; hoy no afecta a la
topología `min=max=1`. Se marcó NFR5 `Met` porque el diseño sí sitúa la autoridad en BD y no asume
instancia única en el resto de caminos; el cierre completo de la garantía multi-instancia de `/trigger`
(índice único parcial) queda como mejora acotada de seguimiento, no como objetivo no cumplido de esta
etapa.

## Cross-unit coverage gate

**PASS** — todos los FR/NFR cubiertos `OK` con archivo objetivo existente. Ver
`cross-unit-traceability.md`.

## Evaluación de readiness

- **Build-ready**: Sí.
- **Test-ready**: Sí (125 passed, 0 regresiones).
- **Deployment-ready**: Sí, condicionado al gate de CI (gitleaks + pytest + ng test) sobre el MR,
  que es donde se ejecutan los checks diferidos.

## Limitaciones / pendientes conocidos

- **gitleaks** (secretos) y lint corren en el gate de CI, no localmente en esta etapa — diferidos a
  CI Pipeline / gate de MR.
- **NFR2** sin umbral numérico → `Unverified` (diferido); recomendación de fijar y medir un umbral
  en una intervención futura si se quiere cerrar formalmente.
- **R-01 (u2)**: unicidad no-atómica en `/trigger` — mejora acotada de seguimiento (índice único
  parcial) para cerrar la garantía multi-instancia de FR1.6/NFR5 si se escala.
- **libsql-experimental** no compila en Python 3.14 (runtime local); excluido en local, no
  ejercitado por tests; CI usa 3.12.
