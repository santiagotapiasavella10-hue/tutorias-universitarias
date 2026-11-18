# Guía de Git para el equipo

## 1. Crear el repositorio (una sola persona)
1. En GitHub: **New repository** → nombre `tutorias-universitarias` → sin README (ya existe).
2. Settings → Collaborators → agregar a todos los integrantes (y verificar que el profesor pueda verlo).
3. En la carpeta del proyecto:

```bash
git init
git add .
git commit -m "chore: estructura inicial del proyecto Gestor de Tutorías"
git branch -M main
git remote add origin https://github.com/USUARIO/tutorias-universitarias.git
git push -u origin main
```

## 2. Trabajo diario (todos)
```bash
git pull origin main
git checkout -b feature/nombre-de-la-tarea
# ... trabajar ...
git add .
git commit -m "feat: descripción corta de lo que hiciste"
git push origin feature/nombre-de-la-tarea
```
Luego abrir un **Pull Request** en GitHub y fusionarlo a `main`.

## 3. Convención de mensajes de commit
| Prefijo | Uso |
|---|---|
| `feat:` | funcionalidad nueva |
| `fix:` | corrección de error |
| `docs:` | README, documentación, evidencias |
| `test:` | pruebas |
| `refactor:` | reorganizar código sin cambiar el comportamiento |
| `chore:` | configuración, estructura |

## 4. Para que la evolución se note
- Haz commits pequeños y frecuentes (uno por funcionalidad o corrección).
- **Que cada integrante tenga commits propios** (usa tu propio usuario de Git: `git config user.name` y `git config user.email`).
- Sugerencia de ramas: `feature/login`, `feature/horarios-tutor`, `feature/citas-estudiante`, `feature/admin-estadisticas`, `docs/readme-evidencias`.
