"""Servidor MCP (solo lectura) para consultar la base local de PocketBase del proyecto.

Herramienta de desarrollo: permite que un asistente de IA vea las colecciones, sus campos y
reglas, y lea registros. No crea, modifica ni borra nada.

Configuración (nada de esto va en el código):
- Dirección de PocketBase: MI_COTIZADOR_PB_URL, en `.env` (la misma que usa la aplicación).
- Credenciales de superusuario, en `.env.mcp` (no se versiona ni se copia junto al .exe):
    MI_COTIZADOR_MCP_TOKEN      token de superusuario (preferido; no guarda ninguna contraseña), o
    MI_COTIZADOR_MCP_EMAIL y MI_COTIZADOR_MCP_PASSWORD
  Una variable de entorno del sistema tiene prioridad sobre el archivo.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pocketbase_client as pbc  # noqa: E402  (reutiliza el lector de .env y la dirección)
from mcp.server.mcpserver import MCPServer  # noqa: E402
from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402
from mcp.types import ToolAnnotations  # noqa: E402

ESPERA = 15
MAX_POR_PAGINA = 100
RE_COLECCION = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,62}$")
RE_ID = re.compile(r"^[A-Za-z0-9]{1,30}$")


class ErrorMCP(ToolError):
    """Error con mensaje claro para el asistente; nunca incluye direcciones ni credenciales.

    Al ser un ToolError, el SDK entrega el mensaje tal cual (los demás errores los oculta)."""


def _config(nombre: str, env_mcp: dict) -> str:
    return (os.environ.get(nombre) or env_mcp.get(nombre) or "").strip()


class ClienteAdmin:
    """Cliente HTTP de solo lectura que se autentica como superusuario."""

    def __init__(self, url: str, token: str = "", email: str = "", password: str = "") -> None:
        self.url = url.rstrip("/")
        self.token_fijo = token
        self.email = email
        self.password = password
        self._token = token

    @classmethod
    def desde_configuracion(cls) -> "ClienteAdmin":
        env_mcp = pbc.leer_env(RAIZ / ".env.mcp")
        return cls(
            pbc.PB_URL,
            _config("MI_COTIZADOR_MCP_TOKEN", env_mcp),
            _config("MI_COTIZADOR_MCP_EMAIL", env_mcp),
            _config("MI_COTIZADOR_MCP_PASSWORD", env_mcp),
        )

    def _http(self, metodo: str, ruta: str, datos: dict | None = None, token: str = "") -> dict:
        if not self.url:
            raise ErrorMCP("Falta MI_COTIZADOR_PB_URL: definila en el archivo .env del proyecto.")
        cab = {"Content-Type": "application/json", "User-Agent": "MiCotizador-MCP/1.0"}
        if token:
            cab["Authorization"] = token
        req = urllib.request.Request(
            self.url + ruta,
            data=None if datos is None else json.dumps(datos).encode("utf-8"),
            headers=cab,
            method=metodo,
        )
        try:
            with urllib.request.urlopen(req, timeout=ESPERA) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                msg = json.loads(e.read().decode("utf-8")).get("message", "")
            except ValueError:
                msg = ""
            raise ErrorMCP(f"PocketBase respondió con error {e.code}: {msg}".strip()) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ErrorMCP(
                "No se pudo conectar con PocketBase. Verificá que el servidor esté en marcha."
            ) from None

    def _autenticar(self) -> None:
        if self.token_fijo:
            self._token = self.token_fijo
            return
        if not (self.email and self.password):
            raise ErrorMCP(
                "Faltan credenciales de superusuario. Completá MI_COTIZADOR_MCP_TOKEN "
                "(o EMAIL y PASSWORD) en el archivo .env.mcp; ver .env.mcp.example."
            )
        try:
            r = self._http(
                "POST",
                "/api/collections/_superusers/auth-with-password",
                {"identity": self.email, "password": self.password},
            )
        except ErrorMCP as e:
            if "error 400" in str(e):
                raise ErrorMCP("Las credenciales de superusuario no son válidas.") from None
            raise
        self._token = r["token"]

    def get(self, ruta: str, params: dict | None = None) -> dict:
        if params:
            limpios = {k: v for k, v in params.items() if v not in ("", None)}
            if limpios:
                ruta += "?" + urllib.parse.urlencode(limpios)
        if not self._token:
            self._autenticar()
        try:
            return self._http("GET", ruta, token=self._token)
        except ErrorMCP as e:
            if ("error 401" in str(e) or "error 403" in str(e)) and not self.token_fijo:
                self._autenticar()  # el token pudo vencer: se renueva una vez
                return self._http("GET", ruta, token=self._token)
            if "error 401" in str(e) and self.token_fijo:
                raise ErrorMCP(
                    "El token de superusuario venció o no es válido. Generá uno nuevo."
                ) from None
            raise


def validar_coleccion(nombre: str) -> str:
    if (nombre or "").startswith("_"):
        raise ErrorMCP("Las colecciones del sistema (con prefijo _) no se pueden leer con esta herramienta.")
    if not RE_COLECCION.match(nombre or ""):
        raise ErrorMCP("Nombre de colección inválido.")
    return nombre


def validar_id(registro_id: str) -> str:
    if not RE_ID.match(registro_id or ""):
        raise ErrorMCP("Identificador de registro inválido.")
    return registro_id


def resumir_coleccion(c: dict, detalle: bool = False) -> dict:
    campos = [
        {"nombre": f.get("name"), "tipo": f.get("type"), "requerido": bool(f.get("required"))}
        for f in c.get("fields", [])
    ]
    r = {"nombre": c.get("name"), "tipo": c.get("type"), "campos": campos}
    if detalle:
        r["reglas"] = {
            k: c.get(k) for k in ("listRule", "viewRule", "createRule", "updateRule", "deleteRule")
            + (("authRule", "manageRule") if c.get("type") == "auth" else ())
        }
        r["indices"] = c.get("indexes", [])
    return r


servidor = MCPServer(
    "pocketbase",
    instructions=(
        "Consulta de solo lectura de la base local de PocketBase de Mi Cotizador. "
        "Empezá con listar_colecciones y ver_coleccion para conocer la estructura; "
        "después usá listar_registros o ver_registro. No se puede modificar nada."
    ),
)
SOLO_LECTURA = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True)
_cliente: ClienteAdmin | None = None


def cliente() -> ClienteAdmin:
    global _cliente
    if _cliente is None:
        _cliente = ClienteAdmin.desde_configuracion()
    return _cliente


@servidor.tool(annotations=SOLO_LECTURA)
def listar_colecciones() -> dict:
    """Lista las colecciones de PocketBase con el nombre, el tipo y los campos de cada una."""
    r = cliente().get("/api/collections", {"perPage": 200, "sort": "name"})
    return {"colecciones": [resumir_coleccion(c) for c in r.get("items", [])]}


@servidor.tool(annotations=SOLO_LECTURA)
def ver_coleccion(nombre: str) -> dict:
    """Muestra una colección en detalle: campos, reglas de acceso e índices."""
    if not RE_COLECCION.match(nombre or ""):
        raise ErrorMCP("Nombre de colección inválido.")
    return resumir_coleccion(cliente().get(f"/api/collections/{nombre}"), detalle=True)


@servidor.tool(annotations=SOLO_LECTURA)
def listar_registros(
    coleccion: str,
    filtro: str = "",
    orden: str = "",
    pagina: int = 1,
    por_pagina: int = 30,
    expandir: str = "",
) -> dict:
    """Lista registros de una colección (hasta 100 por página).

    filtro usa la sintaxis de PocketBase, por ejemplo: rol = "admin" && desactivado = false.
    orden es una lista de campos separados por coma; un guion adelante indica descendente.
    """
    validar_coleccion(coleccion)
    r = cliente().get(
        f"/api/collections/{coleccion}/records",
        {
            "page": max(1, int(pagina)),
            "perPage": min(max(1, int(por_pagina)), MAX_POR_PAGINA),
            "filter": filtro,
            "sort": orden,
            "expand": expandir,
        },
    )
    return {
        "pagina": r.get("page"),
        "por_pagina": r.get("perPage"),
        "total_registros": r.get("totalItems"),
        "total_paginas": r.get("totalPages"),
        "registros": r.get("items", []),
    }


@servidor.tool(annotations=SOLO_LECTURA)
def ver_registro(coleccion: str, id: str, expandir: str = "") -> dict:
    """Devuelve un registro por su id."""
    validar_coleccion(coleccion)
    validar_id(id)
    return cliente().get(f"/api/collections/{coleccion}/records/{id}", {"expand": expandir})


if __name__ == "__main__":
    servidor.run()
