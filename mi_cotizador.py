"""Mi Cotizador: convierte pesos a dólares y guarda cada conversión en historial.txt.

Requiere iniciar sesión con un usuario de PocketBase antes de abrir el conversor.
"""
import re
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

import pocketbase_client as pb


def carpeta_base() -> Path:
    """Carpeta del .exe (si está empaquetado) o del script."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


HISTORIAL = carpeta_base() / "historial.txt"


def parsear_numero(texto: str) -> float:
    """Acepta '1500', '1500.50', '1500,50' y '1.500,50'."""
    t = texto.strip().replace(" ", "").replace("$", "")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", t):  # '100.000' = cien mil
        t = t.replace(".", "")
    return float(t)


def formatear(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def convertir_pesos_a_dolares(pesos: float, cotizacion: float) -> float:
    if cotizacion <= 0:
        raise ValueError("La cotización debe ser mayor que cero.")
    return pesos / cotizacion


def guardar_historial(pesos: float, cotizacion: float, dolares: float, usuario: str = "") -> None:
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = (
        f"{ahora} | {usuario} | ARS {formatear(pesos)} | cotización {formatear(cotizacion)} "
        f"| USD {formatear(dolares)}\n"
    )
    with open(HISTORIAL, "a", encoding="utf-8") as f:
        f.write(linea)


class PantallaLogin(ttk.Frame):
    def __init__(self, app: "MiCotizador") -> None:
        super().__init__(app, padding=20)
        self.app = app
        ttk.Label(self, text="Iniciar sesión", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )
        ttk.Label(self, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        self.email = ttk.Entry(self, width=28)
        self.email.grid(row=1, column=1, pady=5, padx=(10, 0))
        ttk.Label(self, text="Contraseña:").grid(row=2, column=0, sticky="w", pady=5)
        self.password = ttk.Entry(self, width=28, show="•")
        self.password.grid(row=2, column=1, pady=5, padx=(10, 0))
        self.boton = ttk.Button(self, text="Entrar", command=self.entrar)
        self.boton.grid(row=3, column=0, columnspan=2, pady=(12, 4))
        ttk.Button(self, text="Crear cuenta", command=app.mostrar_registro).grid(
            row=4, column=0, columnspan=2
        )
        self.password.bind("<Return>", lambda _e: self.entrar())
        self.email.bind("<Return>", lambda _e: self.password.focus())

    def limpiar(self) -> None:
        self.password.delete(0, tk.END)
        self.email.focus()

    def entrar(self) -> None:
        email = self.email.get().strip()
        if not email or not self.password.get():
            messagebox.showerror("Inicio de sesión", "Completá el email y la contraseña.")
            return
        self.boton.state(["disabled"])
        self.update_idletasks()
        try:
            datos = pb.iniciar_sesion(email, self.password.get())
        except pb.ErrorPB as e:
            messagebox.showerror("Inicio de sesión", str(e))
            return
        finally:
            self.boton.state(["!disabled"])
        self.app.mostrar_conversor(datos["record"].get("email", email))


class PantallaRegistro(ttk.Frame):
    def __init__(self, app: "MiCotizador") -> None:
        super().__init__(app, padding=20)
        self.app = app
        ttk.Label(self, text="Crear cuenta", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 10)
        )
        ttk.Label(self, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        self.email = ttk.Entry(self, width=28)
        self.email.grid(row=1, column=1, pady=5, padx=(10, 0))
        ttk.Label(self, text="Contraseña:").grid(row=2, column=0, sticky="w", pady=5)
        self.password = ttk.Entry(self, width=28, show="•")
        self.password.grid(row=2, column=1, pady=5, padx=(10, 0))
        ttk.Label(self, text="Repetir contraseña:").grid(row=3, column=0, sticky="w", pady=5)
        self.confirmar = ttk.Entry(self, width=28, show="•")
        self.confirmar.grid(row=3, column=1, pady=5, padx=(10, 0))
        ttk.Label(self, text="Mínimo 8 caracteres.", foreground="gray").grid(
            row=4, column=1, sticky="w", padx=(10, 0)
        )
        self.boton = ttk.Button(self, text="Registrarme", command=self.registrar)
        self.boton.grid(row=5, column=0, columnspan=2, pady=(12, 4))
        ttk.Button(self, text="Volver a iniciar sesión", command=app.mostrar_login).grid(
            row=6, column=0, columnspan=2
        )
        self.confirmar.bind("<Return>", lambda _e: self.registrar())

    def limpiar(self) -> None:
        for campo in (self.password, self.confirmar):
            campo.delete(0, tk.END)
        self.email.focus()

    def registrar(self) -> None:
        email = self.email.get().strip()
        if not email or not self.password.get():
            messagebox.showerror("Registro", "Completá todos los campos.")
            return
        if self.password.get() != self.confirmar.get():
            messagebox.showerror("Registro", "Las contraseñas no coinciden.")
            return
        self.boton.state(["disabled"])
        self.update_idletasks()
        try:
            pb.registrar(email, self.password.get(), self.confirmar.get())
        except pb.ErrorPB as e:
            messagebox.showerror("Registro", str(e))
            return
        finally:
            self.boton.state(["!disabled"])
        messagebox.showinfo("Registro", "Cuenta creada. Ahora podés iniciar sesión.")
        self.app.mostrar_login(email)


class PantallaConversor(ttk.Frame):
    def __init__(self, app: "MiCotizador", usuario: str) -> None:
        super().__init__(app, padding=20)
        self.app = app
        self.usuario = usuario

        ttk.Label(self, text=f"Sesión: {usuario}", foreground="gray").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(self, text="Cerrar sesión", command=app.cerrar_sesion).grid(
            row=0, column=1, sticky="e"
        )

        ttk.Label(self, text="Monto en pesos (ARS):").grid(row=1, column=0, sticky="w", pady=5)
        self.monto = ttk.Entry(self, width=22)
        self.monto.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(self, text="Cotización del dólar:").grid(row=2, column=0, sticky="w", pady=5)
        self.cotizacion = ttk.Entry(self, width=22)
        self.cotizacion.grid(row=2, column=1, pady=5, padx=(10, 0))

        ttk.Button(self, text="Convertir", command=self.convertir).grid(
            row=3, column=0, columnspan=2, pady=12
        )

        self.resultado = ttk.Label(self, text="Resultado: —", font=("Segoe UI", 13, "bold"))
        self.resultado.grid(row=4, column=0, columnspan=2)

        app.bind("<Return>", lambda _e: self.convertir())
        self.monto.focus()

    def convertir(self) -> None:
        try:
            pesos = parsear_numero(self.monto.get())
            cotiz = parsear_numero(self.cotizacion.get())
            if pesos < 0:
                raise ValueError("El monto no puede ser negativo.")
            dolares = convertir_pesos_a_dolares(pesos, cotiz)
        except ValueError as e:
            msg = str(e)
            if msg.startswith("could not convert"):
                msg = "Ingresá números válidos en ambos campos."
            messagebox.showerror("Dato inválido", msg)
            return

        self.resultado.config(text=f"Resultado: USD {formatear(dolares)}")
        try:
            guardar_historial(pesos, cotiz, dolares, self.usuario)
        except OSError as e:
            messagebox.showwarning("Historial", f"No se pudo guardar el historial:\n{e}")


class MiCotizador(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mi Cotizador")
        self.resizable(False, False)
        self.actual: ttk.Frame | None = None
        self.mostrar_login()

    def _mostrar(self, pantalla: ttk.Frame) -> None:
        self.unbind("<Return>")
        if self.actual is not None:
            self.actual.destroy()
        self.actual = pantalla
        pantalla.grid()

    def mostrar_login(self, email: str = "") -> None:
        pantalla = PantallaLogin(self)
        self._mostrar(pantalla)
        if email:
            pantalla.email.insert(0, email)
            pantalla.password.focus()
        else:
            pantalla.email.focus()

    def mostrar_registro(self) -> None:
        pantalla = PantallaRegistro(self)
        self._mostrar(pantalla)
        pantalla.email.focus()

    def mostrar_conversor(self, usuario: str) -> None:
        self._mostrar(PantallaConversor(self, usuario))

    def cerrar_sesion(self) -> None:
        self.mostrar_login()


if __name__ == "__main__":
    MiCotizador().mainloop()
