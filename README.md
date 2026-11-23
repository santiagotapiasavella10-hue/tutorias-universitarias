# Gestor de Tutorías Universitarias

> Taller de Programación · Entrega final — Prototipo funcional con servicio de IA

Aplicación de escritorio en **Python** que conecta a estudiantes con tutores: el estudiante busca y agenda tutorías, el tutor publica horarios y responde solicitudes, y el administrador consulta estadísticas. Un **asistente de IA** recomienda al estudiante los horarios que mejor le sirven según lo que necesita estudiar.

## Integrantes

| Nombre | Rol en el proyecto |
|---|---|
| Santiago Tapias Avella | Desarrollo del prototipo |
| Harlen Moreno | Desarrollo del prototipo |

## Problema que resuelve

Hoy las tutorías entre estudiantes se coordinan por chats informales: se pierden los horarios, se cruzan las citas y no hay registro de quién ayudó a quién. Este sistema centraliza la oferta de tutorías, evita cruces de horario y deja historial y calificaciones.

## Funcionalidades

| Rol | Funcionalidades |
|---|---|
| **Todos** | Registro de cuenta, inicio y cierre de sesión (contraseñas con hash PBKDF2) |
| **Estudiante** | Buscar horarios por materia · **Pedir recomendaciones al asistente de IA** · Agendar tutoría · Cancelar cita · Ver historial · Calificar tutorías realizadas (1–5) |
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
- Servicio de IA: API de chat compatible con OpenAI (por defecto **Google Gemini**), consumida con `urllib` de la biblioteca estándar

**No hay dependencias externas que instalar.** Solo el asistente de IA necesita una clave y conexión a internet; el resto de la aplicación funciona sin ellas.

## Servicio de IA

**Asistente de tutorías.** En la pestaña *Asistente de IA* del panel del estudiante, la persona escribe qué necesita (por ejemplo: «tengo parcial de derivadas el viernes y no entiendo la regla de la cadena») y la IA recomienda hasta 5 horarios libres reales, ordenados, con el motivo de cada uno. Desde ahí mismo se agenda la tutoría.

**Servicio utilizado:** Google Gemini, mediante su API compatible con el formato de chat de OpenAI (`/chat/completions`). La conexión es configurable, así que también funciona con Groq, OpenRouter, OpenAI u Ollama (local). El detalle de cómo funciona, el prompt, la validación de respuestas, la privacidad y el manejo de errores está en [`docs/servicio_ia.md`](docs/servicio_ia.md).

### Cómo activarlo (2 minutos)

1. Crea una clave gratuita en [Google AI Studio](https://aistudio.google.com/apikey).
2. En la carpeta del proyecto, copia `.env.example` como `.env` y pega la clave:
   ```
   IA_API_KEY=tu_clave_aqui
   ```
3. Comprueba la conexión:
   ```bash
   python probar_ia.py
   ```
   Debe terminar con `La conexión funciona.`
4. Ejecuta `python main.py`, entra como estudiante y abre la pestaña *Asistente de IA*.

> El archivo `.env` está en `.gitignore`: **nunca se sube a GitHub**. No publiques tu clave.

Si no hay clave o no hay internet, la aplicación sigue funcionando y el asistente muestra un aviso claro de qué falta.

## Instalación y ejecución

```bash
# 1. Clonar
git clone <URL-DEL-REPOSITORIO>
cd tutorias-universitarias

# 2. (Opcional) entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS

# 3. (Opcional) activar el asistente de IA: ver la sección «Servicio de IA»

# 4. Ejecutar
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
├── probar_ia.py             # Comprueba la conexión con el servicio de IA
├── .env.example             # Plantilla de configuración (la clave va en .env)
├── requirements.txt
├── src/
│   ├── models/usuario.py    # Usuario, Estudiante, Tutor, Administrador (herencia)
│   ├── data/
│   │   ├── database.py      # Conexión y esquema SQLite
│   │   └── seed.py          # Datos de ejemplo
│   ├── services/
│   │   ├── auth_service.py      # Registro e inicio de sesión
│   │   ├── tutoria_service.py   # Horarios, citas, calificaciones, estadísticas
│   │   └── ia_service.py        # Cliente del servicio de IA y asistente de recomendaciones
│   ├── utils/
│   │   ├── errores.py       # Excepciones propias
│   │   └── validaciones.py  # Validaciones de entrada
│   └── ui/                  # Interfaz Tkinter (una vista por pantalla/rol)
├── tests/                   # Pruebas unitarias (servicios, validaciones y servicio de IA)
└── docs/                    # Descripción, servicio de IA, guía de Git y evidencias
```

**Arquitectura en capas:** `ui` → `services` → `data`. La interfaz nunca toca la base de datos directamente; toda la lógica y las reglas están en `services`, lo que permite probarla sin interfaz y reutilizarla después en una API REST.

## Evidencias de funcionamiento

Capturas en [`docs/evidencias/`](docs/evidencias/):

| Pantalla | Archivo |
|---|---|
| Inicio de sesión | `image.png` |
| Estudiante: buscar tutorías | `image-1.png` |
| Estudiante: mis citas | `image-2.png` |
| Validación en acción | `image-3.png` |
| Asistente de IA: recomendaciones | `asistente_ia.png` |
| Asistente de IA: error controlado (sin clave o sin conexión) | `asistente_error.png` |

## Posibles mejoras

- API REST y notificaciones por correo.
- Usar los comentarios de las calificaciones como contexto del asistente (hoy solo se envían los promedios).
