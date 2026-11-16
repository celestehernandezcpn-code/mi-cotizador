# cotizacion-oficial Specification

## Purpose
Evita que el usuario deba buscar e ingresar la cotización del dólar, obteniendo la del dólar oficial desde una fuente pública al abrir el conversor y a pedido.

## Requirements

### Requirement: Cotización automática al abrir el conversor
Al mostrarse el conversor, el sistema SHALL consultar la cotización de venta del dólar oficial en dolarapi.com y completar con ella el campo de cotización, sin impedir el uso de la pantalla mientras espera.

#### Scenario: Consulta exitosa
- **WHEN** el usuario abre el conversor y el servicio responde con una cotización válida
- **THEN** el campo de cotización se completa con el valor de venta y se muestra su fecha de actualización

#### Scenario: Pantalla utilizable durante la espera
- **WHEN** la consulta está en curso
- **THEN** el usuario puede seguir usando la ventana y se indica que la cotización se está obteniendo

### Requirement: Actualizar la cotización
El sistema SHALL ofrecer un botón "Actualizar" que vuelva a consultar la cotización y reemplace el valor del campo.

#### Scenario: Actualización manual
- **WHEN** el usuario acciona "Actualizar" y el servicio responde con una cotización válida
- **THEN** el campo se reemplaza por el nuevo valor, aunque el usuario lo hubiera editado, y se actualiza la fecha mostrada

#### Scenario: Una consulta a la vez
- **WHEN** hay una consulta en curso y el usuario acciona "Actualizar"
- **THEN** el sistema no inicia una segunda consulta hasta que termine la actual

### Requirement: Cotización editable
El campo de cotización SHALL seguir siendo editable, y la conversión MUST usar el valor que tenga el campo al accionar "Convertir".

#### Scenario: Valor propio
- **WHEN** el usuario escribe otra cotización en el campo
- **THEN** la conversión usa ese valor

### Requirement: Fallo de la consulta
Si la consulta no puede completarse, el sistema SHALL informarlo sin bloquear la aplicación y MUST conservar el valor que tuviera el campo; también MUST descartar respuestas que no contengan una cotización numérica mayor que cero.

#### Scenario: Sin conexión o servicio caído
- **WHEN** no hay conexión o el servicio no responde a tiempo
- **THEN** el sistema indica que no pudo obtener la cotización y que puede ingresarla a mano, y el campo conserva su valor

#### Scenario: Respuesta inválida
- **WHEN** el servicio responde con un dato que no es una cotización válida
- **THEN** el sistema lo trata como un fallo y no modifica el campo

#### Scenario: Cierre de la pantalla durante la consulta
- **WHEN** el usuario sale del conversor antes de que termine la consulta
- **THEN** el resultado se descarta sin errores
