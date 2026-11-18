"""Punto de entrada: python main.py"""
from src.data.database import Database
from src.data.seed import cargar_datos_ejemplo
from src.ui.app import App


def main():
    db = Database()
    cargar_datos_ejemplo(db)
    App(db).mainloop()
    db.cerrar()


if __name__ == "__main__":
    main()
