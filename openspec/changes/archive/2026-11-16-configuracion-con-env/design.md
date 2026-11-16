## Context

`pocketbase_client.py` toma la dirección de PocketBase de `os.environ` con un valor por defecto. El proyecto no usa dependencias externas para la aplicación.

## Goals / Non-Goals

**Goals:**
- Configurar la dirección de PocketBase desde un `.env`, sin tocar variables del sistema.
- Mantener el `.env` real fuera de Git y publicar un `.env.example` sin valores.

**Non-Goals:**
- No se trasladan contraseñas: el código no contiene ninguna.
- No se agregan variables que ningún código lea.

## Decisions

- **Lector propio de `.env`:** una función pequeña (líneas `CLAVE=valor`, ignora vacías y comentarios, admite comillas) en lugar de `python-dotenv`, para no sumar dependencias ni peso al ejecutable.
- **Ubicación:** junto al ejecutable (si está empaquetado) o al script. Así el usuario puede editarlo sin recompilar; PyInstaller no lo incluye en el `.exe`.
- **Prioridad:** variable de entorno > `.env` > valor por defecto. Un valor vacío se trata como no definido.
- **`.env.example` sin valores:** lista las variables vacías para documentar qué configurar.

## Risks / Trade-offs

- Si el `.env` no se copia junto al ejecutable, se usa la dirección local por defecto sin aviso.
- El analizador no soporta sintaxis avanzada de `.env` (interpolación, multilínea).
