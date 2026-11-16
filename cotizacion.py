"""Consulta de la cotización del dólar oficial en dolarapi.com (valor de venta)."""
import json
import urllib.error
import urllib.request
from datetime import datetime

URL_DOLAR_OFICIAL = "https://dolarapi.com/v1/dolares/oficial"
ESPERA_MAXIMA = 8  # segundos


class ErrorCotizacion(Exception):
    """Error legible para mostrar al usuario."""


def interpretar_respuesta(datos: object) -> tuple[float, str]:
    """Extrae (venta, fecha_iso) de la respuesta; lanza ErrorCotizacion si no es válida."""
    if not isinstance(datos, dict):
        raise ErrorCotizacion("La respuesta del servicio no tiene el formato esperado.")
    venta = datos.get("venta")
    if isinstance(venta, bool) or not isinstance(venta, (int, float)) or not venta > 0:
        raise ErrorCotizacion("El servicio no devolvió una cotización válida.")
    fecha = datos.get("fechaActualizacion")
    return float(venta), fecha if isinstance(fecha, str) else ""


def obtener_cotizacion_oficial() -> tuple[float, str]:
    """Devuelve (venta, fecha_iso) del dólar oficial o lanza ErrorCotizacion."""
    # El servicio rechaza (403) el identificador por defecto de Python: se envía uno propio y genérico.
    req = urllib.request.Request(
        URL_DOLAR_OFICIAL,
        headers={"Accept": "application/json", "User-Agent": "MiCotizador/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=ESPERA_MAXIMA) as resp:
            datos = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ErrorCotizacion(f"El servicio de cotizaciones respondió con un error ({e.code}).") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ErrorCotizacion("No se pudo conectar para obtener la cotización.") from None
    except ValueError:
        raise ErrorCotizacion("La respuesta del servicio no tiene el formato esperado.") from None
    return interpretar_respuesta(datos)


def fecha_legible(fecha_iso: str) -> str:
    """'2026-11-16T18:00:00.000Z' -> '16/11/2026 15:00' (hora local); '' si no se puede leer."""
    try:
        return datetime.fromisoformat(fecha_iso.replace("Z", "+00:00")).astimezone().strftime(
            "%d/%m/%Y %H:%M"
        )
    except ValueError:
        return ""
