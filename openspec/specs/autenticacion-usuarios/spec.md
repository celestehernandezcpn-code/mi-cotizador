# autenticacion-usuarios Specification

## Purpose
Controla el acceso a la aplicación mediante registro e inicio de sesión con las cuentas de usuario de PocketBase, de modo que solo usuarios autenticados usen el conversor.

## Requirements

### Requirement: Pantalla de inicio de sesión
Al abrirse, el sistema SHALL mostrar una pantalla de inicio de sesión con email y contraseña, y MUST NOT mostrar el conversor hasta que la autenticación sea exitosa.

#### Scenario: Apertura de la aplicación
- **WHEN** el usuario abre la aplicación
- **THEN** ve la pantalla de inicio de sesión y no el conversor

#### Scenario: Credenciales correctas
- **WHEN** un usuario activo ingresa su email y contraseña correctos
- **THEN** el sistema lo autentica y abre el conversor

#### Scenario: Credenciales incorrectas
- **WHEN** el usuario ingresa un email o contraseña incorrectos
- **THEN** el sistema muestra un mensaje de error y permanece en la pantalla de inicio de sesión

#### Scenario: Campos vacíos
- **WHEN** el usuario acciona "Entrar" sin completar email y contraseña
- **THEN** el sistema le pide completar ambos campos

### Requirement: Registro de usuarios
El sistema SHALL ofrecer una pantalla de registro con email, contraseña y confirmación, que cree una cuenta común en PocketBase.

#### Scenario: Registro exitoso
- **WHEN** el usuario ingresa un email válido y una contraseña de 8 a 72 caracteres repetida correctamente
- **THEN** se crea la cuenta, se informa el éxito y se vuelve al inicio de sesión con el email ya completado

#### Scenario: Contraseñas distintas
- **WHEN** la contraseña y su confirmación no coinciden
- **THEN** el sistema informa que no coinciden y no crea la cuenta

#### Scenario: Email ya registrado
- **WHEN** el usuario se registra con un email que ya tiene cuenta
- **THEN** el sistema informa que ya existe una cuenta con ese email

#### Scenario: Contraseña corta
- **WHEN** la contraseña tiene menos de 8 caracteres
- **THEN** el sistema informa el rango de longitud permitido y no crea la cuenta

### Requirement: Cuenta desactivada
El sistema MUST impedir el inicio de sesión de una cuenta desactivada e informar al usuario que su cuenta está desactivada.

#### Scenario: Intento de ingreso con cuenta desactivada
- **WHEN** un usuario desactivado ingresa sus credenciales correctas
- **THEN** el sistema rechaza el ingreso y le indica que consulte con un administrador

### Requirement: Cierre de sesión
El sistema SHALL permitir cerrar sesión desde el conversor y el panel de administración, y volver a la pantalla de inicio de sesión descartando la sesión.

#### Scenario: Cierre de sesión
- **WHEN** el usuario acciona "Cerrar sesión"
- **THEN** vuelve a la pantalla de inicio de sesión y debe autenticarse de nuevo para usar el conversor

### Requirement: Servidor no disponible
El sistema SHALL informar con un mensaje claro cuando no pueda conectarse con PocketBase, cuya dirección por defecto es `http://127.0.0.1:8090` y es configurable.

#### Scenario: PocketBase apagado
- **WHEN** el usuario intenta iniciar sesión o registrarse y el servidor no responde
- **THEN** el sistema indica que no pudo conectarse y que verifique que el servidor esté en marcha
