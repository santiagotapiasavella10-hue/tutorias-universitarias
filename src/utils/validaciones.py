"""Validaciones básicas de datos de entrada."""
import re
from datetime import datetime

from src.utils.errores import ValidationError

_REGEX_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def validar_nombre(nombre: str) -> str:
    nombre = (nombre or "").strip()
    if len(nombre) < 3:
        raise ValidationError("El nombre debe tener al menos 3 caracteres.")
    return nombre


def validar_correo(correo: str) -> str:
    correo = (correo or "").strip().lower()
    if not correo:
        raise ValidationError("El correo es obligatorio.")
    if not _REGEX_CORREO.match(correo):
        raise ValidationError("El correo no tiene un formato válido.")
    return correo


def validar_password(password: str) -> str:
    if not password or len(password) < 6:
        raise ValidationError("La contraseña debe tener al menos 6 caracteres.")
    return password


def validar_fecha_hora(fecha: str, hora: str, ahora: datetime | None = None) -> tuple[str, str]:
    """Valida formato AAAA-MM-DD y HH:MM, y que no sea una fecha pasada."""
    fecha = (fecha or "").strip()
    hora = (hora or "").strip()
    if not fecha or not hora:
        raise ValidationError("La fecha y la hora son obligatorias.")
    try:
        momento = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValidationError("Use el formato AAAA-MM-DD para la fecha y HH:MM para la hora.")
    if momento < (ahora or datetime.now()):
        raise ValidationError("No se puede publicar un horario en el pasado.")
    return fecha, hora


def validar_calificacion(puntaje) -> int:
    try:
        puntaje = int(puntaje)
    except (TypeError, ValueError):
        raise ValidationError("La calificación debe ser un número entero.")
    if not 1 <= puntaje <= 5:
        raise ValidationError("La calificación debe estar entre 1 y 5.")
    return puntaje


def validar_nombre_materia(nombre: str) -> str:
    nombre = (nombre or "").strip()
    if len(nombre) < 3:
        raise ValidationError("El nombre de la materia debe tener al menos 3 caracteres.")
    return nombre
