# Security Requirements — U1 `u1-error-layer`

## SR1 — Sin credenciales en excepciones de integración (NFR3)

- **Requisito**: ninguna instancia de `IntegrationError` ni de sus subtipos
  incluye el password ni el token Futmondo del usuario en su mensaje (`str(exc)`),
  su `repr(exc)`, sus `exc.args` ni el `exc_info`/traceback que se loguee. Solo
  lleva `failure_mode` + contexto no sensible (`status`, `endpoint`).
- **Criterio de aceptación (verificable)**: un spec construye cada subtipo con
  un password/token de prueba conocidos en el contexto de la llamada y asvera que
  esa cadena NO aparece en `str(exc)`, `repr(exc)` ni `exc.args`. El log
  estructurado (NFR1, en U2) tampoco los incluye.
- **Fuente**: NFR3 [memory:M1]. Extiende las reglas afirmadas de
  no-credenciales-en-claro.

## SR2 — Los tests no usan credenciales reales

- **Requisito**: los specs de U1 usan fakes/dobles y valores de prueba, nunca
  credenciales ni tokens reales. gitleaks (bloqueante en CI) escanea también los
  `*.py` de tests.
- **Criterio de aceptación**: gitleaks pasa; ningún literal de credencial real en
  los tests.
- **Fuente**: práctica afirmada (secretos), gate CI.

## Nota sobre NFR aplicables por kind

U1 es `kind: library`: no aplican requisitos de performance, escalabilidad,
fiabilidad ni observabilidad a nivel de servicio (esos son de U2, un `service`).
El único NFR con peso en U1 es la seguridad (SR1/SR2).

## Assumptions & Open Questions

None.
