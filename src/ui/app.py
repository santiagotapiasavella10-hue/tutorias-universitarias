"""Ventana principal y navegación entre vistas."""
import tkinter as tk
from tkinter import ttk

from src.data.database import Database
from src.services.auth_service import AuthService
from src.services.ia_service import AsistenteTutorias, ClienteIA, cargar_config
from src.services.tutoria_service import TutoriaService
from src.ui.admin_view import AdminView
from src.ui.estudiante_view import EstudianteView
from src.ui.login_view import LoginView
from src.ui.registro_view import RegistroView
from src.ui.tutor_view import TutorView

DASHBOARDS = {"estudiante": EstudianteView, "tutor": TutorView, "admin": AdminView}


class App(tk.Tk):
    def __init__(self, db: Database):
        super().__init__()
        self.title("Gestor de Tutorías Universitarias")
        self.geometry("860x560")
        self.minsize(760, 500)
        ttk.Style(self).theme_use("clam")
        self.auth, self.tutorias = AuthService(db), TutoriaService(db)
        self.ia = AsistenteTutorias(ClienteIA(cargar_config()))
        self.contenedor = ttk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)
        self._vista = None
        self.mostrar("login")

    def _reemplazar(self, vista):
        if self._vista is not None:
            self._vista.destroy()
        self._vista = vista
        vista.pack(fill="both", expand=True)

    def mostrar(self, nombre: str):
        vistas = {"login": LoginView, "registro": RegistroView}
        self._reemplazar(vistas[nombre](self))

    def abrir_dashboard(self, usuario):
        self._reemplazar(DASHBOARDS[usuario.rol](self, usuario))

    def cerrar_sesion(self):
        self.mostrar("login")
