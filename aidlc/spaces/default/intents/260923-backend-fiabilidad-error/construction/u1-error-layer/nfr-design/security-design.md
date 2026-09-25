# Security Design — U1 `u1-error-layer`

## Diseño: no-filtración de credenciales por construcción (SR1 / NFR3)

**Estrategia: defensa en profundidad — la credencial nunca entra en la
excepción.** La forma más robusta de garantizar que una excepción no expone un
secreto no es redactarlo después, sino no dársele nunca.

- **Contrato del constructor**: los tipos de `integration_errors` se construyen
  con parámetros explícitos y no sensibles: `failure_mode` (enum) y, opcional,
  `status` (int) y `endpoint` (str no sensible). El constructor NO recibe el
  objeto de request, ni el password, ni el token.
- **Mensaje**: se compone SOLO a partir de esos campos no sensibles, en inglés.
- **`__repr__`/`args`**: derivan de los mismos campos; no hay ruta por la que una
  credencial llegue a `str(exc)`, `repr(exc)` o `exc.args`.
- **Consecuencia**: la filtración es imposible por construcción, no por
  vigilancia (no depende de un paso de saneo que podría fallar ante un formato
  de token nuevo).

Pseudocódigo ilustrativo (≤15 líneas, no implementación):

```text
class IntegrationError(Exception):
    def __init__(self, failure_mode, *, status=None, endpoint=None):
        # sólo campos no sensibles; NUNCA credenciales
        self.failure_mode = failure_mode
        self.status = status
        self.endpoint = endpoint
        super().__init__(f"integration {failure_mode} (status={status}, endpoint={endpoint})")
```

## Verificación (defensa)

Un spec construye cada subtipo pasando, en el *contexto de la llamada*, un
password/token de prueba conocidos, y asvera que esa cadena NO aparece en
`str(exc)`, `repr(exc)` ni `exc.args`. (El diseño hace que ni siquiera se le
pueda pasar; el spec es la red de seguridad.)

## NFR aplicables por kind

U1 es `kind: library`: sin diseño de performance/escalabilidad/fiabilidad/
observabilidad a nivel de servicio (esos son de U2). El único diseño NFR es esta
garantía de seguridad.

## Assumptions & Open Questions

None.
