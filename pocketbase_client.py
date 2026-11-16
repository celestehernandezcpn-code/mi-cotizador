"""Cliente mínimo de PocketBase (solo biblioteca estándar) para iniciar sesión y registrarse."""
import json
import os
import urllib.error
import urllib.request

PB_URL = os.environ.get("MI_COTIZADOR_PB_URL", "http://127.0.0.1:8090").rstrip("/")
COLECCION = "users"


class ErrorPB(Exception):
    """Error legible para mostrar al usuario."""


def _post(ruta: str, datos: dict) -> dict:
    req = urllib.request.Request(
        f"{PB_URL}{ruta}",
        data=json.dumps(datos).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
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
        return "Email o contraseña incorrectos."
    return cuerpo.get("message") or f"Error del servidor ({codigo})."


def iniciar_sesion(email: str, password: str) -> dict:
    """Devuelve {'token': ..., 'record': {...}} o lanza ErrorPB."""
    return _post(
        f"/api/collections/{COLECCION}/auth-with-password",
        {"identity": email, "password": password},
    )


def registrar(email: str, password: str, password_confirm: str) -> dict:
    """Crea el usuario. Lanza ErrorPB si falla."""
    return _post(
        f"/api/collections/{COLECCION}/records",
        {"email": email, "password": password, "passwordConfirm": password_confirm},
    )
