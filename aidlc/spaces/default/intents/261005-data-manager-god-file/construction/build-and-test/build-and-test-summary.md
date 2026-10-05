# Build and Test Summary — `data_manager_v2` decomposition

Scope `refactor` · estrategia **Minimal** · zero-Unit (stage-level). Verificación
de equivalencia estricta de la descomposición DDD, a coste 0 € sobre los fakes
in-memory.

## Estado del build y prerrequisitos

- **Build-ready**: sí. Deps fijadas exactas instalables; runner `pytest 9.1.1`
  colecta OK. Sin paso de compilación (Python). Prerrequisito: ejecutar desde
  `backend/` con `JWT_SECRET` efímero no productivo (NFR1.1).
- **Test-ready**: sí. Suite completa verde (414 passed / 3 xfailed), fakes
  in-memory, sin red/BD/credenciales reales.
- **Deployment-ready**: sí para esta etapa (el gate de despliegue vive en fase
  Operation; sin cambio de topología).

## Inventario de tipos de test generados

| Tipo | Estado | Motivo |
|---|---|---|
| Unit / caracterización | Cubierto por Code Generation (14 módulos, 68 tests nuevos) | Minimal: unit por módulo en 3.5 |
| Integración | NO APLICA | Minimal/refactor; equivalencia cubierta por la suite completa (ver fichero) |
| Rendimiento | NO APLICA | Sin target de rendimiento en `requirements.md`; equivalencia no cambia perfil |
| Seguridad | Invariantes verificados; sin árbol nuevo | NFR6 + gitleaks (gate permanente); sin cambio de superficie |

## Expectativas de cobertura

- Piso bloqueante `--cov-fail-under=27` (line-only), **sostenido**; medido
  **57.48%**. El trinquete sólo sube.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|---|---|---|---|---|---|---|
| NFR1 | requirements.md §NFR1 (equivalencia; suite verde) | `backend/tests/` verde | 414 passed, 3 xfailed, 0 failed | test-results.md (`pytest tests/ --cov=app`) | build-and-test | Met |
| NFR2 | requirements.md §NFR2 (piso sólo-sube) | `--cov-fail-under` no se relaja | piso 27 sostenido; cobertura 57.48% (↑ desde 45.94%) | test-results.md; pytest.ini | build-and-test | Met |
| NFR3 | requirements.md §NFR3 (coste 0 €) | Sin deps de pago; nuevas OSS pinned | 0 deps nuevas; venv efímero OSS | code-summary.md; requirements.txt | build-and-test | Met |
| NFR4 | requirements.md §NFR4 (higiene diff brownfield) | Sin `ruff format` masivo; formateo sólo nuevos/quirúrgico | ruff en ficheros nuevos; per-file-ignores registra deuda legacy | code-summary.md; ruff.toml | build-and-test | Met |
| NFR5 | requirements.md §NFR5 (idioma) | Identificadores/docstrings EN; commits/UX ES | módulos nuevos en inglés | code-summary.md; árbol data_manager/ | build-and-test | Met |
| NFR6 | requirements.md §NFR6 (credenciales) | Sin credenciales/tokens en claro; tests sin reales | fakes in-memory; gitleaks bloqueante | security-test-instructions.md | build-and-test | Met |
| TC-CONTRACT | code-generation-plan.md §Testing Contract (test-after/characterization-first) | green-pre == green-post por módulo | 14/14 módulos equivalentes | code-summary.md tabla | build-and-test | Met |
| FR1.2 | requirements.md §FR1.2 (superficie byte a byte) | 57 métodos, firmas idénticas | 57 exactos, 0 añadidos/perdidos | code-summary.md Step 18 | build-and-test | Met |

Sin filas `Pending`. Sin targets diferidos ni `Unverified`.

## Evaluación de readiness

**READY.** Build, test y equivalencia verificados; piso de cobertura sostenido;
superficie pública preservada; consumidores intactos. Sin fallos ni targets no
cumplidos.

## Limitaciones conocidas / pendientes

- Rama de motor PostgreSQL (`_init_database`/`reset_database` DDL `SERIAL`/
  `CASCADE`) no parseable por el fake SQLite: caracterizada por sus rutas
  ejecutables en SQLite + cableado de `__init__`; equivalencia observable
  disponible sin fabricar un Postgres real (coherente con NFR6). Deuda conocida,
  no bloqueante.
- Deuda diferida fuera de alcance (ya registrada): error-handling legacy
  (OQ1) y el `delete_orphan_players` set-replacement (OQ2) se mueven verbatim.
