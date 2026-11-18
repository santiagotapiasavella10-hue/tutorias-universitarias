import tkinter as tk
from tkinter import ttk

from src.ui.base import VistaDashboard, crear_tabla, ejecutar, llenar_tabla


class AdminView(VistaDashboard):
    def __init__(self, app, usuario):
        super().__init__(app, usuario)
        self.svc = app.tutorias
        self._construir_stats()
        self._construir_materias()
        self.refrescar()

    def _construir_stats(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Estadísticas")
        self.resumen = ttk.Label(tab, justify="left", font=("Segoe UI", 11))
        self.resumen.pack(anchor="w", pady=(0, 10))
        ttk.Label(tab, text="Ranking de tutores", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        marco, self.tabla_r = crear_tabla(
            tab, [("tutor", "Tutor"), ("citas", "Tutorías realizadas"), ("promedio", "Promedio")],
            [200, 150, 100], alto=8)
        marco.pack(fill="both", expand=True)
        ttk.Button(tab, text="Actualizar", command=self.refrescar).pack(pady=8)

    def _construir_materias(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Materias")
        form = ttk.Frame(tab)
        form.pack(fill="x", pady=(0, 8))
        self.nueva = tk.StringVar()
        ttk.Label(form, text="Nueva materia:").pack(side="left")
        ttk.Entry(form, textvariable=self.nueva, width=30).pack(side="left", padx=6)
        ttk.Button(form, text="Agregar", command=self.agregar).pack(side="left")
        marco, self.tabla_m = crear_tabla(tab, [("nombre", "Materia")], [300])
        marco.pack(fill="both", expand=True)

    def refrescar(self):
        s = self.svc.estadisticas()
        roles, estados = s["usuarios_por_rol"], s["citas_por_estado"]
        self.resumen.config(text=(
            f"Estudiantes: {roles.get('estudiante', 0)}   Tutores: {roles.get('tutor', 0)}\n"
            f"Total de citas: {s['total_citas']}\n"
            + "   ".join(f"{k}: {v}" for k, v in estados.items())))
        self.tabla_r.delete(*self.tabla_r.get_children())
        for i, r in enumerate(s["ranking_tutores"]):
            self.tabla_r.insert("", "end", iid=str(i),
                                values=(r["tutor"], r["citas"], r["promedio"] or "-"))
        llenar_tabla(self.tabla_m, self.svc.listar_materias(), ["nombre"])

    def agregar(self):
        if ejecutar(self.svc.crear_materia, self.nueva.get())[0]:
            self.nueva.set("")
            self.refrescar()
