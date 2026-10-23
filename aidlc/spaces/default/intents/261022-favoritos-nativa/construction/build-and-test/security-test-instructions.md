# Security Test Instructions — Favoritos nativa iOS

## Aplicabilidad
**NO APLICA.** Estrategia **minimal**; la pantalla no maneja credenciales ni
añade superficie de seguridad nueva.

## Contexto
Reutiliza el `NetworkClient` autenticado existente (Bearer inyectado por el
transporte); `unfollow` va con query params sobre ese transporte; las
preferencias en `UserDefaults` no son sensibles; los `NetworkError` tipados no
filtran URL/tokens. El gate de CI del repo (gitleaks + audits) sigue aplicando a
nivel de proyecto.
