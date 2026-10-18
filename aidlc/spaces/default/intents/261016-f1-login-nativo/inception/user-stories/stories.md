# User Stories — F1: Login nativo end-to-end

> Fase: inception (user-stories). Formato Given/When/Then. Idioma: castellano; tokens técnicos
> verbatim en inglés. IDs estables; cada historia traza a FR (ver `traceability.json`).

## US-1 — Iniciar sesión (P1) — [FR-1, FR-2]

Como **usuario de Futmondo en iPhone**, quiero iniciar sesión con mi email y password para acceder
a la app. **Valor**: entrar a mi información.

- **Given** la pantalla de login y credenciales Futmondo válidas, **When** las introduzco y pulso
  "Iniciar sesión", **Then** la app llama a `POST /auth/login`, recibe el access token, lo guarda
  **en memoria** y me da por autenticado.
- **Given** credenciales inválidas, **When** envío el login, **Then** la app muestra un mensaje de
  error accionable y permanezco en la pantalla de login.

## US-2 — Guardar la sesión de forma segura (P1) — [FR-3, NFR-1]

Como **usuario**, quiero que mi sesión se guarde de forma segura para no re-loguear a cada rato.
**Valor**: comodidad sin sacrificar seguridad.

- **Given** un login correcto, **When** se completa, **Then** el refresh token se guarda en **iOS
  Keychain** y nunca en `UserDefaults`/plist en claro.

## US-3 — Reanudar sesión al abrir la app (P1) — [FR-5]

Como **usuario**, quiero que la app recuerde mi sesión al abrirla. **Valor**: no re-loguear.

- **Given** un refresh token válido en Keychain, **When** abro la app, **Then** se intenta
  `POST /auth/refresh` y, si va bien, entro sin re-login.
- **Given** un refresh token inválido/revocado (401), **When** abro la app, **Then** se borra el
  Keychain y voy a login.
- **Given** un fallo de red o 5xx en el refresh, **When** abro la app, **Then** el Keychain **se
  preserva** y no quedo colgado en el spinner (se reintenta después).

## US-4 — Refrescar la sesión de forma transparente (P1) — [FR-5, FR-7]

Como **usuario**, quiero que la sesión se renueve sola cuando caduca. **Valor**: continuidad.

- **Given** un access token caducado, **When** la app hace una llamada protegida y recibe 401,
  **Then** refresca el token y **reintenta la petición exactamente una vez**; si el refresh falla
  por 401/revocación, fuerza re-login.
- **Given** que el refresh fue OK pero el **reintento vuelve a 401**, **When** ocurre, **Then** la
  app **no entra en bucle**: propaga el error tipado y fuerza re-login (un solo reintento).

## US-5 — Cerrar sesión (P1) — [FR-6]

Como **usuario**, quiero cerrar sesión de forma fiable. **Valor**: control y seguridad.

- **Given** una sesión activa y red disponible, **When** pulso logout, **Then** la app llama a
  `POST /auth/logout`, el refresh token queda **revocado en backend**, y se borran los tokens de
  memoria y Keychain.
- **Given** red caída, **When** pulso logout, **Then** el estado local se limpia igualmente y la
  **revocación pendiente** se marca de forma **observable** (p. ej. flag/log local) para no
  asumir silenciosamente que el backend revocó.

## US-6 — Experiencia de login nativa (P1) — [FR-8, NFR-2]

Como **usuario**, quiero una pantalla de login nativa y fluida. **Valor**: calidad percibida.

- **Given** la pantalla de login, **When** interactúo, **Then** hay animaciones nativas,
  autorrelleno de contraseña de iOS, feedback háptico y materiales, **con solo SDK de Apple**
  (NFR-2); **and** con **Reduce Motion** activo las animaciones se degradan a transiciones
  instantáneas.

## US-7 — Reutilizar el backend sin romper la PWA (P2) — [FR-4, FR-9, NFR-3]

Como **mantenedor**, quiero que el cliente nativo use el backend sin romper la PWA. **Valor**: una
sola fuente de verdad de auth, sin regresión.

- **Given** el ajuste aditivo de D-01, **When** se despliega, **Then** `/auth/login` devuelve el
  refresh token **también en el body** y `/auth/refresh`/`/auth/logout` lo **aceptan por
  body/header**, **and** el canal cookie `HttpOnly` de la PWA sigue funcionando (tests `pytest`
  verdes en ambos canales).

## US-8 — Llamar a un endpoint protegido con Bearer (P1) — [FR-7]

Como **usuario autenticado**, quiero que la app acceda a mis datos. **Valor**: utilidad real del
login.

- **Given** un access token válido, **When** la app llama a `GET /api/v1/user/me`, **Then** adjunta
  `Authorization: Bearer <access>` y recibe 200; **and** sin token válido recibe 401 mapeado a un
  error tipado.

## Sources

- [consumes] requirements.md (FR/NFR), business-overview.md, component-inventory.md,
  team-practices.md.

## Assumptions & Open Questions

None.
