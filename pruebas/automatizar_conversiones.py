"""Prueba automática de Mi Cotizador: abre la app, inicia sesión, hace 10 conversiones y guarda capturas.

Es seguro correrla: levanta su propio PocketBase temporal (en un puerto libre y con una carpeta de
datos descartable) y crea ahí un usuario de prueba con una contraseña aleatoria que no se guarda en
ningún lado. Nunca se conecta a tu base real ni usa tus cuentas.

Uso (Windows):
    python -m pip install -r pruebas/requirements.txt
    python pruebas/automatizar_conversiones.py [--salida CARPETA] [--cotizacion 1580]

Por defecto usa la cotización que la app trae sola del dólar oficial; con --cotizacion se fija una
(útil sin internet o para resultados repetibles). Sale con código 0 si las 10 conversiones dan lo
esperado y quedaron guardadas en el historial; con 1 si algo falla.
"""
import argparse
import ctypes
import ctypes.wintypes
import os
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
POCKETBASE = RAIZ / "pocketbase" / "pocketbase.exe"
MIGRACIONES = RAIZ / "pocketbase" / "pb_migrations"
EMAIL_PRUEBA = "usuario.prueba@example.test"

# Diez montos distintos, escritos como los escribiría una persona (con miles y decimales).
MONTOS = [
    "1.500", "25.000", "99.999,99", "150.000", "320.500",
    "47.850,50", "8.000", "560.000", "1.000.000", "12.345.678",
]


