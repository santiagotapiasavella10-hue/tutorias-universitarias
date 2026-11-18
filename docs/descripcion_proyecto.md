# Descripción del proyecto

## Objetivo general
Desarrollar una aplicación que permita gestionar tutorías universitarias entre estudiantes y tutores, centralizando horarios, citas y calificaciones.

## Objetivos específicos
1. Permitir el registro y autenticación de estudiantes, tutores y administradores.
2. Permitir a los tutores publicar horarios y gestionar solicitudes.
3. Permitir a los estudiantes buscar, agendar, cancelar y calificar tutorías.
4. Evitar conflictos de horarios mediante validaciones.
5. Ofrecer al administrador estadísticas del uso del sistema.

## Alcance de la Fase II
Prototipo funcional con interfaz gráfica, navegación por roles, validaciones básicas y persistencia en SQLite. **Fuera del alcance:** servicio de IA (entrega final), API REST, notificaciones por correo.

## Flujo principal
1. El tutor publica un horario para una materia.
2. El estudiante lo encuentra, filtrando por materia, y solicita la tutoría.
3. El tutor acepta o rechaza la solicitud.
4. Tras la sesión, el tutor la marca como realizada.
5. El estudiante califica al tutor y el administrador ve las estadísticas.

## Modelo de datos
- `usuarios` (id, nombre, correo, password_hash, salt, rol)
- `materias` (id, nombre)
- `horarios` (id, tutor_id, materia_id, fecha, hora)
- `citas` (id, horario_id, estudiante_id, estado, calificacion, comentario)

Estados de una cita: `pendiente → aceptada → realizada`, o `rechazada` / `cancelada`.
