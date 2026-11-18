import tkinter as tk
from tkinter import ttk

from src.ui.base import ejecutar


class LoginView(ttk.Frame):
    def __init__(self, app):
        super().__init__(app.contenedor, padding=30)
        self.app = app
        ttk.Label(self, text="Gestor de Tutorías Universitarias",
                  font=("Segoe UI", 18, "bold")).pack(pady=(10, 4))
        ttk.Label(self, text="Inicia sesión para continuar", foreground="#555").pack(pady=(0, 20))

        self.correo = tk.StringVar()
        self.password = tk.StringVar()
        form = ttk.Frame(self)
        form.pack()
        ttk.Label(form, text="Correo").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.correo, width=32).grid(row=0, column=1, pady=4, padx=8)
        ttk.Label(form, text="Contraseña").grid(row=1, column=0, sticky="w", pady=4)
        e = ttk.Entry(form, textvariable=self.password, show="•", width=32)
        e.grid(row=1, column=1, pady=4, padx=8)
        e.bind("<Return>", lambda _: self.ingresar())

        ttk.Button(self, text="Ingresar", command=self.ingresar).pack(pady=(16, 4))
        ttk.Button(self, text="Crear cuenta", command=lambda: app.mostrar("registro")).pack()
        ttk.Label(self, foreground="#777", justify="center",
                  text="Cuentas de prueba:\nadmin@tutorias.com / admin123\n"
                       "laura@tutorias.com / tutor123\nsantiago@tutorias.com / estudiante123"
                  ).pack(pady=(24, 0))

    def ingresar(self):
        ok, usuario = ejecutar(self.app.auth.iniciar_sesion, self.correo.get(), self.password.get())
        if ok:
            self.app.abrir_dashboard(usuario)
