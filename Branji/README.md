# SecureCampus — SC-LAB-006
Entorno académico local. No publicar con datos reales.

## Ejecutar (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
python -m src.app
```

Credenciales de DEMOSTRACIÓN (solo local): usuarios `profe_ana`, `profe_luis`, `alumna_eli`, `alumno_paz`, `admin_demo`; contraseña `Laboratorio2026!`. No usar en producción.

## Actividad
Implementar TODO de `src/validators.py` y `src/permissions.py`. No modificar tests para ocultar fallas.

## Alcance
La API JSON es de laboratorio: no incluye MFA, rate limiting, control integral de logs ni UI. CI usa versiones mayores de acciones como simplificación didáctica; en producción fijar a SHA verificado.
