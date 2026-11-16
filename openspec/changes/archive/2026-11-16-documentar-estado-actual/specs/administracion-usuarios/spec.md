# Spec Delta

## Purpose

Define los roles de usuario y las herramientas de un administrador para gestionar cuentas (listar, desactivar y resetear contraseñas), junto con las reglas de acceso que impiden que otros usuarios realicen esas acciones.

## ADDED Requirements

### Requirement: Rol de usuario
Cada cuenta SHALL tener un rol "usuario" o "admin" y un estado activo o desactivado; las cuentas nuevas MUST crearse como usuario común y activas.

#### Scenario: Registro sin privilegios
- **WHEN** alguien se registra
- **THEN** su cuenta queda con rol común y activa

#### Scenario: Intento de asignarse un rol al registrarse
- **WHEN** una solicitud de registro incluye un rol o un estado
- **THEN** el servidor rechaza el registro

### Requirement: Panel de administración
Cuando inicia sesión un administrador activo, el sistema SHALL mostrar un panel con la lista de todas las cuentas (email, rol y estado) y acceso al conversor; un usuario sin rol de administrador MUST NOT acceder al panel.

#### Scenario: Ingreso de un administrador
- **WHEN** un administrador activo inicia sesión
- **THEN** ve primero el panel con todas las cuentas

#### Scenario: Ingreso de un usuario común
- **WHEN** un usuario común inicia sesión
- **THEN** ve el conversor y no dispone de acceso al panel

#### Scenario: Volver al conversor
- **WHEN** el administrador acciona "Abrir conversor"
- **THEN** ve el conversor y puede regresar al panel con "Panel admin"

### Requirement: Activar y desactivar cuentas
El administrador SHALL poder desactivar y reactivar cuentas, previa confirmación, y MUST NOT poder desactivar su propia cuenta.

#### Scenario: Desactivar una cuenta
- **WHEN** el administrador selecciona una cuenta, acciona "Activar / Desactivar" y confirma
- **THEN** la cuenta pasa a "Desactivada" y su titular ya no puede iniciar sesión

#### Scenario: Reactivar una cuenta
- **WHEN** el administrador acciona el cambio sobre una cuenta desactivada y confirma
- **THEN** la cuenta vuelve a "Activa"

#### Scenario: Autodesactivación
- **WHEN** el administrador intenta desactivar su propia cuenta
- **THEN** el sistema se lo impide con un aviso

### Requirement: Resetear contraseña
El administrador SHALL poder establecer una nueva contraseña de 8 a 72 caracteres para otra cuenta sin conocer la anterior.

#### Scenario: Reseteo exitoso
- **WHEN** el administrador selecciona una cuenta e ingresa una contraseña válida
- **THEN** la contraseña anterior deja de funcionar y el titular ingresa con la nueva

#### Scenario: Sin cuenta seleccionada
- **WHEN** el administrador acciona una operación sin elegir una cuenta
- **THEN** el sistema le pide elegir una cuenta de la lista

### Requirement: Reglas de acceso en el servidor
PocketBase SHALL restringir al administrador activo el listado de cuentas, el cambio de rol o estado y el cambio de contraseña ajena; cada usuario común solo SHALL ver y editar su propia ficha, sin tocar su rol ni su estado, y ninguna cuenta puede borrarse por la API.

#### Scenario: Usuario común intenta listar o modificar a otros
- **WHEN** un usuario común solicita listar cuentas, desactivar a otro o resetear su contraseña
- **THEN** el servidor rechaza o no devuelve esos datos

#### Scenario: Autopromoción
- **WHEN** un usuario común intenta cambiar su propio rol a administrador
- **THEN** el servidor lo rechaza

#### Scenario: Administrador desactivado con sesión previa
- **WHEN** un administrador desactivado usa una sesión iniciada antes de ser desactivado
- **THEN** pierde sus permisos de administración

#### Scenario: Primer administrador
- **WHEN** aún no existe ningún administrador
- **THEN** solo un superusuario de PocketBase puede asignar el rol "admin" desde su panel
