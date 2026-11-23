# Texto para la entrega en Canvas (completa lo que está entre corchetes)

**Integrantes:** Santiago Tapias Avella, Harlen Moreno

**Nombre del proyecto:** Gestor de Tutorías Universitarias

**Enlace al repositorio:** https://github.com/santiagotapiasavella10-hue/tutorias-universitarias

**Descripción breve de la versión final:**
Aplicación de escritorio en Python (Tkinter y SQLite) para gestionar tutorías universitarias con tres roles: estudiante, tutor y administrador. El estudiante busca horarios, agenda, cancela y califica tutorías; el tutor publica horarios y responde solicitudes; el administrador gestiona materias y consulta estadísticas. En esta entrega se integró un servicio de Inteligencia Artificial (Google Gemini, mediante su API compatible con OpenAI): el estudiante describe qué necesita estudiar y el asistente recomienda horarios libres reales con el motivo de cada uno. La aplicación envía la consulta y los horarios disponibles al servicio, procesa la respuesta (descarta horarios inventados) y la presenta en la interfaz, con manejo de errores para clave inválida, límite de uso, falta de conexión y respuestas mal formadas. El proyecto mantiene una arquitectura en capas, validaciones, 43 pruebas unitarias, README con instrucciones, documentación del servicio de IA y evidencias de funcionamiento.
