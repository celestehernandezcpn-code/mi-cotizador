## Context

`pocketbase_client.py` resuelve la dirección con prioridad entorno > `.env` > valor por defecto escrito en el código. Ese valor por defecto, y las menciones en documentación, exponen la dirección en el repositorio público.

## Goals / Non-Goals

**Goals:**
- Que ningún archivo versionado contenga la dirección concreta de PocketBase.
- Que la falta de configuración produzca un aviso claro y no un intento de conexión a una dirección supuesta.

**Non-Goals:**
- No se reescribe el historial de Git en este cambio: los commits anteriores conservan la dirección salvo que el usuario pida reescribirlo.

## Decisions

- **Sin valor por defecto:** `resolver_url` devuelve cadena vacía si no hay configuración. Esto obliga a configurar explícitamente y evita conectarse a un servidor no previsto.
- **Aviso al operar, no al arrancar:** la comprobación ocurre al hacer una solicitud (iniciar sesión, registrarse), reutilizando el manejo de `ErrorPB`; la interfaz muestra el mensaje en el cuadro habitual.
- **Mensajes sin dirección:** el error de conexión ya no incluye la URL.
- **Documentación sin la dirección:** `CLAUDE.md` y `.env.example` indican dónde configurarla sin repetirla; los documentos archivados de OpenSpec se editan para retirarla.

## Risks / Trade-offs

- Quien no tenga `.env` verá el aviso de configuración en lugar de conectarse automáticamente.
- El historial anterior de Git sigue mostrando la dirección hasta que se reescriba.
