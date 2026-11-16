"""Cliente mínimo de PocketBase (solo biblioteca estándar) para iniciar sesión y registrarse."""
import json
import os
import urllib.error
import urllib.request

PB_URL = os.environ.get("MI_COTIZADOR_PB_URL", "http://127.0.0.1:8090").rstrip("/")
COLECCION = "users"


class ErrorPB(Exception):
    """Error legible para mostrar al usuario."""


def _pedir(metodo: str, ruta: str, datos: dict | None = None, token: str = "") -> dict:
    cabeceras = {"Content-Type": "application/json"}
    if token:
        cabeceras["Authorization"] = token
    req = urllib.request.Request(
        f"{PB_URL}{ruta}",
        data=None if datos is None else json.dumps(datos).encode("utf-8"),
        headers=cabeceras,
        method=metodo,
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            cuerpo = json.loads(e.read().decode("utf-8"))
        except ValueError:
            cuerpo = {}
        raise ErrorPB(_mensaje_error(e.code, cuerpo)) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ErrorPB(
            f"No se pudo conectar con PocketBase en {PB_URL}.\n"
            "Verificá que el servidor esté en marcha."
        ) from None


def _mensaje_error(codigo: int, cuerpo: dict) -> str:
    if codigo == 400 and cuerpo.get("data"):
        partes = []
        for campo, info in cuerpo["data"].items():
            msg = info.get("message", "")
            if campo == "email" and "unique" in info.get("code", ""):
                msg = "Ya existe una cuenta con ese email."
            elif campo == "passwordConfirm":
                msg = "Las contraseñas no coinciden."
            elif campo == "password":
                msg = "La contraseña debe tener entre 8 y 72 caracteres."
            elif campo == "email":
                msg = "El email no es válido."
            partes.append(msg)
        return "\n".join(partes)
    if codigo == 400:
        return "Email o contraseña incorrectos, o la cuenta está desactivada."
    if codigo in (401, 403):
        return "No tenés permisos para hacer esto. Volvé a iniciar sesión."
    return cuerpo.get("message") or f"Error del servidor ({codigo})."


def _post(ruta: str, datos: dict) -> dict:
    return _pedir("POST", ruta, datos)


def _listar(coleccion: str, orden: str, token: str) -> list[dict]:
    items, pagina = [], 1
    while True:
        r = _pedir(
            "GET",
            f"/api/collections/{coleccion}/records?perPage=200&page={pagina}&sort={orden}",
            token=token,
        )
        items += r["items"]
        if pagina >= r["totalPages"]:
            return items
        pagina += 1


def listar_usuarios(token: str) -> list[dict]:
    """Lista todas las cuentas (solo funciona para un admin)."""
    return _listar(COLECCION, "email", token)


def crear_consulta(token: str, usuario_id: str, monto: float, cotizacion: float, resultado: float) -> dict:
    """Guarda una conversión del usuario autenticado; la fecha la fija el servidor."""
    return _pedir(
        "POST",
        "/api/collections/consultas/records",
        {"usuario": usuario_id, "monto": monto, "cotizacion": cotizacion, "resultado": resultado},
        token,
    )


def listar_consultas(token: str) -> list[dict]:
    """Conversiones del usuario autenticado (el servidor filtra las ajenas), más recientes primero."""
    return _listar("consultas", "-fecha", token)


def cambiar_estado(token: str, usuario_id: str, desactivado: bool) -> dict:
    return _pedir(
        "PATCH",
        f"/api/collections/{COLECCION}/records/{usuario_id}",
        {"desactivado": desactivado},
        token,
    )


def resetear_password(token: str, usuario_id: str, nueva: str) -> dict:
    return _pedir(
        "PATCH",
        f"/api/collections/{COLECCION}/records/{usuario_id}",
        {"password": nueva, "passwordConfirm": nueva},
        token,
    )


def iniciar_sesion(email: str, password: str) -> dict:
    """Devuelve {'token': ..., 'record': {...}} o lanza ErrorPB."""
    try:
        return _post(
            f"/api/collections/{COLECCION}/auth-with-password",
            {"identity": email, "password": password},
        )
    except ErrorPB as e:
        if str(e).startswith("No tenés permisos"):  # authRule: cuenta desactivada
            raise ErrorPB("Tu cuenta está desactivada. Consultá con un administrador.") from None
        raise


def registrar(email: str, password: str, password_confirm: str) -> dict:
    """Crea el usuario. Lanza ErrorPB si falla."""
    return _post(
        f"/api/collections/{COLECCION}/records",
        {"email": email, "password": password, "passwordConfirm": password_confirm},
    )
