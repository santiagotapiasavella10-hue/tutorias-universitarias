"""Capa de datos: conexión SQLite y esquema de tablas."""
import sqlite3
from pathlib import Path

RUTA_POR_DEFECTO = Path(__file__).resolve().parents[2] / "data" / "tutorias.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT NOT NULL,
    correo        TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    rol           TEXT NOT NULL CHECK (rol IN ('estudiante', 'tutor', 'admin'))
);

CREATE TABLE IF NOT EXISTS materias (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS horarios (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    tutor_id   INTEGER NOT NULL REFERENCES usuarios(id),
    materia_id INTEGER NOT NULL REFERENCES materias(id),
    fecha      TEXT NOT NULL,
    hora       TEXT NOT NULL,
    UNIQUE (tutor_id, fecha, hora)
);

CREATE TABLE IF NOT EXISTS citas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    horario_id    INTEGER NOT NULL REFERENCES horarios(id),
    estudiante_id INTEGER NOT NULL REFERENCES usuarios(id),
    estado        TEXT NOT NULL DEFAULT 'pendiente'
                  CHECK (estado IN ('pendiente','aceptada','rechazada','cancelada','realizada')),
    calificacion  INTEGER,
    comentario    TEXT
);

-- Un horario no puede tener dos citas vigentes a la vez
CREATE UNIQUE INDEX IF NOT EXISTS idx_cita_vigente
    ON citas(horario_id) WHERE estado IN ('pendiente','aceptada','realizada');
"""


class Database:
    def __init__(self, ruta=RUTA_POR_DEFECTO):
        ruta = str(ruta)
        if ruta != ":memory:":
            Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(ruta)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(ESQUEMA)
        self.conn.commit()

    def cerrar(self):
        self.conn.close()
