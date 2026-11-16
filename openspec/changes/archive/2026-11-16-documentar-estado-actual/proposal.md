# Proposal

## Why

Mi Cotizador se construyó antes de adoptar OpenSpec, por lo que no existe ninguna especificación del comportamiento actual. Sin una línea base, los cambios futuros no pueden expresarse como modificaciones sobre requisitos conocidos. Este cambio documenta, sin alterar código, lo que la aplicación ya hace.

## What Changes

- Se documenta el conversor de pesos a dólares con registro de cada conversión en `historial.txt`.
- Se documenta el inicio de sesión y el registro de usuarios contra PocketBase.
- Se documenta el rol de usuario, el panel de administración y las reglas de acceso de PocketBase.
- No se modifica código ni configuración de la aplicación (es un cambio solo de documentación).

## Capabilities

### New Capabilities
- `conversion-pesos-dolares`: conversión de un monto en pesos a dólares según una cotización, con historial en archivo de texto.
- `autenticacion-usuarios`: registro e inicio de sesión de usuarios; el conversor solo se abre tras autenticarse.
- `administracion-usuarios`: rol de usuario, panel para listar cuentas, activarlas/desactivarlas y resetear contraseñas, y reglas que restringen esas acciones a administradores.

### Modified Capabilities

## Impact

- Código existente descrito: `mi_cotizador.py`, `pocketbase_client.py` y la migración `pocketbase/pb_migrations/1763340000_usuarios_rol_y_reglas.js`.
- Sistemas: una instancia de PocketBase (colección `users`) accesible por HTTP.
- No hay cambios de API, dependencias ni comportamiento.
