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

## Reglas del proyecto

- La seguridad de las cuentas la imponen las reglas de PocketBase (`pocketbase/pb_migrations/`), no la interfaz.
- No se versionan el binario de PocketBase, `pb_data/`, `dist/` ni `historial.txt`.
