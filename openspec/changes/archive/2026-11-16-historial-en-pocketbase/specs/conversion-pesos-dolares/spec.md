# Spec Delta

## MODIFIED Requirements

### Requirement: Historial de conversiones
El sistema SHALL guardar en PocketBase un registro por cada conversión exitosa, asociado al usuario que inició sesión, con monto en pesos, cotización, resultado en dólares y fecha y hora; el sistema MUST NOT escribir `historial.txt`.

#### Scenario: Conversión registrada
- **WHEN** el usuario completa una conversión válida
- **THEN** se crea una consulta en PocketBase con su usuario, el monto, la cotización, el resultado y la fecha y hora

#### Scenario: Ubicación del archivo
- **WHEN** la aplicación se ejecuta como programa empaquetado y el usuario completa una conversión válida
- **THEN** el sistema no crea ni modifica `historial.txt` junto al ejecutable, porque el historial vive en PocketBase

#### Scenario: No se pudo guardar
- **WHEN** PocketBase no responde o rechaza el guardado
- **THEN** el sistema muestra igualmente el resultado y avisa que la conversión no quedó registrada
