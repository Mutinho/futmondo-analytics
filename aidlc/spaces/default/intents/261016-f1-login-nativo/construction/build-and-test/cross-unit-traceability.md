# Cross-Unit Traceability — F1: Login nativo end-to-end

> Fase: construcción (build-and-test). Trazabilidad FR/NFR → unidades → verificación. Idioma:
> castellano; identificadores/código en inglés.

| Req | Unidad(es) | Verificación |
|-----|-----------|--------------|
| FR-1 Login | ios-native-auth (+ backend login) | swift test (AuthService.login) + pytest (login body) |
| FR-2 Access en memoria | ios-native-auth | swift test (sin persistencia; borrado en logout) |
| FR-3 Refresh en Keychain | ios-native-auth | swift test (KeychainStore doble) + manual (SecItem real) |
| FR-4 Transporte aditivo (D-01) | backend-refresh-transport | pytest (cookie/header/body, precedencia) |
| FR-5 Refresh automático | ios-native-auth + ios-network-client | swift test (bootstrap, refresh coalescido, reintento único) |
| FR-6 Logout | ios-native-auth (+ backend logout) | swift test (borrado doble + pending) + pytest (revocación) |
| FR-7 Cliente de red Bearer | ios-network-client | swift test (14 casos) |
| FR-8 Polish nativo UI | ios-native-auth (vistas) | validación manual en iPhone (xtool) |
| FR-9 Sin regresión PWA | backend-refresh-transport | pytest (canal cookie verde) |
| NFR-1 Seguridad credenciales | backend + ios-native-auth | pytest + swift test (nada en claro, Keychain) |
| NFR-2 Coste 0 / solo SDK | todos | sin dependencias externas (pytest/swift test) |
| NFR-3 Verificación | todos | pytest 422 + swift test 28 + validación manual iPhone |
| NFR-4 Idioma | transversal | código inglés / UI-commits castellano |

Sin FR/NFR sin verificación asignada (FR-8 y la parte de dispositivo de FR-3 vía validación manual
documentada).

## Sources
- traceability.json de cada bolt; test-results.md.

## Assumptions & Open Questions
None.
