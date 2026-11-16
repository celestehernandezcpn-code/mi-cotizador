# Proposal

## Why

Hoy el usuario debe buscar e ingresar a mano la cotización del dólar, con el riesgo de errores o de usar un valor desactualizado. La aplicación puede obtener el dólar oficial de una fuente pública y ahorrar ese paso.

## What Changes

- Al abrirse el conversor, la aplicación consulta la cotización del dólar oficial en dolarapi.com y la completa en el campo de cotización.
- Se agrega un botón "Actualizar" que vuelve a consultarla cuando el usuario quiera.
- Junto al campo se muestra de dónde viene el valor y su fecha de actualización.
- El campo sigue siendo editable: el usuario puede usar otro valor.
- Si la consulta falla, la aplicación lo informa sin bloquearse y el usuario puede ingresar la cotización a mano.

## Capabilities

### New Capabilities
- `cotizacion-oficial`: obtención automática y manual de la cotización del dólar oficial desde dolarapi.com.

### Modified Capabilities

## Impact

- Código: nuevo módulo `cotizacion.py` y cambios en la pantalla del conversor de `mi_cotizador.py`.
- Sistemas: dependencia de un servicio público externo (`dolarapi.com`); la aplicación necesita acceso a internet para esta función, y solo envía una consulta sin datos del usuario.
- Sin dependencias nuevas de Python.

## Supuestos

- Se usa el valor de **venta** del dólar oficial, que es el precio al que se compran dólares con pesos, coherente con la conversión de pesos a dólares.
- La consulta automática ocurre al abrirse el conversor (tras iniciar sesión), que es donde está el campo de cotización.
- El botón reemplaza el valor del campo, incluso si el usuario lo había editado.
- La consulta se hace en segundo plano para no congelar la ventana, con un tiempo máximo de espera de 8 segundos.
