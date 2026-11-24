# SC-LAB-009 | Registro de evidencias

**Equipo:** __________  **Grupo:** __________  **Fecha:** __________

| Control | Comando / ubicación | Resultado (aprobado / hallazgo / no ejecutado) | Explicación y evidencia |
|---|---|---|---|
| Pruebas | `python -m pytest -q` | | |
| SAST | `python -m bandit -r src -ll -ii` | | |
| Dependencias | `python -m pip_audit -r requirements.txt` | | |
| CI en GitHub | Pestaña Actions | | |
| Imagen / Trivy | Trabajo container | | |

## Reflexión
1. ¿Qué control impide integrar un cambio con pruebas fallidas?
2. ¿En qué se diferencia SAST de auditar dependencias?
3. ¿Por qué un pipeline que aparece en verde no garantiza seguridad absoluta?
4. ¿Qué harías al detectar una vulnerabilidad crítica en una imagen?

**Conclusión del equipo (6 a 10 líneas):**
