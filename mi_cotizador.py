"""Mi Cotizador: convierte pesos a dólares y guarda cada conversión en historial.txt."""
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk


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
    return float(t)


def formatear(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def convertir_pesos_a_dolares(pesos: float, cotizacion: float) -> float:
    if cotizacion <= 0:
        raise ValueError("La cotización debe ser mayor que cero.")
    return pesos / cotizacion


def guardar_historial(pesos: float, cotizacion: float, dolares: float) -> None:
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = (
        f"{ahora} | ARS {formatear(pesos)} | cotización {formatear(cotizacion)} "
        f"| USD {formatear(dolares)}\n"
    )
    with open(HISTORIAL, "a", encoding="utf-8") as f:
        f.write(linea)


class MiCotizador(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mi Cotizador")
        self.resizable(False, False)

        marco = ttk.Frame(self, padding=20)
        marco.grid()

        ttk.Label(marco, text="Monto en pesos (ARS):").grid(row=0, column=0, sticky="w", pady=5)
        self.monto = ttk.Entry(marco, width=22)
        self.monto.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(marco, text="Cotización del dólar:").grid(row=1, column=0, sticky="w", pady=5)
        self.cotizacion = ttk.Entry(marco, width=22)
        self.cotizacion.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Button(marco, text="Convertir", command=self.convertir).grid(
            row=2, column=0, columnspan=2, pady=12
        )

        self.resultado = ttk.Label(marco, text="Resultado: —", font=("Segoe UI", 13, "bold"))
        self.resultado.grid(row=3, column=0, columnspan=2)

        self.bind("<Return>", lambda _e: self.convertir())
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
            guardar_historial(pesos, cotiz, dolares)
        except OSError as e:
            messagebox.showwarning("Historial", f"No se pudo guardar el historial:\n{e}")


if __name__ == "__main__":
    MiCotizador().mainloop()
