# Spec Delta

## MODIFIED Requirements

### Requirement: Servidor no disponible
El sistema SHALL informar con un mensaje claro cuando no pueda conectarse con PocketBase. La dirección se toma de `MI_COTIZADOR_PB_URL`, definida en el entorno o en un archivo `.env` junto a la aplicación, con un valor por defecto (retirado después en el cambio `sin-url-por-defecto`).

#### Scenario: PocketBase apagado
- **WHEN** el usuario intenta iniciar sesión o registrarse y el servidor no responde
- **THEN** el sistema indica que no pudo conectarse y que verifique que el servidor esté en marcha

#### Scenario: Dirección desde el archivo .env
- **WHEN** existe un `.env` junto a la aplicación con `MI_COTIZADOR_PB_URL` definida
- **THEN** el sistema usa esa dirección para conectarse a PocketBase

#### Scenario: Variable de entorno con prioridad
- **WHEN** `MI_COTIZADOR_PB_URL` está definida en el entorno y también en el `.env`
- **THEN** el sistema usa el valor del entorno

#### Scenario: Sin configuración
- **WHEN** no hay `.env` ni variable de entorno, o la variable está vacía
- **THEN** el sistema usa el valor por defecto (retirado después en el cambio `sin-url-por-defecto`)
