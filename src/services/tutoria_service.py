"""Lógica de negocio: materias, horarios, citas, calificaciones y estadísticas."""
import sqlite3
from datetime import datetime

from src.data.database import Database
from src.utils.errores import ReglaNegocioError, ValidationError
from src.utils.validaciones import (
    validar_calificacion,
    validar_fecha_hora,
    validar_nombre_materia,
)

ESTADOS_VIGENTES = ("pendiente", "aceptada", "realizada")


class TutoriaService:
    def __init__(self, db: Database):
        self.db = db

    # ---------- Materias ----------
    def listar_materias(self):
        return self.db.conn.execute("SELECT id, nombre FROM materias ORDER BY nombre").fetchall()

    def crear_materia(self, nombre: str) -> int:
        nombre = validar_nombre_materia(nombre)
        try:
            cur = self.db.conn.execute("INSERT INTO materias (nombre) VALUES (?)", (nombre,))
            self.db.conn.commit()
        except sqlite3.IntegrityError:
            raise ReglaNegocioError("Esa materia ya existe.")
        return cur.lastrowid

    # ---------- Horarios (tutor) ----------
    def publicar_horario(self, tutor_id, materia_id, fecha, hora, ahora=None) -> int:
        if not materia_id:
            raise ValidationError("Seleccione una materia.")
        fecha, hora = validar_fecha_hora(fecha, hora, ahora)
        try:
            cur = self.db.conn.execute(
                "INSERT INTO horarios (tutor_id, materia_id, fecha, hora) VALUES (?,?,?,?)",
                (tutor_id, materia_id, fecha, hora),
            )
            self.db.conn.commit()
        except sqlite3.IntegrityError:
            raise ReglaNegocioError("Ya publicaste un horario en esa fecha y hora.")
        return cur.lastrowid

    def listar_horarios_tutor(self, tutor_id):
        return self.db.conn.execute(
            """SELECT h.id, m.nombre AS materia, h.fecha, h.hora,
                      CASE WHEN EXISTS (SELECT 1 FROM citas c WHERE c.horario_id = h.id
                                        AND c.estado IN ('pendiente','aceptada','realizada'))
                           THEN 'Reservado' ELSE 'Libre' END AS estado
               FROM horarios h JOIN materias m ON m.id = h.materia_id
               WHERE h.tutor_id = ? ORDER BY h.fecha, h.hora""",
            (tutor_id,),
        ).fetchall()

    def eliminar_horario(self, tutor_id, horario_id):
        fila = self.db.conn.execute(
            "SELECT tutor_id FROM horarios WHERE id = ?", (horario_id,)
        ).fetchone()
        if fila is None or fila["tutor_id"] != tutor_id:
            raise ReglaNegocioError("Horario no encontrado.")
        vigente = self.db.conn.execute(
            "SELECT 1 FROM citas WHERE horario_id = ? AND estado IN ('pendiente','aceptada','realizada')",
            (horario_id,),
        ).fetchone()
        if vigente:
            raise ReglaNegocioError("No puedes eliminar un horario que ya tiene una cita.")
        self.db.conn.execute("DELETE FROM citas WHERE horario_id = ?", (horario_id,))
        self.db.conn.execute("DELETE FROM horarios WHERE id = ?", (horario_id,))
        self.db.conn.commit()

    # ---------- Búsqueda (estudiante) ----------
    def listar_horarios_disponibles(self, materia_id=None, hoy=None):
        hoy = (hoy or datetime.now()).strftime("%Y-%m-%d")
        sql = """SELECT h.id, m.nombre AS materia, u.nombre AS tutor, h.fecha, h.hora
                 FROM horarios h
                 JOIN materias m ON m.id = h.materia_id
                 JOIN usuarios u ON u.id = h.tutor_id
                 WHERE h.fecha >= ?
                   AND NOT EXISTS (SELECT 1 FROM citas c WHERE c.horario_id = h.id
                                   AND c.estado IN ('pendiente','aceptada','realizada'))"""
        params = [hoy]
        if materia_id:
            sql += " AND h.materia_id = ?"
            params.append(materia_id)
        sql += " ORDER BY h.fecha, h.hora"
        return self.db.conn.execute(sql, params).fetchall()

    # ---------- Citas ----------
    def agendar_cita(self, estudiante_id, horario_id) -> int:
        horario = self.db.conn.execute(
            "SELECT * FROM horarios WHERE id = ?", (horario_id,)
        ).fetchone()
        if horario is None:
            raise ReglaNegocioError("El horario seleccionado no existe.")
        if horario["tutor_id"] == estudiante_id:
            raise ReglaNegocioError("No puedes agendar una cita contigo mismo.")
        cruce = self.db.conn.execute(
            """SELECT 1 FROM citas c JOIN horarios h ON h.id = c.horario_id
               WHERE c.estudiante_id = ? AND h.fecha = ? AND h.hora = ?
                 AND c.estado IN ('pendiente','aceptada','realizada')""",
            (estudiante_id, horario["fecha"], horario["hora"]),
        ).fetchone()
        if cruce:
            raise ReglaNegocioError("Ya tienes una cita en ese mismo día y hora.")
        try:
            cur = self.db.conn.execute(
                "INSERT INTO citas (horario_id, estudiante_id) VALUES (?, ?)",
                (horario_id, estudiante_id),
            )
            self.db.conn.commit()
        except sqlite3.IntegrityError:
            raise ReglaNegocioError("Ese horario ya fue reservado por otro estudiante.")
        return cur.lastrowid

    _SQL_CITAS = """SELECT c.id, m.nombre AS materia, h.fecha, h.hora, c.estado,
                           c.calificacion, c.comentario,
                           t.nombre AS tutor, e.nombre AS estudiante
                    FROM citas c
                    JOIN horarios h ON h.id = c.horario_id
                    JOIN materias m ON m.id = h.materia_id
                    JOIN usuarios t ON t.id = h.tutor_id
                    JOIN usuarios e ON e.id = c.estudiante_id"""

    def listar_citas_estudiante(self, estudiante_id):
        return self.db.conn.execute(
            self._SQL_CITAS + " WHERE c.estudiante_id = ? ORDER BY h.fecha DESC, h.hora DESC",
            (estudiante_id,),
        ).fetchall()

    def listar_citas_tutor(self, tutor_id):
        return self.db.conn.execute(
            self._SQL_CITAS + " WHERE h.tutor_id = ? ORDER BY h.fecha DESC, h.hora DESC",
            (tutor_id,),
        ).fetchall()

    def _cita(self, cita_id):
        fila = self.db.conn.execute(
            """SELECT c.*, h.tutor_id FROM citas c JOIN horarios h ON h.id = c.horario_id
               WHERE c.id = ?""",
            (cita_id,),
        ).fetchone()
        if fila is None:
            raise ReglaNegocioError("La cita no existe.")
        return fila

    def _cambiar_estado(self, cita_id, estado):
        self.db.conn.execute("UPDATE citas SET estado = ? WHERE id = ?", (estado, cita_id))
        self.db.conn.commit()

    def responder_cita(self, tutor_id, cita_id, aceptar: bool):
        cita = self._cita(cita_id)
        if cita["tutor_id"] != tutor_id:
            raise ReglaNegocioError("Esta cita no pertenece a tus horarios.")
        if cita["estado"] != "pendiente":
            raise ReglaNegocioError("Solo se pueden responder citas pendientes.")
        self._cambiar_estado(cita_id, "aceptada" if aceptar else "rechazada")

    def marcar_realizada(self, tutor_id, cita_id):
        cita = self._cita(cita_id)
        if cita["tutor_id"] != tutor_id:
            raise ReglaNegocioError("Esta cita no pertenece a tus horarios.")
        if cita["estado"] != "aceptada":
            raise ReglaNegocioError("Solo se puede marcar como realizada una cita aceptada.")
        self._cambiar_estado(cita_id, "realizada")

    def cancelar_cita(self, estudiante_id, cita_id):
        cita = self._cita(cita_id)
        if cita["estudiante_id"] != estudiante_id:
            raise ReglaNegocioError("Esta cita no es tuya.")
        if cita["estado"] not in ("pendiente", "aceptada"):
            raise ReglaNegocioError("Solo se pueden cancelar citas pendientes o aceptadas.")
        self._cambiar_estado(cita_id, "cancelada")

    def calificar(self, estudiante_id, cita_id, puntaje, comentario=""):
        puntaje = validar_calificacion(puntaje)
        cita = self._cita(cita_id)
        if cita["estudiante_id"] != estudiante_id:
            raise ReglaNegocioError("Esta cita no es tuya.")
        if cita["estado"] != "realizada":
            raise ReglaNegocioError("Solo puedes calificar tutorías ya realizadas.")
        if cita["calificacion"] is not None:
            raise ReglaNegocioError("Esta tutoría ya fue calificada.")
        self.db.conn.execute(
            "UPDATE citas SET calificacion = ?, comentario = ? WHERE id = ?",
            (puntaje, (comentario or "").strip(), cita_id),
        )
        self.db.conn.commit()

    # ---------- Estadísticas (admin) ----------
    def estadisticas(self) -> dict:
        q = self.db.conn.execute
        por_rol = {r["rol"]: r["n"] for r in q("SELECT rol, COUNT(*) AS n FROM usuarios GROUP BY rol")}
        por_estado = {r["estado"]: r["n"] for r in q("SELECT estado, COUNT(*) AS n FROM citas GROUP BY estado")}
        ranking = q(
            """SELECT t.nombre AS tutor, COUNT(c.id) AS citas,
                      ROUND(AVG(c.calificacion), 2) AS promedio
               FROM usuarios t
               JOIN horarios h ON h.tutor_id = t.id
               LEFT JOIN citas c ON c.horario_id = h.id AND c.estado = 'realizada'
               WHERE t.rol = 'tutor' GROUP BY t.id ORDER BY citas DESC, t.nombre"""
        ).fetchall()
        return {
            "usuarios_por_rol": por_rol,
            "citas_por_estado": por_estado,
            "total_citas": sum(por_estado.values()),
            "ranking_tutores": [dict(r) for r in ranking],
        }
