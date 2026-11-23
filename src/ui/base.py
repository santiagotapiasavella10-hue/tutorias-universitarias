"""Componentes de interfaz reutilizables."""
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from src.utils.errores import AppError


def ejecutar(accion, *args, **kwargs):
    """Ejecuta una acción del servicio mostrando los errores al usuario.
    Devuelve (ok, resultado)."""
    try:
        return True, accion(*args, **kwargs)
    except AppError as e:
        messagebox.showwarning("Atención", str(e))
    except Exception as e:  # error inesperado: no cerrar la app
        messagebox.showerror("Error inesperado", str(e))
    return False, None


def en_segundo_plano(widget, trabajo, al_terminar):
    """Ejecuta trabajo() en otro hilo para no congelar la ventana y llama a
    al_terminar(ok, resultado) en el hilo de la interfaz. Si falla, resultado es el mensaje.
    Dentro de trabajo() no se debe usar la base de datos ni ningún widget."""
    cola = queue.Queue()

    def correr():
        try:
            cola.put((True, trabajo()))
        except AppError as e:
            cola.put((False, str(e)))
        except Exception as e:  # error inesperado: no cerrar la app
            cola.put((False, f"Error inesperado: {e}"))

    def revisar():
        try:
            ok, resultado = cola.get_nowait()
        except queue.Empty:
            try:
                widget.after(100, revisar)
            except tk.TclError:  # la vista se cerró mientras esperaba
                pass
            return
        try:
            if widget.winfo_exists():
                al_terminar(ok, resultado)
        except tk.TclError:
            pass

    threading.Thread(target=correr, daemon=True).start()
    widget.after(100, revisar)


def crear_tabla(padre, columnas, anchos=None, alto=10):
    """Treeview con scrollbar. columnas: lista de (clave, título)."""
    marco = ttk.Frame(padre)
    tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings",
                         height=alto, selectmode="browse")
    for i, (clave, titulo) in enumerate(columnas):
        tabla.heading(clave, text=titulo)
        tabla.column(clave, width=(anchos[i] if anchos else 120), anchor="w")
    barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return marco, tabla


def llenar_tabla(tabla, filas, claves):
    tabla.delete(*tabla.get_children())
    for fila in filas:
        tabla.insert("", "end", iid=str(fila["id"]), values=[fila[k] for k in claves])


def seleccionado(tabla):
    """Devuelve el id (int) de la fila seleccionada o None con aviso."""
    sel = tabla.selection()
    if not sel:
        messagebox.showinfo("Selecciona una fila", "Primero selecciona un elemento de la tabla.")
        return None
    return int(sel[0])


class VistaDashboard(ttk.Frame):
    """Base de los paneles por rol: encabezado con usuario y botón de cerrar sesión."""

    def __init__(self, app, usuario):
        super().__init__(app.contenedor, padding=10)
        self.app, self.usuario = app, usuario
        cab = ttk.Frame(self)
        cab.pack(fill="x", pady=(0, 8))
        ttk.Label(cab, text=f"Hola, {usuario.nombre}", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(cab, text="Cerrar sesión", command=app.cerrar_sesion).pack(side="right")
        ttk.Label(self, text=usuario.descripcion_rol(), foreground="#555").pack(anchor="w")
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, pady=8)
