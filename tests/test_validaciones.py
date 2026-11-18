import unittest
from datetime import datetime

from src.utils.errores import ValidationError
from src.utils.validaciones import (
    validar_calificacion, validar_correo, validar_fecha_hora,
    validar_nombre, validar_password,
)


class TestValidaciones(unittest.TestCase):
    def test_correo_valido_se_normaliza(self):
        self.assertEqual(validar_correo("  Ana@Mail.com "), "ana@mail.com")

    def test_correo_invalido(self):
        for malo in ["", "ana", "ana@", "ana@mail", "@mail.com"]:
            with self.assertRaises(ValidationError):
                validar_correo(malo)

    def test_password_corta(self):
        with self.assertRaises(ValidationError):
            validar_password("123")

    def test_nombre_corto(self):
        with self.assertRaises(ValidationError):
            validar_nombre("Al")

    def test_fecha_hora_formato(self):
        ahora = datetime(2026, 1, 1, 8, 0)
        self.assertEqual(validar_fecha_hora("2026-01-02", "09:30", ahora), ("2026-01-02", "09:30"))
        with self.assertRaises(ValidationError):
            validar_fecha_hora("02/01/2026", "09:30", ahora)
        with self.assertRaises(ValidationError):
            validar_fecha_hora("2026-01-02", "25:00", ahora)

    def test_fecha_pasada(self):
        with self.assertRaises(ValidationError):
            validar_fecha_hora("2025-12-31", "10:00", datetime(2026, 1, 1))

    def test_calificacion(self):
        self.assertEqual(validar_calificacion("5"), 5)
        for malo in [0, 6, "abc", None]:
            with self.assertRaises(ValidationError):
                validar_calificacion(malo)


if __name__ == "__main__":
    unittest.main()
