"""Modelos de usuario (POO: herencia y polimorfismo)."""
from dataclasses import dataclass


@dataclass
class Usuario:
    id: int
    nombre: str
    correo: str
    rol: str = "usuario"

    def descripcion_rol(self) -> str:
        return "Usuario del sistema"


@dataclass
class Estudiante(Usuario):
    rol: str = "estudiante"

    def descripcion_rol(self) -> str:
        return "Estudiante: busca tutorías, agenda citas y califica sesiones"


@dataclass
class Tutor(Usuario):
    rol: str = "tutor"

    def descripcion_rol(self) -> str:
        return "Tutor: publica horarios y gestiona las solicitudes de tutoría"


@dataclass
class Administrador(Usuario):
    rol: str = "admin"

    def descripcion_rol(self) -> str:
        return "Administrador: gestiona materias y consulta estadísticas"


def crear_usuario(id: int, nombre: str, correo: str, rol: str) -> Usuario:
    """Fábrica: devuelve la subclase que corresponde al rol."""
    clases = {"estudiante": Estudiante, "tutor": Tutor, "admin": Administrador}
    return clases.get(rol, Usuario)(id=id, nombre=nombre, correo=correo)