def activar_dpi() -> None:
    """Hace que las coordenadas de tkinter y de la captura coincidan en pantallas con escala."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass


def puerto_libre(host: str) -> int:
    with socket.socket() as s:
        s.bind((host, 0))
        return s.getsockname()[1]


def levantar_pocketbase(carpeta_datos: Path) -> tuple[subprocess.Popen, str]:
    host = socket.gethostbyname("localhost")  # sin direcciones escritas en el código
    puerto = puerto_libre(host)
    url = f"http://{host}:{puerto}"
    proceso = subprocess.Popen(
        [str(POCKETBASE), "serve", "--http", f"{host}:{puerto}",
         "--dir", str(carpeta_datos), "--migrationsDir", str(MIGRACIONES)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    fin = time.time() + 30
    while time.time() < fin:
        if proceso.poll() is not None:
            raise RuntimeError("El PocketBase temporal terminó al arrancar.")
        try:
            with urllib.request.urlopen(url + "/api/health", timeout=2):
                return proceso, url
        except OSError:
            time.sleep(0.3)
    proceso.terminate()
    raise RuntimeError("El PocketBase temporal no respondió a tiempo.")


def limites_ventana(app) -> tuple[int, int, int, int]:
    """Rectángulo exacto de la ventana (sin sombra ni margen: no se captura nada de lo que hay detrás)."""
    app.update_idletasks()
    try:
        hwnd = ctypes.windll.user32.GetParent(app.winfo_id())
        r = ctypes.wintypes.RECT()
        # DWMWA_EXTENDED_FRAME_BOUNDS = 9
        if ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(r), ctypes.sizeof(r)) == 0:
            return r.left, r.top, r.right, r.bottom
    except Exception:
        pass
    x, y = app.winfo_rootx(), app.winfo_rooty()
    return x, y, x + app.winfo_width(), y + app.winfo_height()


def capturar(app, ruta: Path) -> None:
    from PIL import ImageGrab

    app.update()
    time.sleep(0.15)  # deja que Windows termine de pintar
    ImageGrab.grab(bbox=limites_ventana(app)).save(ruta)


def nombre_captura(n: int, monto: str) -> str:
    limpio = "".join(c if c.isdigit() else "_" for c in monto).strip("_")
    return f"conversion_{n:02d}_{limpio}.png"


def main() -> int:
    ap = argparse.ArgumentParser(description="Prueba automática de Mi Cotizador con capturas.")
    ap.add_argument("--salida", default=str(RAIZ / "capturas_prueba"), help="carpeta de las capturas")
    ap.add_argument("--cotizacion", default="", help="fija la cotización en vez de la automática")
    args = ap.parse_args()

    if os.name != "nt":
        print("Este programa está pensado para Windows.")
        return 1
    if not POCKETBASE.exists():
        print("No se encuentra pocketbase/pocketbase.exe (ver CLAUDE.md para descargarlo).")
        return 1
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("Falta Pillow: python -m pip install -r pruebas/requirements.txt")
        return 1

    activar_dpi()
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    datos = Path(tempfile.mkdtemp(prefix="mi_cotizador_prueba_"))
    proceso = None
    app = None
    try:
        proceso, url = levantar_pocketbase(datos)
        # La app lee la dirección del entorno antes que del .env: se apunta a la base temporal.
        os.environ["MI_COTIZADOR_PB_URL"] = url
        sys.path.insert(0, str(RAIZ))
        import mi_cotizador as m
        import pocketbase_client as pb
        from tkinter import messagebox

        assert pb.PB_URL == url, "la app no apunta a la base temporal: se cancela por seguridad"

        avisos: list[tuple[str, str]] = []  # los cuadros de diálogo se registran en vez de bloquear
        for nombre in ("showerror", "showinfo", "showwarning"):
            setattr(messagebox, nombre, lambda t, s, _n=nombre: avisos.append((_n, s.replace("\n", " "))))

        clave = secrets.token_urlsafe(18)  # contraseña aleatoria, solo para esta ejecución
        pb.registrar(EMAIL_PRUEBA, clave, clave)

        app = m.MiCotizador()
        app.geometry("+100+100")
        app.attributes("-topmost", True)
        app.update()
        print("Mi Cotizador abierto (base temporal).")

        app.actual.email.insert(0, EMAIL_PRUEBA)
        app.actual.password.insert(0, clave)
        app.actual.entrar()
        app.update()
        if type(app.actual).__name__ != "PantallaConversor":
            print("No se pudo iniciar sesión:", avisos)
            return 1
        print(f"Sesión iniciada como {app.email_actual}.")

        c = app.actual
        fin = time.time() + 30
        while c._consultando and time.time() < fin:
            app.update()
            time.sleep(0.05)
        if args.cotizacion:
            c.cotizacion.delete(0, "end")
            c.cotizacion.insert(0, args.cotizacion)
        cotizacion_txt = c.cotizacion.get()
        if not cotizacion_txt:
            print("La app no pudo traer la cotización; usá --cotizacion para fijar una.")
            return 1
        cot = m.parsear_numero(cotizacion_txt)
        print(f"Cotización usada: {cotizacion_txt}\n")

        print(f"{'#':>2} {'Monto (ARS)':>14} {'Resultado en pantalla':>24} {'Esperado':>12}  Estado")
        fallas = 0
        for n, monto in enumerate(MONTOS, 1):
            c.monto.delete(0, "end")
            c.monto.insert(0, monto)
            c.convertir()
            app.update()
            en_pantalla = c.resultado.cget("text").removeprefix("Resultado: ")
            esperado = "USD " + m.formatear(m.parsear_numero(monto) / cot)
            ok = en_pantalla == esperado
            fallas += not ok
            capturar(app, salida / nombre_captura(n, monto))
            print(f"{n:>2} {monto:>14} {en_pantalla:>24} {esperado:>12}  {'OK' if ok else 'DIFERENTE'}")

        guardadas = pb.listar_consultas(app.token)
        en_historial = sorted(round(g["monto"], 2) for g in guardadas)
        esperadas = sorted(round(m.parsear_numero(x), 2) for x in MONTOS)
        historial_ok = en_historial == esperadas
        print(f"\nConversiones guardadas en el historial: {len(guardadas)} de {len(MONTOS)} "
              f"({'coinciden los montos' if historial_ok else 'NO coinciden los montos'}).")
        if avisos:
            print("Avisos de la app durante la prueba:", avisos)
        print(f"Capturas guardadas en: {salida}")
        return 0 if (fallas == 0 and historial_ok and not avisos) else 1
    finally:
        if app is not None:
            try:
                app.destroy()
            except Exception:
                pass
        if proceso is not None:
            proceso.terminate()
            try:
                proceso.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proceso.kill()
        shutil.rmtree(datos, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
