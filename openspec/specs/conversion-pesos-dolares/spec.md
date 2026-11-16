# conversion-pesos-dolares Specification

## Purpose
Permite al usuario convertir un monto en pesos a dólares usando la cotización que ingresa, y deja constancia de cada conversión realizada en un archivo de historial.

## Requirements

### Requirement: Conversión de pesos a dólares
El sistema SHALL calcular el monto en dólares dividiendo el monto en pesos por la cotización del dólar y mostrar el resultado al usuario al accionar "Convertir".

#### Scenario: Conversión válida
- **WHEN** el usuario ingresa un monto de 100.000 pesos y una cotización de 1.200 y acciona "Convertir"
- **THEN** el sistema muestra "USD 83,33"

### Requirement: Lectura de números en formato argentino
El sistema SHALL aceptar montos y cotizaciones con coma como separador decimal y punto como separador de miles, y también con punto decimal.

#### Scenario: Separador de miles
- **WHEN** el usuario ingresa "100.000" en el monto
- **THEN** el sistema lo interpreta como cien mil

#### Scenario: Miles y decimales
- **WHEN** el usuario ingresa "1.500,50"
- **THEN** el sistema lo interpreta como 1500,50

#### Scenario: Punto decimal
- **WHEN** el usuario ingresa "1500.5"
- **THEN** el sistema lo interpreta como 1500,5

### Requirement: Validación de datos de entrada
El sistema MUST rechazar con un mensaje de error los valores no numéricos, los montos negativos y las cotizaciones menores o iguales a cero, sin mostrar resultado ni escribir en el historial.

#### Scenario: Texto no numérico
- **WHEN** el usuario ingresa texto que no es un número y acciona "Convertir"
- **THEN** el sistema informa que debe ingresar números válidos

#### Scenario: Cotización cero
- **WHEN** el usuario ingresa una cotización igual a cero
- **THEN** el sistema informa que la cotización debe ser mayor que cero

#### Scenario: Monto negativo
- **WHEN** el usuario ingresa un monto negativo
- **THEN** el sistema informa que el monto no puede ser negativo

### Requirement: Historial de conversiones
El sistema SHALL agregar una línea a `historial.txt` por cada conversión exitosa, con fecha y hora, email del usuario, monto en pesos, cotización y resultado en dólares.

#### Scenario: Conversión registrada
- **WHEN** el usuario completa una conversión válida
- **THEN** se añade a `historial.txt` una línea con fecha y hora, su email, el monto, la cotización y el resultado

#### Scenario: Ubicación del archivo
- **WHEN** la aplicación se ejecuta como programa empaquetado
- **THEN** `historial.txt` se guarda en la misma carpeta que el ejecutable
