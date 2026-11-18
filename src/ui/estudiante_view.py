import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from src.ui.base import VistaDashboard, crear_tabla, ejecutar, llenar_tabla, seleccionado


class EstudianteView(VistaDashboard):
    def __init__(self, app, usuario):
        super().__init__(app, usuario)
        self.svc = app.tutorias
        self._construir_buscar()
        self._construir_mis_citas()
        self.refrescar()

    # --- Pestaña: buscar tutorías ---
    def _construir_buscar(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Buscar tutorías")
        barra = ttk.Frame(tab)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Materia:").pack(side="left")
        self.filtro = tk.StringVar(value="Todas")
        self.combo = ttk.Combobox(barra, textvariable=self.filtro, state="readonly", width=28)
        self.combo.pack(side="left", padx=6)
        self.combo.bind("<<ComboboxSelected>>", lambda _: self.refrescar())
        marco, self.tabla_disp = crear_tabla(
            tab, [("materia", "Materia"), ("tutor", "Tutor"), ("fecha", "Fecha"), ("hora", "Hora")],
            [200, 180, 110, 70])
        marco.pack(fill="both", expand=True)
        ttk.Button(tab, text="Agendar tutoría seleccionada", command=self.agendar).pack(pady=8)

    # --- Pestaña: mis citas ---
    def _construir_mis_citas(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Mis citas")
        marco, self.tabla_citas = crear_tabla(
            tab, [("materia", "Materia"), ("tutor", "Tutor"), ("fecha", "Fecha"),
                  ("hora", "Hora"), ("estado", "Estado"), ("calificacion", "Nota")],
            [160, 140, 100, 60, 90, 50])
        marco.pack(fill="both", expand=True)
        botones = ttk.Frame(tab)
        botones.pack(pady=8)
        ttk.Button(botones, text="Cancelar cita", command=self.cancelar).pack(side="left", padx=4)
        ttk.Button(botones, text="Calificar tutoría", command=self.calificar).pack(side="left", padx=4)

    def refrescar(self):
        materias = self.svc.listar_materias()
        self._mapa = {m["nombre"]: m["id"] for m in materias}
        self.combo["values"] = ["Todas"] + list(self._mapa)
        materia_id = self._mapa.get(self.filtro.get())
        llenar_tabla(self.tabla_disp, self.svc.listar_horarios_disponibles(materia_id),
                     ["materia", "tutor", "fecha", "hora"])
        citas = [dict(c, calificacion=c["calificacion"] or "-")
                 for c in self.svc.listar_citas_estudiante(self.usuario.id)]
        llenar_tabla(self.tabla_citas, citas,
                     ["materia", "tutor", "fecha", "hora", "estado", "calificacion"])

    def agendar(self):
        hid = seleccionado(self.tabla_disp)
        if hid and ejecutar(self.svc.agendar_cita, self.usuario.id, hid)[0]:
            messagebox.showinfo("Solicitud enviada", "El tutor debe aceptar tu solicitud.")
            self.refrescar()

    def cancelar(self):
        cid = seleccionado(self.tabla_citas)
        if cid and messagebox.askyesno("Confirmar", "¿Cancelar esta cita?"):
            if ejecutar(self.svc.cancelar_cita, self.usuario.id, cid)[0]:
                self.refrescar()

    def calificar(self):
        cid = seleccionado(self.tabla_citas)
        if not cid:
            return
        puntaje = simpledialog.askinteger("Calificar", "Puntaje de 1 a 5:", minvalue=1, maxvalue=5)
        if puntaje is None:
            return
        comentario = simpledialog.askstring("Calificar", "Comentario (opcional):") or ""
        if ejecutar(self.svc.calificar, self.usuario.id, cid, puntaje, comentario)[0]:
            messagebox.showinfo("Gracias", "Tu calificación fue registrada.")
            self.refrescar()
