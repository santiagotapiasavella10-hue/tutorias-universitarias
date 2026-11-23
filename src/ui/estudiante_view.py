import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from src.ui.base import VistaDashboard, crear_tabla, ejecutar, en_segundo_plano, llenar_tabla, seleccionado


class EstudianteView(VistaDashboard):
    def __init__(self, app, usuario):
        super().__init__(app, usuario)
        self.svc, self.ia = app.tutorias, app.ia
        self._motivos = {}
        self._consultando = False
        self._construir_buscar()
        self._construir_asistente()
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

    # --- Pestaña: asistente de IA ---
    def _construir_asistente(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Asistente de IA")
        caja = ttk.LabelFrame(tab, text="¿Qué necesitas estudiar?", padding=8)
        caja.pack(fill="x")
        self.texto_ia = tk.Text(caja, height=3, wrap="word", font=("Segoe UI", 10))
        self.texto_ia.pack(fill="x")
        ttk.Label(caja, foreground="#777",
                  text="Ejemplo: tengo parcial de derivadas el viernes y no entiendo la regla de la cadena."
                  ).pack(anchor="w", pady=(4, 0))
        fila = ttk.Frame(caja)
        fila.pack(fill="x", pady=(8, 0))
        self.btn_pedir = ttk.Button(fila, text="Pedir recomendación", command=self.pedir_recomendacion)
        self.btn_pedir.pack(side="left")
        self.estado_ia = ttk.Label(fila, foreground="#555",
                                   text="" if self.ia.configurado else
                                   "Falta configurar la clave de IA (ver README, sección «Servicio de IA»).")
        self.estado_ia.pack(side="left", padx=10)

        self.resumen_ia = ttk.Label(tab, wraplength=680, justify="left")
        self.resumen_ia.pack(anchor="w", pady=8)
        marco, self.tabla_ia = crear_tabla(
            tab, [("materia", "Materia"), ("tutor", "Tutor"), ("fecha", "Fecha"),
                  ("hora", "Hora"), ("promedio", "Nota del tutor")],
            [180, 160, 100, 70, 110], alto=5)
        marco.pack(fill="both", expand=True)
        self.tabla_ia.bind("<<TreeviewSelect>>", self._mostrar_motivo)
        self.motivo_ia = ttk.Label(tab, wraplength=680, justify="left", foreground="#555")
        self.motivo_ia.pack(anchor="w", pady=6)
        ttk.Button(tab, text="Agendar tutoría seleccionada", command=self.agendar_recomendada).pack(pady=4)

    def pedir_recomendacion(self):
        if self._consultando:
            return
        ok, consulta = ejecutar(self.ia.validar_consulta, self.texto_ia.get("1.0", "end"))
        if not ok:
            return
        horarios = self.svc.listar_horarios_con_calificacion()  # la base se lee en este hilo
        self._consultando = True
        self.btn_pedir.state(["disabled"])
        self.estado_ia.config(text="Consultando al asistente…")
        self.resumen_ia.config(text="")
        en_segundo_plano(self, lambda: self.ia.recomendar(consulta, horarios),
                         lambda ok, res: self._mostrar_recomendacion(ok, res, horarios))

    def _mostrar_recomendacion(self, ok, resultado, horarios):
        self._consultando = False
        self.btn_pedir.state(["!disabled"])
        self.estado_ia.config(text="")
        if not ok:
            self.estado_ia.config(text="No se pudo obtener la recomendación.")
            messagebox.showwarning("Asistente de IA", resultado)
            return
        por_id = {h["id"]: h for h in horarios}
        filas, self._motivos = [], {}
        for r in resultado.recomendaciones:
            h = dict(por_id[r.horario_id])
            h["promedio"] = h["promedio"] if h["promedio"] else "Sin notas"
            filas.append(h)
            self._motivos[str(h["id"])] = r.motivo
        self.resumen_ia.config(text=resultado.resumen)
        self.motivo_ia.config(text="Selecciona un horario para ver por qué se recomienda." if filas else "")
        llenar_tabla(self.tabla_ia, filas, ["materia", "tutor", "fecha", "hora", "promedio"])

    def _mostrar_motivo(self, _evento=None):
        sel = self.tabla_ia.selection()
        if sel:
            self.motivo_ia.config(text=f"Por qué: {self._motivos.get(sel[0], '')}")

    def agendar_recomendada(self):
        hid = seleccionado(self.tabla_ia)
        if hid and ejecutar(self.svc.agendar_cita, self.usuario.id, hid)[0]:
            messagebox.showinfo("Solicitud enviada", "El tutor debe aceptar tu solicitud.")
            self.tabla_ia.delete(*self.tabla_ia.get_children())  # ese horario ya no está libre
            self.resumen_ia.config(text="")
            self.motivo_ia.config(text="")
            self.refrescar()

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
