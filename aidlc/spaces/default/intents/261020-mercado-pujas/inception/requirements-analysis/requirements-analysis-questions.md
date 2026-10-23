# Requirements Analysis — Preguntas y Resumen (F3 Mercado)

> Modo **Guíame**. Requisitos derivados del alcance ya aprobado y de los
> contratos reales confirmados en Reverse Engineering. Confirmo una decisión.

---

## Q1 — Tope de importe de la puja

La UI usa como **máximo** el `available_for_bids` del usuario. El backend valida
además un tope absoluto (`price ≤ 5.000.000.000`) que, en la práctica, nunca lo
alcanza un usuario real.

- **A.** La UI valida con `available_for_bids` como máximo (mensaje claro si se
  supera); el tope absoluto del backend queda como última barrera del servidor,
  no se replica en la UI. ← **recomendada** (coincide con el Angular y evita
  duplicar lógica).
- **X.** Other (please specify)

[Answer]: A

---

## Consolidated Summary Confirmation

Resumen de Requirements Analysis para F3 = Mercado:

- **FR1** 2ª pestaña Mercado; **FR2** carga con estados cargando/error/vacío/
  datos; **FR3** banner (5 campos de user_info con formato moneda y color);
  **FR4** cards 1:1 (incl. favorito y tendencia con flecha+signo); **FR5** orden
  descendente por 7 campos (default value).
- **FR6 Pujar**: sheet con importe (default sugerida, mín precio de mercado, máx
  disponible), validación inline (incl. vacío/≤0), `POST /market/bid`, resultado
  aceptada/rechazada/error + recarga, botones deshabilitados durante la escritura.
- **FR7 Cancelar**: confirmación, `POST /market/cancelbid`, resultado + recarga.
- **FR8 Sofascore (Should)**: sheet con `GET /sofascore/player/{name}`, estados
  cargando/error/datos; su fallo no afecta a la lista ni a pujar.
- **NFR**: coste 0 €, tema DesignSystem, seguridad (Bearer/Keychain, sin exponer
  credenciales), idioma, testabilidad (lógica en FutmondoKit), accesibilidad.
- **Reviewer advisory** (product-lead) sobre `requirements`: pendiente (ahora).
- **Siguiente etapa**: User Stories.

¿Todo correcto?

- **Looks correct** — confirmo y avanzamos.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
