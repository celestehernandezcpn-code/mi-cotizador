# Proposal

## Why

Hoy cada conversión se guarda en un `historial.txt` local, sin separación por usuario y editable por cualquiera con acceso a la carpeta. Al existir ya cuentas de usuario en PocketBase, el historial puede guardarse en el servidor, asociado a cada usuario y protegido por reglas de acceso.

## What Changes

- Se crea en PocketBase una colección `consultas` con usuario, monto en pesos, cotización, resultado en dólares y fecha y hora.
- Cada conversión exitosa se guarda en esa colección en lugar de `historial.txt`.
- Se agrega en la aplicación una pantalla "Mi historial" que lista las consultas del usuario que inició sesión.
- Las reglas de PocketBase hacen que cada usuario solo pueda crear y ver sus propias consultas; nadie puede modificarlas ni borrarlas por la API.
- **BREAKING**: la aplicación deja de escribir `historial.txt`. El archivo existente no se migra ni se borra; queda como está.

## Capabilities

### New Capabilities
- `historial-consultas`: consulta del historial personal de conversiones guardado en PocketBase, con acceso restringido al propietario.

### Modified Capabilities
- `conversion-pesos-dolares`: el requisito "Historial de conversiones" pasa de un archivo de texto local a registros en PocketBase.

## Impact

- Código: `mi_cotizador.py` (guardado de conversiones y nueva pantalla), `pocketbase_client.py` (crear y listar consultas).
- PocketBase: nueva migración en `pocketbase/pb_migrations/` que crea la colección `consultas` y sus reglas.
- Dependencias: ninguna nueva.
- Requiere conexión con PocketBase para registrar conversiones.

## Supuestos

- Un administrador ve solo su propio historial, igual que los demás usuarios; el superusuario de PocketBase puede ver todos desde su panel.
- Si no se puede guardar la consulta, se muestra igualmente el resultado y se avisa que no quedó registrada.
- La fecha y hora la asigna el servidor al crear la consulta.
