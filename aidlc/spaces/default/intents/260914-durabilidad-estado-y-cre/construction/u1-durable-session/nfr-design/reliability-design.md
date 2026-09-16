# Reliability Design — u1-durable-session

> Etapa NFR Design (Construction). Traduce NFR5.1, NFR5.2, NFR5.3 y NFR4.1 en patrones de resiliencia
> concretos. Es diseño, no implementación: los snippets son ilustrativos.

## Sources

- nfr-requirements/reliability-requirements.md (NFR5.1, NFR5.2, NFR5.3, NFR4.1) [scope]
- functional-design/functional-spec.md (máquina de estados; WF2/WF3 rehidratación; casos de error) [scope]
- inception/contract-design/contract-summary.md (C1: sin reintentos internos; BD autoridad ADR-005) [scope]
- nfr-design-questions.md (Q3-A lock BD, Q4-A distinguir fallo transitorio, Q5-A purga) [Q3] [Q4] [Q5]

## Durabilidad de la sesión (NFR5.1)

La sesión sobrevive a reinicio/redeploy porque su fuente de verdad es la fila `UserSession` en Neon,
no la memoria del proceso. Al reiniciar, la caché queda vacía y la primera lectura rehidrata desde BD:

```text
Reinicio del proceso:
  petición -> ensureSession(user_id):
    SessionStore MISS (caché vacía)
    SELECT UserSession de BD
      - active   -> poblar caché, continuar          [sesión sobrevive: NFR5.1]
      - expired  -> DELETE perezoso -> como absent
      - absent   -> rehidratar (re-auth interno)      [reconstrucción: FR1.2]
```

100% de las sesiones válidas con medio de re-auth disponible son reconstruibles tras reinicio.

## Patrón de rehidratación y política de reintentos

BR1.6 / C1: **sin reintentos internos**. Pero se distingue el tipo de fallo (Q4-A):

| Situación | Estado resultante | Respuesta |
|-----------|-------------------|-----------|
| Credencial inválida / `resolve` = `None` | `unrecoverable` | 401 accionable (FR1.3) — el usuario re-loguea |
| Fallo transitorio de Futmondo (timeout, 5xx de red) | error tipado hacia arriba | NO se marca `unrecoverable`; NO se destruye el handle; el usuario reintenta |
| Re-auth OK | `active` | sesión reconstruida (FR1.2) |

No hay bucle de reintento ni backoff dentro del componente (respeta BR1.6). La resiliencia ante un
blip transitorio viene de **no destruir el handle** y dejar que el cliente reintente su petición, no
de reintentar internamente. Esto evita convertir un hipo de red en un logout injustificado.

## Degradación controlada (NFR5.3)

Cuando la sesión no puede reconstruirse, el sistema degrada a **401 accionable** en el 100% de los
casos irrecuperables — nunca un 403 opaco (deuda actual que este intent elimina) ni un cuelgue. El
401 lleva la señal para que el frontend dispare el re-login.

## Concurrencia y consistencia (NFR5.2)

- **Lock por `user_id` en BD** (`SELECT ... FOR UPDATE`, Q3-A): serializa dos rehidrataciones
  simultáneas del mismo usuario. La segunda transacción espera y encuentra la sesión ya `active`
  (idempotencia BR1.2). Funciona entre instancias (autoridad = BD, NFR5.2).
- **Discrepancia caché↔BD:** gana la BD (BR1.5). La caché nunca fuerza un estado que la BD no tiene.

## Fallos de la capa de credencial

`CredentialProtection` lanza una **excepción tipada del dominio** (`CredentialProtectionError`) ante
fallo de almacén/resolución — nunca `except: pass` (BR1.4). `SessionService` la traduce a un error
accionable sin filtrar el secreto. Un fallo de almacén NO se confunde con "credencial inválida":
es un error tipado transitorio, coherente con Q4-A.

## Health checks, failover y backup

- **Health check:** el `/health` existente no cambia; esta unidad no añade dependencia dura nueva (la
  BD ya era dependencia). Si Neon no responde, el fallo es tipado y visible, no silencioso.
- **Failover / réplicas:** no se añaden (coste 0€, NFR3). La durabilidad se apoya en Neon (ya en
  producción).
- **Backup / RPO / RTO:** no se definen objetivos nuevos; el TTL de 12h acota la ventana de estado y
  la sesión es reconstruible mientras haya medio de re-auth.

## No regresión (NFR4.1)

La suite existente permanece en verde. El orden de trabajo (team.md): caracterización primero
(congelar el comportamiento actual, incluidos los bugs conocidos), luego implementar durabilidad con
tests del nuevo contrato usando **fakes de la capa de persistencia** (no Neon real). El gate de CI
(`pytest` + `ng test`) es bloqueante.

## Trazabilidad

| NFR | Solución de diseño |
|-----|--------------------|
| NFR5.1 | Fuente de verdad en BD; rehidratación desde BD al reiniciar; 100% reconstruible con medio de re-auth |
| NFR5.2 | Lock por usuario en BD (cross-instancia, Q3-A); sin estado autoritativo en memoria |
| NFR5.3 | Degradación a 401 accionable en 100% de irrecuperables; nunca 403 opaco ni cuelgue |
| NFR4.1 | Caracterización primero + fakes de persistencia; gate CI bloqueante mantiene la suite verde |
