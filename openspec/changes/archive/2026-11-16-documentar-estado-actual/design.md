## Context

Este cambio es retroactivo: describe decisiones de diseño ya implementadas en Mi Cotizador, una aplicación de escritorio en Python (tkinter) empaquetada con PyInstaller, que usa PocketBase como servicio de cuentas.

## Goals / Non-Goals

**Goals:**
- Dejar registrado cómo está construido el sistema para poder modificarlo con cambios OpenSpec posteriores.

**Non-Goals:**
- No se cambia código ni comportamiento.
- No se documenta infraestructura de despliegue de PocketBase.

## Decisions

- **Interfaz con tkinter:** viene con Python, no agrega dependencias y alcanza para formularios simples. Una sola ventana cambia entre pantallas (inicio de sesión, registro, conversor, panel).
- **Cliente HTTP con la biblioteca estándar:** `pocketbase_client.py` usa `urllib`, evitando dependencias externas y manteniendo pequeño el ejecutable. Traduce los errores de PocketBase a mensajes en español.
- **Seguridad en el servidor, no en la interfaz:** la aplicación oculta el panel a los no administradores, pero la protección real son las reglas de la colección `users` de PocketBase, definidas en una migración versionada (`pb_migrations/`). Un cliente modificado no puede saltarse esos controles.
- **Campo `desactivado` en lugar de `activo`:** la migración se aplica sobre cuentas existentes; un booleano nuevo vale falso, así que ninguna cuenta previa queda bloqueada.
- **Cambio de contraseña ajena con `manageRule`:** permite a un administrador resetear sin conocer la contraseña anterior, sin crear rutas personalizadas.
- **Primer administrador por superusuario:** ningún flujo de la API permite asignarse el rol; se hace desde el panel de PocketBase.
- **Historial en archivo de texto junto al ejecutable:** simple y legible; no se sincroniza con PocketBase.

## Risks / Trade-offs

- La dirección de PocketBase por defecto es local (`127.0.0.1:8090`); fuera de esa computadora hay que configurar `MI_COTIZADOR_PB_URL` y la conexión no está cifrada salvo que se use HTTPS.
- Una sesión ya iniciada de un usuario desactivado sigue vigente hasta que venza, aunque las reglas le quitan permisos de lectura y edición.
- El historial no es por usuario ni se protege: cualquiera con acceso a la carpeta puede leerlo o editarlo.
