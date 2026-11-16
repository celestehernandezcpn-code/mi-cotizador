# Spec Delta

## Purpose

Permite a cada usuario consultar su propio historial de conversiones guardado en PocketBase, garantizando que nadie vea ni altere las consultas de otros.

## ADDED Requirements

### Requirement: Registro de consultas
PocketBase SHALL mantener una colección `consultas` en la que cada registro contiene el usuario propietario, el monto en pesos, la cotización, el resultado en dólares y la fecha y hora de creación asignada por el servidor.

#### Scenario: Consulta creada por su propietario
- **WHEN** un usuario autenticado y activo crea una consulta a su nombre
- **THEN** el servidor la guarda con la fecha y hora actuales

#### Scenario: Consulta a nombre de otro usuario
- **WHEN** un usuario intenta crear una consulta cuyo propietario es otra cuenta
- **THEN** el servidor la rechaza

#### Scenario: Sin autenticación
- **WHEN** una solicitud sin sesión intenta crear o leer consultas
- **THEN** el servidor la rechaza

### Requirement: Historial personal
El sistema SHALL ofrecer una pantalla "Mi historial" que liste, de la más reciente a la más antigua, solo las consultas del usuario que inició sesión, y SHALL permitir volver al conversor.

#### Scenario: Ver el propio historial
- **WHEN** el usuario abre "Mi historial"
- **THEN** ve sus consultas con fecha y hora, monto, cotización y resultado, ordenadas de la más reciente a la más antigua

#### Scenario: Historial vacío
- **WHEN** el usuario no tiene consultas
- **THEN** la pantalla indica que todavía no hay conversiones

#### Scenario: Administrador
- **WHEN** un administrador abre "Mi historial"
- **THEN** ve únicamente sus propias consultas

### Requirement: Aislamiento entre usuarios
PocketBase MUST permitir que cada usuario lea solo sus propias consultas y MUST NOT permitir modificar ni borrar consultas por la API; las cuentas desactivadas no pueden leer ni crear consultas.

#### Scenario: Leer consultas ajenas
- **WHEN** un usuario solicita las consultas de otra cuenta
- **THEN** el servidor no las devuelve

#### Scenario: Modificar o borrar
- **WHEN** cualquier usuario, incluso administrador, intenta modificar o borrar una consulta por la API
- **THEN** el servidor lo rechaza

#### Scenario: Cuenta desactivada con sesión previa
- **WHEN** un usuario desactivado usa una sesión iniciada antes de ser desactivado
- **THEN** el servidor no le permite leer ni crear consultas
