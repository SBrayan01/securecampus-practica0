# SecureCampus | SC-LAB-009 — DevSecOps guiado

Continúa el proyecto de los laboratorios 007 y 008. **No es necesario escribir el pipeline**: está incluido para que el estudiantado lo ejecute, observe y explique.

## Requisitos
- Windows con Python, Visual Studio Code y conexión a internet para instalar bibliotecas.
- Git y una cuenta GitHub solo para la etapa opcional de ejecución remota.
- Docker Desktop opcional para construir una imagen local.
- **Únicamente datos ficticios**. No usar credenciales reales ni publicar la base de datos.

## Ruta principal (sin Docker, sin GitHub)
1. Descomprime este ZIP en `C:\Proyectos` y abre **SecureCampus_SC-LAB-009_GUIADO** en VS Code.
2. Terminal → Nueva terminal (PowerShell):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt -r requirements-dev.txt
   ```
3. En la misma terminal, ejecuta una comprobación cada vez y registra sus resultados:
   ```powershell
   python -m pytest -q
   python -m bandit -r src -ll -ii
   python -m pip_audit -r requirements.txt
   ```
4. Abre `.github/workflows/security.yml` y ubica los mismos comandos en el pipeline.
5. Si una herramienta detecta problemas, no se garantiza que el resultado sea “aprobado”: **documenta el hallazgo**. Nunca omitas controles para obtener verde.

## Ruta opcional con GitHub Actions
- Inicia un repositorio nuevo de laboratorio (privado si corresponde). No subas `.venv`, `*.db`, cookies, secretos ni datos de personas.
- Desde la carpeta del proyecto: `git init`, `git add .`, `git commit -m "SC-LAB-009: primera revision"`.
- Crea un repositorio vacío en GitHub y sigue sus instrucciones oficiales para establecer `origin` y subir la rama.
- Ve a **Actions → SC-LAB-009 | Controles DevSecOps**; revisa los trabajos **security** y **container**.
- Los resultados pueden variar con las vulnerabilidades publicadas y el entorno de GitHub. Un hallazgo no debe ocultarse ni tratarse como éxito.

## Ruta opcional Docker local
```powershell
docker build -t securecampus:lab009 .
docker images
```
Construir una imagen **no demuestra** que sea segura; el pipeline incluye un escaneo de vulnerabilidades con Trivy.

## Límites importantes
- Las versiones de dependencias están acotadas por rangos, no bloqueadas: el resultado puede cambiar en el tiempo. Para despliegues reales, fijar y actualizar versiones deliberadamente.
- La imagen usa HTTP solo en localhost; **no es un despliegue de producción**.
- El escaneo automatizado requiere internet y acceso a GitHub; Docker es opcional para la ruta local, pero el trabajo `container` de GitHub utiliza Docker.
- `Bandit` es SAST; `pip-audit` analiza dependencias; `pytest` prueba escenarios; `Trivy` analiza la imagen. Ninguna herramienta por sí sola acredita que el sistema esté libre de riesgos.
