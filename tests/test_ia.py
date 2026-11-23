"""Pruebas del servicio de IA. No usan internet: el transporte HTTP se reemplaza por uno falso."""
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.data.database import Database
from src.services.auth_service import AuthService
from src.services.ia_service import (AsistenteTutorias, ClienteIA, ConfigIA, MODELO_POR_DEFECTO,
                                     URL_POR_DEFECTO, cargar_config)
from src.services.tutoria_service import TutoriaService
from src.utils.errores import ServicioIAError, ValidationError

CONFIG = ConfigIA(api_key="clave-de-prueba")
HORARIOS = [
    {"id": 1, "materia": "Cálculo", "tutor": "Laura Gómez", "fecha": "2026-11-20", "hora": "09:00",
     "promedio": 4.8, "realizadas": 5},
    {"id": 2, "materia": "Física", "tutor": "Carlos Ruiz", "fecha": "2026-11-21", "hora": "11:00",
     "promedio": None, "realizadas": 0},
    {"id": 3, "materia": "Cálculo", "tutor": "Carlos Ruiz", "fecha": "2026-11-22", "hora": "15:00",
     "promedio": 4.0, "realizadas": 2},
]


def respuesta_chat(contenido):
    return json.dumps({"choices": [{"message": {"role": "assistant", "content": contenido}}]})


class Transporte:
    """Transporte falso: devuelve respuestas en orden y guarda lo que se envió."""

    def __init__(self, *respuestas):
        self.respuestas, self.enviados = list(respuestas), []

    def __call__(self, url, cabeceras, cuerpo, timeout):
        self.enviados.append((url, cabeceras, json.loads(cuerpo), timeout))
        r = self.respuestas.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def asistente(*respuestas):
    t = Transporte(*respuestas)
    return AsistenteTutorias(ClienteIA(CONFIG, t)), t


