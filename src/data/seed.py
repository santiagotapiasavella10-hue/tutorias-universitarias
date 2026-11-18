"""Datos de ejemplo para demostrar el prototipo."""
from datetime import datetime, timedelta

from src.data.database import Database
from src.services.auth_service import AuthService
from src.services.tutoria_service import TutoriaService


def cargar_datos_ejemplo(db: Database) -> bool:
    """Inserta datos de ejemplo solo si la base está vacía. Devuelve True si cargó."""
    if db.conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] > 0:
        return False
    auth, tut = AuthService(db), TutoriaService(db)

    auth.registrar("Administrador", "admin@tutorias.com", "admin123", "admin", permitir_admin=True)
    t1 = auth.registrar("Laura Gómez", "laura@tutorias.com", "tutor123", "tutor")
    t2 = auth.registrar("Carlos Ruiz", "carlos@tutorias.com", "tutor123", "tutor")
    auth.registrar("Santiago Pérez", "santiago@tutorias.com", "estudiante123", "estudiante")
    auth.registrar("Ana Torres", "ana@tutorias.com", "estudiante123", "estudiante")

    ids = {n: tut.crear_materia(n) for n in
           ["Cálculo", "Programación", "Física", "Estructura de Datos", "Bases de Datos"]}

    manana = datetime.now() + timedelta(days=1)
    for dias, (tutor, materia, hora) in enumerate([
        (t1, "Cálculo", "09:00"), (t1, "Física", "11:00"), (t1, "Cálculo", "15:00"),
        (t2, "Programación", "10:00"), (t2, "Estructura de Datos", "14:00"),
        (t2, "Bases de Datos", "16:00"),
    ]):
        fecha = (manana + timedelta(days=dias % 3)).strftime("%Y-%m-%d")
        tut.publicar_horario(tutor.id, ids[materia], fecha, hora)
    return True
