## Context

El historial es hoy un archivo local escrito por `mi_cotizador.py`. Las cuentas ya viven en PocketBase (colección `users`) y la seguridad se impone con reglas definidas en migraciones versionadas.

## Goals / Non-Goals

**Goals:**
- Guardar cada conversión en PocketBase asociada a su usuario.
- Que cada usuario vea solo su historial, con la garantía impuesta por el servidor.

**Non-Goals:**
- No se migran los datos de `historial.txt`.
- No se agrega una vista de historial de todos los usuarios para administradores.
- No hay modo sin conexión ni cola de reintentos.

## Decisions

- **Colección `consultas` creada por migración JS** en `pocketbase/pb_migrations/`, igual que la migración de `users`, para que se aplique automáticamente y quede versionada.
- **Campos:** `usuario` (relación obligatoria a `users`, con borrado en cascada), `monto`, `cotizacion` y `resultado` (números) y `fecha` (autodate, se fija al crear). La fecha la asigna el servidor, no el cliente, para que no pueda falsearse.
- **Reglas:**
  - listar y ver: `usuario = @request.auth.id && @request.auth.desactivado = false`;
  - crear: sesión de usuario activo y `@request.body.usuario = @request.auth.id`;
  - modificar y borrar: ninguna (solo el superusuario).
  Se prefiere un registro inmutable para que el historial sea confiable.
- **Cliente:** se agregan a `pocketbase_client.py` las funciones para crear una consulta y para listar las propias (ordenadas por `-fecha`), reutilizando el manejo de errores existente.
- **Pantalla "Mi historial":** una tabla de solo lectura con acceso desde el conversor y desde el panel de administración, y botón para volver.
- **Fallo de guardado:** no bloquea el resultado; se avisa al usuario. Es preferible mostrar la conversión a perderla, aunque implique un registro faltante.
- **`historial.txt`:** la aplicación deja de usarlo. Se elimina el código que lo escribe; el archivo queda en `.gitignore`.

## Risks / Trade-offs

- Sin conexión a PocketBase las conversiones se muestran pero no se registran.
- Un administrador no puede auditar historiales ajenos desde la app (sí el superusuario desde el panel de PocketBase).
- Aplicar la migración requiere reiniciar PocketBase.