class TestConfig(unittest.TestCase):
    def test_valores_por_defecto(self):
        c = cargar_config(Path("no-existe.env"), entorno={})
        self.assertEqual((c.base_url, c.modelo), (URL_POR_DEFECTO, MODELO_POR_DEFECTO))
        self.assertFalse(c.configurada)

    def test_lee_archivo_env_y_el_entorno_tiene_prioridad(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / ".env"
            ruta.write_text('# comentario\nIA_API_KEY="abc"\nIA_MODELO=modelo-x\nIA_TIMEOUT=45\n', encoding="utf-8")
            c = cargar_config(ruta, entorno={})
            self.assertEqual((c.api_key, c.modelo, c.timeout), ("abc", "modelo-x", 45))
            self.assertTrue(c.configurada)
            self.assertEqual(cargar_config(ruta, entorno={"IA_MODELO": "otro"}).modelo, "otro")

    def test_servicio_local_no_necesita_clave(self):
        self.assertTrue(ConfigIA(base_url="http://localhost:11434/v1").configurada)

    def test_timeout_invalido_usa_el_valor_por_defecto(self):
        self.assertEqual(cargar_config(Path("no-existe.env"), entorno={"IA_TIMEOUT": "abc"}).timeout, 30)


class TestCliente(unittest.TestCase):
    MENSAJES = [{"role": "user", "content": "hola"}]

    def test_sin_clave_no_llama_al_servicio(self):
        t = Transporte()
        with self.assertRaises(ServicioIAError) as cm:
            ClienteIA(ConfigIA(), t).completar(self.MENSAJES)
        self.assertIn("README", str(cm.exception))
        self.assertEqual(t.enviados, [])

    def test_respuesta_correcta_y_formato_de_la_peticion(self):
        t = Transporte((200, respuesta_chat("listo")))
        self.assertEqual(ClienteIA(CONFIG, t).completar(self.MENSAJES), "listo")
        url, cabeceras, cuerpo, _ = t.enviados[0]
        self.assertEqual(url, URL_POR_DEFECTO + "/chat/completions")
        self.assertEqual(cabeceras["Authorization"], "Bearer clave-de-prueba")
        self.assertEqual(cuerpo["model"], MODELO_POR_DEFECTO)
        self.assertEqual(cuerpo["response_format"], {"type": "json_object"})

    def test_errores_http_con_mensajes_claros(self):
        casos = {401: "no es válida", 403: "permiso", 404: "modelo", 429: "límite", 503: "no está disponible",
                 418: "rechazó"}
        for codigo, texto in casos.items():
            with self.subTest(codigo=codigo):
                with self.assertRaises(ServicioIAError) as cm:
                    ClienteIA(CONFIG, Transporte((codigo, "{}"))).completar(self.MENSAJES)
                self.assertIn(texto, str(cm.exception))
                self.assertNotIn("clave-de-prueba", str(cm.exception))

    def test_reintenta_sin_response_format_si_el_servicio_lo_rechaza(self):
        t = Transporte((400, "{}"), (200, respuesta_chat("{}")))
        ClienteIA(CONFIG, t).completar(self.MENSAJES)
        self.assertIn("response_format", t.enviados[0][2])
        self.assertNotIn("response_format", t.enviados[1][2])

    def test_fallos_de_red(self):
        with self.assertRaises(ServicioIAError) as cm:
            ClienteIA(CONFIG, Transporte(ConnectionError("sin red"))).completar(self.MENSAJES)
        self.assertIn("conexión", str(cm.exception))
        with self.assertRaises(ServicioIAError) as cm:
            ClienteIA(CONFIG, Transporte(TimeoutError())).completar(self.MENSAJES)
        self.assertIn("tardó", str(cm.exception))

    def test_respuestas_mal_formadas(self):
        for cuerpo in ("no es json", "{}", json.dumps({"choices": []}), respuesta_chat("   "),
                       json.dumps({"choices": [{"message": {"content": None}}]})):
            with self.subTest(cuerpo=cuerpo):
                with self.assertRaises(ServicioIAError):
                    ClienteIA(CONFIG, Transporte((200, cuerpo))).completar(self.MENSAJES)


class TestAsistente(unittest.TestCase):
    CONSULTA = "Tengo parcial de derivadas el viernes"

    def recomendar(self, contenido, horarios=HORARIOS):
        a, t = asistente((200, respuesta_chat(contenido)))
        return a.recomendar(self.CONSULTA, horarios, hoy=datetime(2026, 11, 18)), t

    def test_recomendaciones_en_el_orden_de_la_ia(self):
        r, _ = self.recomendar(json.dumps({
            "resumen": "Estos dos te sirven.",
            "recomendaciones": [{"horario_id": 3, "motivo": "Más cercano"},
                                {"horario_id": 1, "motivo": "Mejor calificado"}]}))
        self.assertEqual(r.resumen, "Estos dos te sirven.")
        self.assertEqual([(x.horario_id, x.motivo) for x in r.recomendaciones],
                         [(3, "Más cercano"), (1, "Mejor calificado")])

    def test_acepta_json_dentro_de_un_bloque_de_codigo(self):
        r, _ = self.recomendar('Claro:\n```json\n{"resumen": "ok", "recomendaciones": '
                               '[{"horario_id": 1, "motivo": "m"}]}\n```')
        self.assertEqual([x.horario_id for x in r.recomendaciones], [1])

    def test_descarta_ids_inventados_repetidos_o_invalidos(self):
        r, _ = self.recomendar(json.dumps({"resumen": "x", "recomendaciones": [
            {"horario_id": 99, "motivo": "inventado"}, {"horario_id": "1", "motivo": "texto"},
            {"horario_id": 1, "motivo": "repetido"}, {"horario_id": None}, "basura", {"motivo": "sin id"}]}))
        self.assertEqual([x.horario_id for x in r.recomendaciones], [1])

    def test_maximo_de_recomendaciones(self):
        horarios = [dict(HORARIOS[0], id=i) for i in range(1, 11)]
        r, _ = self.recomendar(json.dumps({"resumen": "x", "recomendaciones": [
            {"horario_id": i, "motivo": "m"} for i in range(1, 11)]}), horarios)
        self.assertEqual(len(r.recomendaciones), AsistenteTutorias.MAX_RECOMENDACIONES)

    def test_sin_coincidencias_y_textos_largos_o_ausentes(self):
        r, _ = self.recomendar(json.dumps({"recomendaciones": []}))
        self.assertEqual(r.recomendaciones, [])
        self.assertIn("No encontré", r.resumen)
        r, _ = self.recomendar(json.dumps({"resumen": "a" * 1000, "recomendaciones": [
            {"horario_id": 1, "motivo": "b" * 1000}]}))
        self.assertLessEqual(len(r.resumen), 400)
        self.assertLessEqual(len(r.recomendaciones[0].motivo), 220)

    def test_respuesta_que_no_es_json(self):
        with self.assertRaises(ServicioIAError):
            self.recomendar("Lo siento, no puedo ayudar.")

    def test_solo_se_envia_lo_necesario(self):
        _, t = self.recomendar(json.dumps({"resumen": "x", "recomendaciones": []}))
        mensajes = t.enviados[0][2]["messages"]
        self.assertEqual(mensajes[0]["role"], "system")
        contexto = json.loads(mensajes[1]["content"])
        self.assertEqual(contexto["consulta"], self.CONSULTA)
        self.assertEqual(contexto["hoy"], "2026-11-18")
        self.assertEqual({"id", "materia", "tutor", "fecha", "hora", "promedio", "tutorias_realizadas"},
                         set(contexto["horarios"][0]))

    def test_validacion_de_la_consulta(self):
        a, t = asistente()
        for mala in ("", "   ", "hola", "x" * 601, None):
            with self.subTest(consulta=mala):
                with self.assertRaises(ValidationError):
                    a.recomendar(mala, HORARIOS)
        self.assertEqual(t.enviados, [])

    def test_sin_horarios_no_consulta_a_la_ia(self):
        a, t = asistente()
        r = a.recomendar(self.CONSULTA, [])
        self.assertEqual(r.recomendaciones, [])
        self.assertEqual(t.enviados, [])


class TestHorariosConCalificacion(unittest.TestCase):
    def test_incluye_promedio_y_realizadas_del_tutor(self):
        db = Database(":memory:")
        auth, svc = AuthService(db), TutoriaService(db)
        tutor = auth.registrar("Laura Gómez", "laura@mail.com", "secreto1", "tutor")
        est = auth.registrar("Santiago Pérez", "san@mail.com", "secreto1", "estudiante")
        mat = svc.crear_materia("Cálculo")
        ahora = datetime(2026, 1, 1, 8, 0)
        h1 = svc.publicar_horario(tutor.id, mat, "2026-01-05", "10:00", ahora)
        svc.publicar_horario(tutor.id, mat, "2026-01-06", "10:00", ahora)
        cita = svc.agendar_cita(est.id, h1)
        svc.responder_cita(tutor.id, cita, True)
        svc.marcar_realizada(tutor.id, cita)
        svc.calificar(est.id, cita, 5, "Muy claro")
        filas = svc.listar_horarios_con_calificacion(hoy=ahora)
        self.assertEqual(len(filas), 1)  # el horario ya realizado no está libre
        self.assertEqual((filas[0]["promedio"], filas[0]["realizadas"]), (5.0, 1))
        db.cerrar()


if __name__ == "__main__":
    unittest.main()
