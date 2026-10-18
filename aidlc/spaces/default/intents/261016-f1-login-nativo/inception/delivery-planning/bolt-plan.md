# Bolt Plan — F1: Login nativo end-to-end

> Fase: inception (delivery-planning). Secuencia de bolts para construcción. Idioma: castellano;
> tokens técnicos verbatim en inglés. Walking skeleton **OFF** (team.md: sistema ya en producción;
> no hay esqueleto que arrancar).

## Secuencia de bolts (1:1 con las unidades, camino lineal)

| Bolt | Unidad | kind | Depende de | Contenido |
|------|--------|------|------------|-----------|
| Bolt 1 | `backend-refresh-transport` | service | — | Ajuste aditivo de `/auth/login\|refresh\|logout` (transporte del refresh token por cookie O header O body); tests `pytest` de ambos canales; characterization-first. |
| Bolt 2 | `ios-network-client` | library | Bolt 1 | Capa de red Swift (`URLSession`, JSON, `Bearer`, errores tipados); humo a `GET /api/v1/user/me`. |
| Bolt 3 | `ios-native-auth` | ui | Bolt 2 | `KeychainStore` + `AuthService` (login/refresh/bootstrap/logout, reintento único, revocación pendiente) + `AuthViewModel` + `LoginView`/`SplashView` con polish nativo. |

- **Merge**: squash-merge a `main` por bolt (política de equipo); Conventional Commits con scope
  (`feat(ios-auth)`, `feat(ios-net)`, scope backend para Bolt 1).
- **Skeleton**: OFF — Bolt 1 corre como un bolt normal.

## Nota de tamaño (del reviewer de arquitectura)

**Bolt 3 (`ios-native-auth`) es el de mayor alcance** (6 FR, 6 US, C2–C5). Se mantiene como un
bolt por su cohesión alta; si durante la construcción el bolt resulta demasiado grande, se puede
**sub-batchear** en: (3a) `KeychainStore` + `AuthService` (lógica de sesión), (3b)
`AuthViewModel` + `LoginView`/`SplashView` (UI). Decisión en construcción, no obligatoria aquí.

## Autonomía de construcción

Al ser ejecutor único y camino lineal, se propone **continuar autónomamente** entre bolts tras la
aprobación del plan, con gate en cada bolt que toque superficie sensible (el ajuste de backend,
Bolt 1). (La elección definitiva de Construction Autonomy Mode se confirma al entrar en
construcción.)

## Sources

- [consumes] requirements.md, stories.md, mockups.md, components.md, unit-of-work.md,
  unit-of-work-dependency.md, unit-of-work-story-map.md, contract-summary.md, team-practices.md.

## Assumptions & Open Questions

None.
