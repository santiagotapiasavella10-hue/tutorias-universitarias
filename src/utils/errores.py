"""Excepciones propias de la aplicación."""


class AppError(Exception):
    """Error base: su mensaje es apto para mostrarse al usuario."""


class ValidationError(AppError):
    """Dato de entrada inválido (formato, vacío, rango...)."""


class ReglaNegocioError(AppError):
    """Operación que viola una regla del negocio (cruce de horarios, etc.)."""
