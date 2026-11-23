# Servicio de IA: asistente de tutorías

## Qué hace
El estudiante escribe en lenguaje natural qué necesita estudiar. La aplicación le envía esa descripción y la lista de horarios libres al servicio de IA, que elige y ordena los más convenientes y explica el motivo. La interfaz muestra el resultado en una tabla y permite solicitar la tutoría con un clic.

## Servicio utilizado
- **Proveedor:** Google Gemini (modelo por defecto: `gemini-3.5-flash-lite`, con nivel gratuito).
- **Protocolo:** API de chat compatible con OpenAI, `POST {IA_BASE_URL}/chat/completions`, con la clave en la cabecera `Authorization: Bearer`.
- **Por qué este formato:** el mismo cliente sirve para Gemini, Groq, OpenRouter, OpenAI u Ollama (local) cambiando solo `IA_BASE_URL` y `IA_MODELO` en `.env`. Si un modelo se retira, basta con cambiar el nombre.
- **Sin librerías externas:** el cliente usa `urllib` de la biblioteca estándar.

## Flujo
```
Estudiante escribe su necesidad
        │
        ▼
EstudianteView ──► TutoriaService.listar_horarios_con_calificacion()   (SQLite, hilo principal)
        │
        ▼  (hilo en segundo plano: la ventana no se congela)
AsistenteTutorias.recomendar()
   1. valida la consulta (10 a 600 caracteres)
   2. arma el prompt: instrucciones + JSON con la consulta y los horarios
   3. ClienteIA.completar() ──► servicio de IA (HTTPS)
   4. interpreta el JSON de la respuesta
   5. descarta ids inexistentes o repetidos, recorta textos, máximo 5
        │
        ▼
EstudianteView muestra resumen, tabla y motivo ──► "Solicitar tutoría"
```

## Datos que se envían (privacidad)
Solo lo necesario: el texto que escribe el estudiante, la fecha de hoy y, de cada horario libre, su `id`, materia, nombre del tutor, fecha, hora, promedio de calificaciones y número de tutorías realizadas. **No se envían** correos, contraseñas, datos del estudiante ni comentarios de las calificaciones. Se recomienda no escribir datos personales en la descripción. En el nivel gratuito de Gemini, Google puede usar los datos enviados para mejorar sus productos.

## Prompt
El mensaje de sistema (en `src/services/ia_service.py`, constante `_INSTRUCCIONES`) le pide a la IA elegir hasta 5 horarios usando solo los `id` recibidos, considerar materia, calificación del tutor y urgencia, tratar el texto del estudiante como datos (no como instrucciones) y responder únicamente con JSON:

```json
{"resumen": "una o dos frases", "recomendaciones": [{"horario_id": 12, "motivo": "una frase corta"}]}
```

## Procesamiento y validación de la respuesta
Una IA puede equivocarse, así que la respuesta no se muestra tal cual:
- Se acepta JSON puro o dentro de un bloque de código.
- Los `horario_id` que no existen en la lista enviada, o repetidos, se descartan (la IA no puede mostrar horarios inventados).
- Los textos se limpian y se recortan (resumen 400 caracteres, motivo 220).
- Si la respuesta no es JSON, se muestra un error claro y la aplicación sigue funcionando.
- Al solicitar la tutoría se aplican las mismas reglas de negocio de siempre (horario libre, sin cruces).

## Manejo de errores
| Situación | Mensaje al usuario |
|---|---|
| Falta la clave | Indica crear `.env` y mira el README |
| Clave inválida (401) | «La clave del servicio de IA no es válida…» |
| Sin permiso (403) | «La clave… no tiene permiso para esta función» |
| Modelo o URL incorrectos (404) | «No se encontró el modelo o la dirección…» |
| Límite de uso (429) | «Se alcanzó el límite de uso… espera un momento» |
| Error del servicio (5xx) | «El servicio de IA no está disponible…» |
| Sin internet / tiempo agotado | «No hay conexión…» / «tardó demasiado…» |
| Respuesta vacía o mal formada | «…formato inesperado» / «no pude interpretar la respuesta» |
| Descripción muy corta o larga | Mensaje de validación |

La clave nunca aparece en los mensajes de error. Si el servicio rechaza el parámetro `response_format` (código 400), el cliente reintenta una vez sin él.

## Configuración (`.env`)
| Variable | Descripción | Valor por defecto |
|---|---|---|
| `IA_API_KEY` | Clave del servicio | (vacía) |
| `IA_BASE_URL` | Dirección base del servicio | Gemini (compatible con OpenAI) |
| `IA_MODELO` | Nombre del modelo | `gemini-3.5-flash-lite` |
| `IA_TIMEOUT` | Segundos de espera | `30` |

Las variables de entorno tienen prioridad sobre el archivo `.env`. Para comprobar la configuración: `python probar_ia.py`.

## Pruebas
`tests/test_ia.py` (20 pruebas) usa un transporte HTTP simulado, por lo que no necesita internet ni clave: configuración, formato de la petición, cada código de error, reintento sin `response_format`, fallos de red, respuestas mal formadas, ids inventados, límites, validación de la consulta y la consulta de horarios con calificaciones.
