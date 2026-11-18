"""Registro e inicio de sesión."""
import hashlib
import os
import sqlite3

from src.data.database import Database
from src.models.usuario import Usuario, crear_usuario
from src.utils.errores import ReglaNegocioError, ValidationError
from src.utils.validaciones import validar_correo, validar_nombre, validar_password

ROLES_REGISTRABLES = ("estudiante", "tutor")


def _hash(password: str, salt_hex: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 100_000).hex()


class AuthService:
    def __init__(self, db: Database):
        self.db = db

    def registrar(self, nombre, correo, password, rol, permitir_admin=False) -> Usuario:
        nombre = validar_nombre(nombre)
        correo = validar_correo(correo)
        password = validar_password(password)
        permitidos = ROLES_REGISTRABLES + (("admin",) if permitir_admin else ())
        if rol not in permitidos:
            raise ValidationError("Seleccione un rol válido.")
        salt = os.urandom(16).hex()
        try:
            cur = self.db.conn.execute(
                "INSERT INTO usuarios (nombre, correo, password_hash, salt, rol) VALUES (?,?,?,?,?)",
                (nombre, correo, _hash(password, salt), salt, rol),
            )
            self.db.conn.commit()
        except sqlite3.IntegrityError:
            raise ReglaNegocioError("Ya existe una cuenta con ese correo.")
        return crear_usuario(cur.lastrowid, nombre, correo, rol)

    def iniciar_sesion(self, correo, password) -> Usuario:
        correo = validar_correo(correo)
        if not password:
            raise ValidationError("La contraseña es obligatoria.")
        fila = self.db.conn.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,)).fetchone()
        if fila is None or _hash(password, fila["salt"]) != fila["password_hash"]:
            raise ReglaNegocioError("Correo o contraseña incorrectos.")
        return crear_usuario(fila["id"], fila["nombre"], fila["correo"], fila["rol"])
