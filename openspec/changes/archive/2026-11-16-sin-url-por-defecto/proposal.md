# Proposal

## Why

La dirección de PocketBase es un dato de configuración que no debe figurar en el código ni en la documentación publicada en GitHub. Hoy la aplicación incluye una dirección por defecto escrita en el código, y esa dirección aparece también en especificaciones y guías.

## What Changes

- **BREAKING**: la aplicación deja de tener una dirección de PocketBase por defecto. Debe definirse en `MI_COTIZADOR_PB_URL`, en el entorno o en el archivo `.env`.
- Si no está definida, la aplicación avisa que falta configurarla y no intenta conectarse.
- Los mensajes de error no muestran la dirección del servidor.
- Se retira la dirección concreta del código, de `.env.example`, de `CLAUDE.md` y de las especificaciones y documentos de OpenSpec.

## Capabilities

### New Capabilities

### Modified Capabilities
- `autenticacion-usuarios`: el requisito "Servidor no disponible" elimina la dirección por defecto y define el aviso de configuración faltante.

## Impact

- Código: `pocketbase_client.py`.
- Documentación: `.env.example`, `CLAUDE.md`, especificaciones y cambios archivados de OpenSpec.
- Quien use la aplicación debe tener un `.env` con la dirección; sin él no podrá iniciar sesión ni registrarse.
- Los commits anteriores ya publicados conservan la dirección en su historial.
