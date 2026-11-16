"""Mi Cotizador: convierte pesos a dólares y guarda cada conversión en historial.txt.

Requiere iniciar sesión con un usuario de PocketBase antes de abrir el conversor.
"""
import re
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

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
        self.app.iniciar(datos)


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


class PantallaAdmin(ttk.Frame):
    """Panel para listar cuentas, desactivarlas/activarlas y resetear contraseñas."""

    def __init__(self, app: "MiCotizador") -> None:
        super().__init__(app, padding=15)
        self.app = app
        self.usuarios: dict[str, dict] = {}

        ttk.Label(self, text="Panel de administración", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(self, text=f"Sesión: {app.email_actual}", foreground="gray").grid(
            row=1, column=0, sticky="w", pady=(0, 8)
        )

        self.tabla = ttk.Treeview(
            self, columns=("email", "rol", "estado"), show="headings", height=10,
            selectmode="browse",
        )
        for col, titulo, ancho in (("email", "Email", 260), ("rol", "Rol", 80), ("estado", "Estado", 100)):
            self.tabla.heading(col, text=titulo)
            self.tabla.column(col, width=ancho, anchor="w")
        self.tabla.grid(row=2, column=0, sticky="nsew")
        barra = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        barra.grid(row=2, column=1, sticky="ns")

        botones = ttk.Frame(self)
        botones.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="w")
        ttk.Button(botones, text="Actualizar", command=self.cargar).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(botones, text="Activar / Desactivar", command=self.alternar_estado).grid(
            row=0, column=1, padx=6
        )
        ttk.Button(botones, text="Resetear contraseña", command=self.resetear).grid(
            row=0, column=2, padx=6
        )
        ttk.Button(botones, text="Abrir conversor", command=app.mostrar_conversor).grid(
            row=0, column=3, padx=6
        )
        ttk.Button(botones, text="Cerrar sesión", command=app.cerrar_sesion).grid(
            row=0, column=4, padx=(6, 0)
        )
        self.cargar()

    def _error(self, e: pb.ErrorPB) -> None:
        messagebox.showerror("Administración", str(e))
        if str(e).startswith("No tenés permisos"):
            self.app.cerrar_sesion()

    def cargar(self) -> None:
        try:
            lista = pb.listar_usuarios(self.app.token)
        except pb.ErrorPB as e:
            self._error(e)
            return
        seleccion = self.tabla.selection()
        self.tabla.delete(*self.tabla.get_children())
        self.usuarios = {u["id"]: u for u in lista}
        for u in lista:
            self.tabla.insert(
                "", "end", iid=u["id"],
                values=(u["email"], u.get("rol") or "usuario",
                        "Desactivada" if u.get("desactivado") else "Activa"),
            )
        if seleccion and seleccion[0] in self.usuarios:
            self.tabla.selection_set(seleccion[0])

    def _seleccionado(self) -> dict | None:
        sel = self.tabla.selection()
        if not sel:
            messagebox.showinfo("Administración", "Elegí una cuenta de la lista.")
            return None
        return self.usuarios[sel[0]]

    def alternar_estado(self) -> None:
        u = self._seleccionado()
        if u is None:
            return
        if u["id"] == self.app.sesion["record"]["id"]:
            messagebox.showwarning("Administración", "No podés desactivar tu propia cuenta.")
            return
        desactivar = not u.get("desactivado")
        accion = "desactivar" if desactivar else "activar"
        if not messagebox.askyesno("Administración", f"¿Querés {accion} la cuenta {u['email']}?"):
            return
        try:
            pb.cambiar_estado(self.app.token, u["id"], desactivar)
        except pb.ErrorPB as e:
            self._error(e)
            return
        self.cargar()

    def resetear(self) -> None:
        u = self._seleccionado()
        if u is None:
            return
        nueva = simpledialog.askstring(
            "Resetear contraseña",
            f"Nueva contraseña para {u['email']} (mínimo 8 caracteres):",
            show="•", parent=self,
        )
        if nueva is None:
            return
        if not 8 <= len(nueva) <= 72:
            messagebox.showerror("Administración", "La contraseña debe tener entre 8 y 72 caracteres.")
            return
        try:
            pb.resetear_password(self.app.token, u["id"], nueva)
        except pb.ErrorPB as e:
            self._error(e)
            return
        messagebox.showinfo("Administración", f"Contraseña de {u['email']} actualizada.")


class PantallaConversor(ttk.Frame):
    def __init__(self, app: "MiCotizador", usuario: str) -> None:
        super().__init__(app, padding=20)
        self.app = app
        self.usuario = usuario

        ttk.Label(self, text=f"Sesión: {usuario}", foreground="gray").grid(
            row=0, column=0, sticky="w"
        )
        barra = ttk.Frame(self)
        barra.grid(row=0, column=1, sticky="e")
        if app.es_admin:
            ttk.Button(barra, text="Panel admin", command=app.mostrar_admin).grid(
                row=0, column=0, padx=(0, 6)
            )
        ttk.Button(barra, text="Cerrar sesión", command=app.cerrar_sesion).grid(row=0, column=1)

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
        self.sesion: dict | None = None
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

    # --- sesión -------------------------------------------------------------
    @property
    def token(self) -> str:
        return self.sesion["token"] if self.sesion else ""

    @property
    def email_actual(self) -> str:
        return self.sesion["record"].get("email", "") if self.sesion else ""

    @property
    def es_admin(self) -> bool:
        r = self.sesion["record"] if self.sesion else {}
        return r.get("rol") == "admin" and not r.get("desactivado")

    def iniciar(self, datos: dict) -> None:
        """Guarda la sesión: los admins ven primero el panel, el resto el conversor."""
        self.sesion = datos
        if self.es_admin:
            self.mostrar_admin()
        else:
            self.mostrar_conversor()

    def mostrar_conversor(self) -> None:
        self._mostrar(PantallaConversor(self, self.email_actual))

    def mostrar_admin(self) -> None:
        if not self.es_admin:  # defensa extra: el servidor igualmente rechaza a los no admin
            return
        self._mostrar(PantallaAdmin(self))

    def cerrar_sesion(self) -> None:
        self.sesion = None
        self.mostrar_login()


if __name__ == "__main__":
    MiCotizador().mainloop()
