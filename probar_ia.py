"""Prueba rápida de la conexión con el servicio de IA.

Uso:  python probar_ia.py
"""
import sys

from src.services.ia_service import ClienteIA, cargar_config
from src.utils.errores import AppError


def main() -> int:
    config = cargar_config()
    print(f"Servicio: {config.base_url}")
    print(f"Modelo:   {config.modelo}")
    print(f"Clave:    {'configurada' if config.api_key else 'NO configurada'}")
    try:
        respuesta = ClienteIA(config).completar(
            [{"role": "user", "content": "Responde solo con la palabra: listo"}], json_estricto=False)
    except AppError as e:
        print(f"\nERROR: {e}")
        return 1
    print(f"\nRespuesta del servicio: {respuesta.strip()}")
    print("La conexión funciona.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
