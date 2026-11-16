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
- PocketBase: `cd pocketbase && ./pocketbase.exe serve` (panel en `http://127.0.0.1:8090/_/`).
- Generar el .exe: `python -m PyInstaller --onefile --windowed --name "Mi Cotizador" --paths . mi_cotizador.py`

## Reglas del proyecto

- La seguridad de las cuentas la imponen las reglas de PocketBase (`pocketbase/pb_migrations/`), no la interfaz.
- No se versionan el binario de PocketBase, `pb_data/`, `dist/` ni `historial.txt`.
