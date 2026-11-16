# Proposal

## Why

La dirección de PocketBase solo se puede cambiar con una variable de entorno del sistema, lo cual es incómodo para quien usa el ejecutable. Un archivo `.env` junto a la aplicación permite configurarla sin tocar el sistema y mantiene la configuración fuera del código y de Git.

## What Changes

- La aplicación lee la dirección de PocketBase (`MI_COTIZADOR_PB_URL`) de un archivo `.env` ubicado junto al ejecutable o al script.
- Una variable de entorno del sistema sigue teniendo prioridad sobre el `.env`; sin ninguna de las dos se usaba un valor por defecto (retirado después en el cambio `sin-url-por-defecto`).
- Se agrega `.env.example` con los nombres de las variables y sin valores, y `.env` se excluye de Git.
- No hay contraseñas ni secretos en el código, por lo que no se traslada ninguno; el `.env` contiene solo la dirección.

## Capabilities

### New Capabilities

### Modified Capabilities
- `autenticacion-usuarios`: el requisito "Servidor no disponible" define de dónde se toma la dirección de PocketBase.

## Impact

- Código: `pocketbase_client.py` (lectura del `.env`).
- Archivos: nuevos `.env` (local, no versionado) y `.env.example`; `.gitignore` y `CLAUDE.md` actualizados.
- Sin cambios de dependencias ni de comportamiento visible, salvo la nueva fuente de configuración.
