import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

from src.ui.base import VistaDashboard, crear_tabla, ejecutar, llenar_tabla, seleccionado


class TutorView(VistaDashboard):
    def __init__(self, app, usuario):
        super().__init__(app, usuario)
        self.svc = app.tutorias
        self._construir_horarios()
        self._construir_solicitudes()
        self.refrescar()

    def _construir_horarios(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Mis horarios")
        form = ttk.LabelFrame(tab, text="Publicar nuevo horario", padding=8)
        form.pack(fill="x", pady=(0, 8))
        self.materia = tk.StringVar()
        self.fecha = tk.StringVar(value=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        self.hora = tk.StringVar(value="10:00")
        ttk.Label(form, text="Materia").grid(row=0, column=0, padx=4)
        self.combo = ttk.Combobox(form, textvariable=self.materia, state="readonly", width=24)
        self.combo.grid(row=0, column=1, padx=4)
        ttk.Label(form, text="Fecha (AAAA-MM-DD)").grid(row=0, column=2, padx=4)
        ttk.Entry(form, textvariable=self.fecha, width=12).grid(row=0, column=3, padx=4)
        ttk.Label(form, text="Hora (HH:MM)").grid(row=0, column=4, padx=4)
        ttk.Entry(form, textvariable=self.hora, width=7).grid(row=0, column=5, padx=4)
        ttk.Button(form, text="Publicar", command=self.publicar).grid(row=0, column=6, padx=8)
        marco, self.tabla_h = crear_tabla(
            tab, [("materia", "Materia"), ("fecha", "Fecha"), ("hora", "Hora"), ("estado", "Estado")],
            [220, 110, 70, 100])
        marco.pack(fill="both", expand=True)
        ttk.Button(tab, text="Eliminar horario seleccionado", command=self.eliminar).pack(pady=8)

    def _construir_solicitudes(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Solicitudes")
        marco, self.tabla_c = crear_tabla(
            tab, [("estudiante", "Estudiante"), ("materia", "Materia"), ("fecha", "Fecha"),
                  ("hora", "Hora"), ("estado", "Estado"), ("calificacion", "Nota")],
            [150, 150, 100, 60, 90, 50])
        marco.pack(fill="both", expand=True)
        b = ttk.Frame(tab)
        b.pack(pady=8)
        ttk.Button(b, text="Aceptar", command=lambda: self.responder(True)).pack(side="left", padx=4)
        ttk.Button(b, text="Rechazar", command=lambda: self.responder(False)).pack(side="left", padx=4)
        ttk.Button(b, text="Marcar como realizada", command=self.realizada).pack(side="left", padx=4)

    def refrescar(self):
        self._mapa = {m["nombre"]: m["id"] for m in self.svc.listar_materias()}
        self.combo["values"] = list(self._mapa)
        if self._mapa and not self.materia.get():
            self.materia.set(next(iter(self._mapa)))
        llenar_tabla(self.tabla_h, self.svc.listar_horarios_tutor(self.usuario.id),
                     ["materia", "fecha", "hora", "estado"])
        citas = [dict(c, calificacion=c["calificacion"] or "-")
                 for c in self.svc.listar_citas_tutor(self.usuario.id)]
        llenar_tabla(self.tabla_c, citas,
                     ["estudiante", "materia", "fecha", "hora", "estado", "calificacion"])

    def publicar(self):
        ok, _ = ejecutar(self.svc.publicar_horario, self.usuario.id,
                         self._mapa.get(self.materia.get()), self.fecha.get(), self.hora.get())
        if ok:
            self.refrescar()

    def eliminar(self):
        hid = seleccionado(self.tabla_h)
        if hid and messagebox.askyesno("Confirmar", "¿Eliminar este horario?"):
            if ejecutar(self.svc.eliminar_horario, self.usuario.id, hid)[0]:
                self.refrescar()

    def responder(self, aceptar):
        cid = seleccionado(self.tabla_c)
        if cid and ejecutar(self.svc.responder_cita, self.usuario.id, cid, aceptar)[0]:
            self.refrescar()

    def realizada(self):
        cid = seleccionado(self.tabla_c)
        if cid and ejecutar(self.svc.marcar_realizada, self.usuario.id, cid)[0]:
            self.refrescar()
