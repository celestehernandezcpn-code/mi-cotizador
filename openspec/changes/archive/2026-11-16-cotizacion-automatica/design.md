## Context

El conversor tiene un campo de cotización que el usuario completa a mano. La fuente indicada es el servicio público dolarapi.com, que devuelve para el dólar oficial los valores de compra y venta y la fecha de actualización.

## Goals / Non-Goals

**Goals:**
- Completar la cotización automáticamente al abrir el conversor y a pedido.
- No congelar la ventana ni romperse ante fallos de red.

**Non-Goals:**
- No se ofrecen otros tipos de dólar (blue, MEP, etc.).
- No se guarda una caché ni se actualiza periódicamente.
- No se registra el origen de la cotización en el historial.

## Decisions

- **Módulo `cotizacion.py`:** una función `obtener_cotizacion_oficial()` con `urllib` (sin dependencias nuevas) que devuelve el valor de venta y la fecha. Valida que el valor sea numérico y mayor que cero; ante cualquier fallo lanza un error propio con mensaje claro.
- **Valor de venta:** es el precio de compra de dólares con pesos, adecuado para convertir pesos a dólares.
- **Segundo plano:** tkinter no admite actualizar widgets desde otros hilos, por lo que la consulta corre en un hilo que deja su resultado en una cola y la interfaz la lee periódicamente con `after`. Así la ventana no se congela y no hay accesos concurrentes a widgets.
- **Estado visible:** una etiqueta junto al campo muestra "obteniendo…", el valor con su fecha, o el motivo del fallo.
- **Pantalla cerrada:** al procesar el resultado se comprueba que la pantalla siga existiendo; si no, se descarta.
- **Dirección del servicio:** es pública y no sensible, por lo que se deja como constante en el módulo.

## Risks / Trade-offs

- Depende de un servicio de terceros: si cambia su formato o deja de funcionar, la función falla de forma controlada y el usuario ingresa el valor a mano.
- Cada apertura del conversor realiza una consulta de red.
