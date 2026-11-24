# SecureCampus — SC-LAB-008 | Laboratorio guiado de seguridad móvil y contenedores

Esta versión **amplía SC-LAB-007**. No es necesario instalar Android Studio. Usa una interfaz de navegador como **simulador conceptual de un cliente móvil**. Los datos y cuentas son ficticios.

## Ruta A — Sin Docker (parte móvil, Windows + VS Code)

1. Descomprime el ZIP en `C:\Proyectos\SecureCampus_SC-LAB-008_GUIADO`.
2. Abre esa carpeta con VS Code; usa Terminal > Nueva terminal.
3. `python -m venv .venv`
4. `.\.venv\Scripts\Activate.ps1`
5. `python -m pip install -r requirements.txt -r requirements-dev.txt`
6. `python run.py`
7. Abre `http://127.0.0.1:5000/mobile-demo` y, para iniciar sesión, `http://127.0.0.1:5000/`.
8. Ejecuta `python -m pytest -q` para verificar pruebas automatizadas.

Si PowerShell no permite activar el entorno: `Set-ExecutionPolicy -Scope Process Bypass`, y repite la activación. Si el puerto 5000 está ocupado, detén el servidor anterior con Ctrl+C.

## Ruta B — Con Docker Desktop (parte contenedores, Windows)

1. Instala y abre Docker Desktop; espera a que el motor esté iniciado.
2. Detén previamente `python run.py` (Ctrl+C) para liberar el puerto 5000.
3. Desde la carpeta de este proyecto: `docker compose up --build -d`.
4. Comprueba: `docker compose ps` y abre `http://127.0.0.1:5000/mobile-demo`.
5. Consulta registros: `docker compose logs --tail=50 securecampus`.
6. Termina: `docker compose down` (conserva la base de prueba en el volumen).
7. Reinicio total de datos ficticios, SOLO si se desea: `docker compose down -v`.

## Seguridad y límites didácticos

- SOLO ambiente local. El archivo `compose.yaml` publica la aplicación en `127.0.0.1` y configura `SC_COOKIE_SECURE=0` porque se usa HTTP **exclusivamente en localhost**. Para producción se requieren HTTPS/TLS, cookie Secure, secretos y configuración de despliegue revisada.
- El simulador guarda únicamente un **marcador ficticio**, jamás contraseñas ni tokens de sesión reales. La sesión auténtica utiliza cookies `HttpOnly`.
- Docker ejecuta la aplicación como usuario no privilegiado, con filesystem raíz de solo lectura y volumen para la base de datos; esto **no equivale** a una auditoría integral ni garantiza aislamiento absoluto.
- No publiques `securecampus_demo.db`, contraseñas de prueba ni datos personales reales.
- Si Docker no está disponible, realiza la Ruta A y el análisis guiado del `Dockerfile` y `compose.yaml` sin pretender que el contenedor se ejecutó.
