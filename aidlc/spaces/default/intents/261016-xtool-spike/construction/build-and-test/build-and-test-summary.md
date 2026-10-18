# Build and Test Summary — Spike de la cadena `xtool` (B-01)

## Estado general y prerequisitos

Spike de toolchain, scope `bugfix`, test strategy `minimal`. No se generan ficheros de test
adicionales (Minimal: los unit tests van por-Unit en Code Generation, y aquí no hay código de
app testeable). La verificación del DONE es manual en dispositivo.

## Inventario de tipos de test

- Unit tests nuevos: **ninguno** (spike de toolchain; sin código de app).
- Integration/performance/security: **no aplican** (Minimal; sin NFRs de rendimiento/seguridad).
- Smoke manual en dispositivo: **sí** (criterio de aceptación del spike, documentado en el runbook).
- Suite existente del repo: debe permanecer **verde** (obligación del Testing Contract).

## Expectativas de cobertura

Sin piso de cobertura nuevo. El trinquete del repo (backend `--cov-fail-under`, frontend
`coverageThresholds`) no se toca ni se relaja.

## Target Verification Matrix

| Target ID | Source | Expected | Actual | Evidence | Owning Stage | Verdict |
|-----------|--------|----------|--------|----------|--------------|---------|
| T1-suite-green | Testing Contract (`scope_floor`: keep existing suite green) | Suite existente del repo sin regresiones | Sin cambios en `backend/` ni `angular-app/` | `git status --porcelain`: 0 cambios en código de app; cambios solo en `spikes/` y `docs/spikes/` | build-and-test | Met |
| T2-scripts-syntax | code-summary (scripts bash setup/smoke) | Scripts sin errores de sintaxis | `bash -n` OK en ambos | `bash -n setup-wsl.sh` y `smoke.sh` → OK | build-and-test | Met |
| T3-chain-live | intent-capture Q1 (app arranca en el iPhone 13 Pro vía xtool) | App construida+firmada+instalada arranca en dispositivo | **Arranca: "xtool OK version 1.0.0" en el iPhone 13 Pro** | `xtool dev run` exit=0 (Install/Verify 100%) + confirmación visual del usuario | build-and-test | Met |

## Readiness

- **Build-ready**: sí (build cacheado; `Build complete!`).
- **Test-ready**: sí (smoke manual PASÓ; suite existente intacta).
- **Deployment-ready**: N/A (el spike no despliega; su DONE era la instalación en dispositivo, lograda).

## Resultado

**GO confirmado end-to-end.** Toda la cadena `xtool` (build Swift 6.4.0 → firma
Apple ID gratuito → empaquetado → instalación → arranque) funciona desde WSL
Ubuntu 26.04 sobre el iPhone 13 Pro físico, a coste 0 €. Secuencia reproducible
y fricciones recurrentes (relay USB, caducidad ~7 días, IP de WSL) documentadas
en `docs/spikes/ios-xtool.md`.
