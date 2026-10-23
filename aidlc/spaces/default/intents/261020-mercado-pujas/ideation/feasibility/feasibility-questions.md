# Feasibility & Constraints — Preguntas y Resumen (F3 Mercado)

> Modo **Guíame**. No hay decisiones de viabilidad abiertas: F3 reproduce una
> pantalla existente sobre endpoints en producción, reutilizando la base de
> F1/F2. Sólo confirmo el enfoque y los riesgos registrados.

---

## Q1 — Enfoque de viabilidad

- **A.** Proceder con **Build** (SwiftUI + SDK de Apple) reutilizando
  `FutmondoKit`/`DesignSystem`, con las restricciones C1–C9 y los riesgos R1–R4
  registrados (en especial el rigor anti-hueco-WSL y la escritura con efecto
  real). ← **recomendada**.
- **X.** Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de Feasibility & Constraints para F3 = Mercado:

- **Veredicto**: **viable** con alta confianza. Pantalla existente + endpoints en
  producción + base F1/F2 reutilizable. Trabajo nuevo: modelo/servicio de Mercado
  en `FutmondoKit` (lectura + escritura) y UI en `FutmondoApp` (banner, cards,
  orden, puja/cancelar, sheet Sofascore) + 2ª pestaña.
- **Restricciones clave**: coste 0 € (C1), tema Angular como fuente (C2), sin
  cambios de backend (C3), credenciales en Keychain (C4), idioma (C5), hueco WSL
  → validación en dispositivo con `xtool` (C6), sin `actool` (C7), iOS 26 (C8),
  sólo cards + orden descendente (C9).
- **Riesgos**: arm-only en WSL (R1), escritura con efecto económico real (R2),
  fallo/latencia de Sofascore (R3), deriva visual (R4) — con mitigaciones.
- **Dependencias**: base F1/F2, backend `/market/*`, validación en dispositivo.
- **Siguiente etapa**: Scope Definition.

¿Todo correcto?

- **Looks correct** — confirmo y avanzamos.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
