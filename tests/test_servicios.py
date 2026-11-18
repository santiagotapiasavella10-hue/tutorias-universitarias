import unittest
from datetime import datetime

from src.data.database import Database
from src.services.auth_service import AuthService
from src.services.tutoria_service import TutoriaService
from src.utils.errores import ReglaNegocioError, ValidationError

AHORA = datetime(2026, 1, 1, 8, 0)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.auth = AuthService(self.db)
        self.svc = TutoriaService(self.db)
        self.tutor = self.auth.registrar("Laura Gómez", "laura@mail.com", "secreto1", "tutor")
        self.est = self.auth.registrar("Santiago Pérez", "san@mail.com", "secreto1", "estudiante")
        self.est2 = self.auth.registrar("Ana Torres", "ana@mail.com", "secreto1", "estudiante")
        self.mat = self.svc.crear_materia("Cálculo")
        self.mat2 = self.svc.crear_materia("Física")

    def horario(self, fecha="2026-01-05", hora="10:00", materia=None):
        return self.svc.publicar_horario(self.tutor.id, materia or self.mat, fecha, hora, AHORA)

    def tearDown(self):
        self.db.cerrar()


class TestAuth(BaseTest):
    def test_login_correcto_e_incorrecto(self):
        u = self.auth.iniciar_sesion("laura@mail.com", "secreto1")
        self.assertEqual(u.rol, "tutor")
        with self.assertRaises(ReglaNegocioError):
            self.auth.iniciar_sesion("laura@mail.com", "otra")

    def test_correo_duplicado(self):
        with self.assertRaises(ReglaNegocioError):
            self.auth.registrar("Otra Laura", "laura@mail.com", "secreto1", "estudiante")

    def test_no_se_puede_registrar_admin_desde_ui(self):
        with self.assertRaises(ValidationError):
            self.auth.registrar("Falso Admin", "fa@mail.com", "secreto1", "admin")

    def test_password_no_se_guarda_en_claro(self):
        fila = self.db.conn.execute("SELECT password_hash FROM usuarios WHERE correo='laura@mail.com'").fetchone()
        self.assertNotIn("secreto1", fila["password_hash"])


class TestHorarios(BaseTest):
    def test_horario_duplicado(self):
        self.horario()
        with self.assertRaises(ReglaNegocioError):
            self.horario()

    def test_horario_en_el_pasado(self):
        with self.assertRaises(ValidationError):
            self.svc.publicar_horario(self.tutor.id, self.mat, "2025-12-01", "10:00", AHORA)

    def test_no_eliminar_horario_reservado(self):
        h = self.horario()
        self.svc.agendar_cita(self.est.id, h)
        with self.assertRaises(ReglaNegocioError):
            self.svc.eliminar_horario(self.tutor.id, h)

    def test_materia_duplicada(self):
        with self.assertRaises(ReglaNegocioError):
            self.svc.crear_materia("Cálculo")


class TestCitas(BaseTest):
    def test_flujo_completo(self):
        h = self.horario()
        cid = self.svc.agendar_cita(self.est.id, h)
        self.svc.responder_cita(self.tutor.id, cid, True)
        self.svc.marcar_realizada(self.tutor.id, cid)
        self.svc.calificar(self.est.id, cid, 5, "Excelente")
        stats = self.svc.estadisticas()
        self.assertEqual(stats["citas_por_estado"], {"realizada": 1})
        self.assertEqual(stats["ranking_tutores"][0]["promedio"], 5.0)

    def test_horario_reservado_no_aparece_disponible(self):
        h = self.horario()
        self.assertEqual(len(self.svc.listar_horarios_disponibles(hoy=AHORA)), 1)
        self.svc.agendar_cita(self.est.id, h)
        self.assertEqual(len(self.svc.listar_horarios_disponibles(hoy=AHORA)), 0)

    def test_dos_estudiantes_mismo_horario(self):
        h = self.horario()
        self.svc.agendar_cita(self.est.id, h)
        with self.assertRaises(ReglaNegocioError):
            self.svc.agendar_cita(self.est2.id, h)

    def test_cruce_de_horarios_del_estudiante(self):
        otro_tutor = self.auth.registrar("Carlos Ruiz", "c@mail.com", "secreto1", "tutor")
        h1 = self.horario()
        h2 = self.svc.publicar_horario(otro_tutor.id, self.mat2, "2026-01-05", "10:00", AHORA)
        self.svc.agendar_cita(self.est.id, h1)
        with self.assertRaises(ReglaNegocioError):
            self.svc.agendar_cita(self.est.id, h2)

    def test_cancelar_libera_el_horario(self):
        h = self.horario()
        cid = self.svc.agendar_cita(self.est.id, h)
        self.svc.cancelar_cita(self.est.id, cid)
        self.svc.agendar_cita(self.est2.id, h)  # ya no falla

    def test_rechazada_libera_el_horario(self):
        h = self.horario()
        cid = self.svc.agendar_cita(self.est.id, h)
        self.svc.responder_cita(self.tutor.id, cid, False)
        self.svc.agendar_cita(self.est2.id, h)

    def test_no_calificar_antes_de_realizar_ni_dos_veces(self):
        cid = self.svc.agendar_cita(self.est.id, self.horario())
        with self.assertRaises(ReglaNegocioError):
            self.svc.calificar(self.est.id, cid, 4)
        self.svc.responder_cita(self.tutor.id, cid, True)
        self.svc.marcar_realizada(self.tutor.id, cid)
        self.svc.calificar(self.est.id, cid, 4)
        with self.assertRaises(ReglaNegocioError):
            self.svc.calificar(self.est.id, cid, 5)

    def test_otro_estudiante_no_puede_cancelar(self):
        cid = self.svc.agendar_cita(self.est.id, self.horario())
        with self.assertRaises(ReglaNegocioError):
            self.svc.cancelar_cita(self.est2.id, cid)


if __name__ == "__main__":
    unittest.main()
