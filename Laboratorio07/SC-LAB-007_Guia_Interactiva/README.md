# SecureCampus SC-LAB-007 — guía visual REST y GraphQL

## Windows / VS Code
1. Descomprime este ZIP en `C:\Proyectos\SecureCampus_SC-LAB-007` y abre la carpeta en VS Code.
2. Abre **Terminal > Nueva terminal**.
3. `python -m venv .venv`
4. ` .\.venv\Scripts\Activate.ps1` (sin espacio inicial). Si PowerShell bloquea la activación, ejecuta `Set-ExecutionPolicy -Scope Process Bypass` y repite.
5. `python -m pip install -r requirements.txt -r requirements-dev.txt`
6. `python run.py`
7. Abre `http://127.0.0.1:5000` en el navegador.
8. Al terminar, detén el servidor con `Ctrl+C`.

## Verificación
`python -m pytest -q` — se esperan 18 pruebas aprobadas en el proyecto distribuido.

## Cuentas ficticias
`profe_ana`, `profe_luis`, `alumna_eli`, `alumno_paz` — contraseña de laboratorio `Laboratorio2026!`.

## Atención
- Ejecutar **solo en la computadora local**; no desplegar en Internet.
- La base `securecampus_demo.db` contiene datos ficticios. Para restaurarla, detén el servidor, elimina ese archivo y vuelve a ejecutar `python run.py`.
- No guardar secretos reales en código ni subir la base a GitHub.
- GraphQL es solo de lectura; REST permite GET y PUT. Ambos comprueban autorización en servidor.
- Los errores GraphQL de esta demostración usan HTTP 403/400 para facilitar el aprendizaje; otras implementaciones GraphQL pueden usar HTTP 200 con un campo `errors`.
