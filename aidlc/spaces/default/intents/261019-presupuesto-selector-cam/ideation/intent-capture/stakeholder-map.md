# Stakeholder Map — F2: Presupuesto nativo + selector de campeonato

> Fase: ideación (intent-capture). Idioma: castellano; tokens técnicos verbatim en inglés.

## Stakeholders

| Stakeholder | Rol | Interés / necesidad |
|-------------|-----|---------------------|
| Propietario / único usuario | Single-maintainer y usuario final | Ver el Presupuesto en el iPhone con la misma información que en la web; cambiar de campeonato cómodamente sin sidebar; coste 0 €. Decide todas las opciones de diseño. |
| Backend Futmondo (`futmondo-api`) | Sistema existente | Proveedor de datos vía endpoints existentes (`/api/v1/analytics/balances`, `/api/v1/user/championships`); **no cambia** por F2. |
| Librería de diseño nativa (F1) | Dependencia interna | `FutmondoKit`/`FutmondoApp` DesignSystem — tokens de color/tipografía/espaciado y componentes que F2 consume y, si hace falta, amplía. |
| Apple (plataforma) | Plataforma de distribución | SDK gratuito; HIG como referencia de patrones nativos (navigation bar, menús, listas). |

## Notas

- No hay equipo ni on-call: un solo responsable. El feedback de diseño es iterativo, por uso propio en dispositivo.
- La dimensión de validación en dispositivo (iPhone 13 Pro) que quedó pendiente en F1 se arrastra como método de verificación de la UI de F2.

## Sources

- [memory:M1] `project.md`/`team.md`: single-maintainer, coste 0 €, stack Fly.io/Neon, librería de diseño nativa de F1.
- `angular-app/src/app/core/services/championship.service.ts`, `budget.service.ts` — endpoints consumidos.

## Assumptions & Open Questions

None.
