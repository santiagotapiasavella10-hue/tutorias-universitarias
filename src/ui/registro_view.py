import tkinter as tk
from tkinter import messagebox, ttk

from src.ui.base import ejecutar


class RegistroView(ttk.Frame):
    def __init__(self, app):
        super().__init__(app.contenedor, padding=30)
        self.app = app
        ttk.Label(self, text="Crear cuenta", font=("Segoe UI", 18, "bold")).pack(pady=(10, 20))
        self.nombre, self.correo = tk.StringVar(), tk.StringVar()
        self.password, self.rol = tk.StringVar(), tk.StringVar(value="estudiante")
        form = ttk.Frame(self)
        form.pack()
        campos = [("Nombre completo", self.nombre, ""), ("Correo", self.correo, ""),
                  ("Contraseña (mín. 6)", self.password, "•")]
        for i, (txt, var, mask) in enumerate(campos):
            ttk.Label(form, text=txt).grid(row=i, column=0, sticky="w", pady=4)
            ttk.Entry(form, textvariable=var, show=mask, width=32).grid(row=i, column=1, pady=4, padx=8)
        ttk.Label(form, text="Rol").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Combobox(form, textvariable=self.rol, values=["estudiante", "tutor"],
                     state="readonly", width=29).grid(row=3, column=1, pady=4, padx=8)
        ttk.Button(self, text="Registrarme", command=self.registrar).pack(pady=(16, 4))
        ttk.Button(self, text="Volver al inicio de sesión", command=lambda: app.mostrar("login")).pack()

    def registrar(self):
        ok, _ = ejecutar(self.app.auth.registrar, self.nombre.get(), self.correo.get(),
                         self.password.get(), self.rol.get())
        if ok:
            messagebox.showinfo("Cuenta creada", "Ya puedes iniciar sesión.")
            self.app.mostrar("login")
