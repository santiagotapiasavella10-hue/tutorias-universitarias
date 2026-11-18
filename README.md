# Gestor de Tutorías Universitarias

> Taller de Programación · Fase II — Prototipo funcional

Aplicación de escritorio en **Python** que conecta a estudiantes con tutores: el estudiante busca y agenda tutorías, el tutor publica horarios y responde solicitudes, y el administrador consulta estadísticas.

## Integrantes

| Nombre | Rol en el proyecto |
|---|---|
| _Nombre 1_ | Santiago Tapias Avella |
| _Nombre 2_ | _Harlen Moreno |
| _Nombre 3_ | _por definir_ |

## Problema que resuelve

Hoy las tutorías entre estudiantes se coordinan por chats informales: se pierden los horarios, se cruzan las citas y no hay registro de quién ayudó a quién. Este sistema centraliza la oferta de tutorías, evita cruces de horario y deja historial y calificaciones.

## Funcionalidades de la Fase II

| Rol | Funcionalidades |
|---|---|
| **Todos** | Registro de cuenta, inicio y cierre de sesión (contraseñas con hash PBKDF2) |
| **Estudiante** | Buscar horarios por materia · Agendar tutoría · Cancelar cita · Ver historial · Calificar tutorías realizadas (1–5) |
| **Tutor** | Publicar y eliminar horarios · Aceptar o rechazar solicitudes · Marcar tutoría como realizada |
| **Administrador** | Crear materias · Estadísticas (usuarios, citas por estado, ranking de tutores con promedio) |

### Validaciones implementadas
- Campos obligatorios y longitud mínima (nombre, contraseña).
- Formato de correo electrónico y correo único.
- Formato de fecha `AAAA-MM-DD` y hora `HH:MM`; no se permiten horarios en el pasado.
- No se pueden duplicar horarios de un mismo tutor.
- Un horario solo puede tener una cita vigente (también garantizado por un índice único en la BD).
- Un estudiante no puede tener dos citas en el mismo día y hora (cruce de horarios).
- Solo se califica una tutoría realizada y una única vez; solo el dueño puede cancelar su cita.
- Los errores se muestran al usuario con mensajes claros; la aplicación no se cierra por errores.

## Tecnologías

- Python 3.10 o superior
- Tkinter (interfaz gráfica) — incluido con Python
- SQLite (`sqlite3`) — persistencia, incluido con Python
- `unittest` para las pruebas

**No hay dependencias externas que instalar.**

## Instalación y ejecución

```bash
# 1. Clonar
git clone <URL-DEL-REPOSITORIO>
cd tutorias-universitarias

# 2. (Opcional) entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS

# 3. Ejecutar
python main.py
```

La primera vez se crea `data/tutorias.db` con datos de ejemplo.
Para reiniciar los datos, borra ese archivo y vuelve a ejecutar.

> En Linux, si falla `import tkinter`: `sudo apt install python3-tk`.

### Cuentas de prueba

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@tutorias.com | admin123 |
| Tutor | laura@tutorias.com | tutor123 |
| Tutor | carlos@tutorias.com | tutor123 |
| Estudiante | santiago@tutorias.com | estudiante123 |
| Estudiante | ana@tutorias.com | estudiante123 |

## Pruebas

```bash
python -m unittest -v
```

## Estructura del proyecto

```
tutorias-universitarias/
├── main.py                  # Punto de entrada
├── requirements.txt
├── src/
│   ├── models/usuario.py    # Usuario, Estudiante, Tutor, Administrador (herencia)
│   ├── data/
│   │   ├── database.py      # Conexión y esquema SQLite
│   │   └── seed.py          # Datos de ejemplo
│   ├── services/
│   │   ├── auth_service.py      # Registro e inicio de sesión
│   │   └── tutoria_service.py   # Horarios, citas, calificaciones, estadísticas
│   ├── utils/
│   │   ├── errores.py       # Excepciones propias
│   │   └── validaciones.py  # Validaciones de entrada
│   └── ui/                  # Interfaz Tkinter (una vista por pantalla/rol)
├── tests/                   # Pruebas unitarias
└── docs/                    # Descripción, guía de Git y evidencias
```

**Arquitectura en capas:** `ui` → `services` → `data`. La interfaz nunca toca la base de datos directamente; toda la lógica y las reglas están en `services`, lo que permite probarla sin interfaz y reutilizarla después en una API REST.

## Evidencias de funcionamiento

Capturas en [`docs/evidencias/`](docs/evidencias/):

| Pantalla | Archivo |
|---|---|
| Inicio de sesión | `01_login.png` |
| Registro | `02_registro.png` |
| Estudiante: buscar y agendar | `03_estudiante_buscar.png` |
| Estudiante: mis citas | `04_estudiante_citas.png` |
| Tutor: horarios | `05_tutor_horarios.png` |
| Tutor: solicitudes | `06_tutor_solicitudes.png` |
| Administrador: estadísticas | `07_admin_estadisticas.png` |
| Validación en acción | `08_validacion_error.png` |
| Pruebas pasando | `09_tests.png` |

## Próximos pasos (entrega final)

- Integración de un servicio de **Inteligencia Artificial** (por ejemplo, recomendación de tutores según materia y nivel).
- Posible API REST y notificaciones.
