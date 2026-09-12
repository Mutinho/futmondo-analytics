# Instrucciones de Test de Seguridad — Reemplazo transaccional de la caché de Sofascore

> Intent: `260911-sofascore-cache-atomica` · Scope: `bugfix` · Estrategia: Minimal.
> Perspectiva: ingeniería de seguridad (soporte DevSecOps).

## Superficie y riesgos relevantes

- **Dependencia externa no oficial (Sofascore vía `curl_cffi`)** con riesgo real
  de baneo de IP. El bugfix añade detección de baneo (HTTP 403 →
  `SofascoreIPBanError`) que aborta el repoblado y preserva la caché, evitando
  un modo de fallo por disponibilidad de datos. No hay entrada de usuario nueva
  ni cambio de autenticación (el endpoint sigue tras Bearer token).
- **Integridad de datos (NFR1):** el reemplazo transaccional evita un estado
  intermedio vacío/parcial visible por lecturas concurrentes.
- **Sin secretos nuevos ni credenciales hardcodeadas:** el cambio no introduce
  claves ni variables sensibles (verificado: no se añaden secretos en los 4
  ficheros tocados).

## Verificaciones recomendadas

1. **Regresión de detección de baneo** (ya cubierta en la suite unit): 403 del
   cliente → excepción propagada → `applied=False`, `reason="ip_ban"`, caché
   intacta. Cubre el fallo de disponibilidad ante baneo.
2. **Sin fuga de datos en la respuesta:** confirmar que la respuesta del
   endpoint (`applied`/`reason`/`synced`/`errors`/`total_players`) no expone
   detalles internos sensibles (nombres de jugador ya son públicos; no hay PII
   de usuario). Verificación manual/lectura de código.
3. **Escaneo de dependencias (opcional, coste 0€):** el bugfix no añade
   dependencias; si se ejecuta el escaneo de CI existente, no debe reportar
   nuevos hallazgos atribuibles a este cambio.

No se requiere SAST/DAST dedicado para este bugfix; la superficie de cambio es
mínima y sin nueva exposición de autenticación/autorización.
