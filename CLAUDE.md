# Mi Cotizador

Aplicación de escritorio en Python (tkinter) que convierte pesos a dólares. Usa PocketBase para las cuentas de usuario. Se empaqueta con PyInstaller.

## Flujo de trabajo: OpenSpec

Este proyecto usa OpenSpec. Las especificaciones vigentes están en `openspec/specs/`.

- Todo cambio de comportamiento (funcionalidad nueva, cambio de reglas, de pantallas o de permisos) se plantea primero con `/openspec-propose`, se implementa con `/openspec-apply-change` y se cierra con `/openspec-archive-change`.
- No se programa un cambio de comportamiento antes de tener su propuesta.
- Correcciones menores que no cambian lo que dicen las especificaciones (errores de tipeo, refactors internos) pueden hacerse sin propuesta.
- Los artefactos se escriben en español; los encabezados de OpenSpec y las palabras SHALL/MUST quedan en inglés.

## Comandos útiles

- Ejecutar la app: `python mi_cotizador.py` (requiere PocketBase en marcha).
- PocketBase: `cd pocketbase && ./pocketbase.exe serve` (muestra en consola la dirección del servidor; el panel está en la ruta `/_/`).
- Generar el .exe: `python -m PyInstaller --onefile --windowed --name "Mi Cotizador" --paths . mi_cotizador.py`

## Configuración

- La dirección de PocketBase se define en `.env` (`MI_COTIZADOR_PB_URL`), que va junto al script o al `.exe`. Copiá `.env.example` como `.env`. Una variable de entorno del sistema tiene prioridad. No hay dirección por defecto: sin configurarla, la app avisa y no se conecta.
- `.env` no se versiona y no debe contener contraseñas ni secretos que no hagan falta.
- No escribir la dirección concreta de PocketBase en código, documentación, especificaciones ni mensajes: solo en `.env`.

## Servidor MCP de PocketBase (herramienta de desarrollo)

- `mcp_pocketbase/servidor.py` expone la base local a Claude Code, **solo lectura**: `listar_colecciones`, `ver_coleccion`, `listar_registros` y `ver_registro`. Está registrado en `.mcp.json` y usa el entorno virtual `.venv`.
- Instalación: `python -m venv .venv` y luego `.venv\Scripts\python.exe -m pip install -r mcp_pocketbase/requirements.txt`.
- La dirección sale de `MI_COTIZADOR_PB_URL` (`.env`). Las credenciales de superusuario van en `.env.mcp` (copiar `.env.mcp.example`), preferentemente un token. `.env.mcp` no se versiona y nunca debe copiarse junto al `.exe`.
- No lee colecciones del sistema (prefijo `_`). Para escribir datos no hay herramientas a propósito: los cambios van por migraciones o por el panel de PocketBase.

## Prueba automática con capturas

- `pruebas/automatizar_conversiones.py` abre la app, inicia sesión con un usuario de prueba, hace 10 conversiones con montos distintos, verifica cada resultado y guarda una captura de cada una en `capturas_prueba/` (no se versiona).
- Corre contra un PocketBase **temporal** que el propio programa levanta y descarta; nunca toca la base real. El usuario de prueba tiene contraseña aleatoria por ejecución.
- Uso: `python -m pip install -r pruebas/requirements.txt` y luego `python pruebas/automatizar_conversiones.py [--cotizacion 1580]`. Requiere `pocketbase/pocketbase.exe` y Windows.

## Reglas del proyecto

- La seguridad de las cuentas la imponen las reglas de PocketBase (`pocketbase/pb_migrations/`), no la interfaz.
- No se versionan el binario de PocketBase, `pb_data/`, `dist/` ni `historial.txt`.
