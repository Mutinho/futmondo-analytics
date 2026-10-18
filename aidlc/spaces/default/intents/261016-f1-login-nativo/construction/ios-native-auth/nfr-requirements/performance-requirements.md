# NFR — Performance Requirements (`ios-native-auth`)

> Bolt 3 de F1. Idioma: castellano; identificadores/código en inglés.

## PERF-A1 — Arranque fluido
El `bootstrap` (auto-login) corre en `async` sin bloquear el hilo principal; el Splash muestra
progreso y no se cuelga (cae a Login si el refresh tarda/ falla). El acceso al Keychain es local y
rápido.

## PERF-A2 — Sin tormentas de refresh
El refresh coalescido (AR4) evita múltiples refresh concurrentes ante un pico de 401.

## Sources
- [consumes] functional-spec.md, rules.md (AR3, AR4).

## Assumptions & Open Questions
None.
