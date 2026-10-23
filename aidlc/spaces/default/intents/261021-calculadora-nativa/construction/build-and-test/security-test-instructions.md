# Security Test Instructions — Calculadora nativa iOS

## Aplicabilidad

**NO APLICA en este intent.** Estrategia **minimal**; la pantalla no maneja
credenciales ni introduce superficie de seguridad nueva.

## Contexto

Las llamadas reutilizan el `NetworkClient` autenticado existente (Bearer
inyectado por el transporte); las preferencias en `UserDefaults` no son
sensibles; los `NetworkError` tipados no filtran la URL/query ni tokens. El
gate de CI del repo (gitleaks + audits) sigue aplicando a nivel de proyecto,
pero este intent no añade checks de seguridad nuevos.
