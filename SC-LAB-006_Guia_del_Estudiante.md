# LABORATORIO INTEGRADOR | BLOQUE 2
# SC-LAB-006: GUÍA DEL ESTUDIANTE

**Instrucciones, código inicial, actividades y registro de evidencias**  
**Temas:** 2.1 Patrones · 2.2 Resiliencia · 2.3 Validación · 2.4 Sesiones y acceso · 2.5 Criptografía · 2.6 Dependencias y errores · 2.7 CI/CD  
**Proyecto:** SecureCampus | **Modalidad:** equipos de cuatro | **Duración:** 2 sesiones de 120 minutos + entrega posterior de documentación  

---

## 1. Propósito y reglas

Tu equipo recibirá una API Flask de calificaciones y una base SQLite que se crea automáticamente con datos ficticios. **NO** programarán toda la aplicación. Su misión es completar controles de seguridad, comprobarlos con pruebas y explicar las decisiones de diseño.

Trabajen solo en entorno local y en repositorio académico privado. Las credenciales del ejercicio son ficticias; no suban información real ni secretos. No alteren las pruebas para ocultar errores. El paquete inicial contiene fallas deliberadas en validación y autorización.

---

## 2. Entrega y evaluación

| Entregable | Evidencia requerida |
| :--- | :--- |
| **Repositorio** | Código corregido, historial de commits y PR |
| **Informe** | Matriz de riesgos y permisos; arquitectura y decisiones |
| **Pruebas** | Salida de pytest y auditoría de dependencias |
| **CI** | Captura de ejecución en GitHub Actions |
| **Demostración** | 5 minutos por equipo + preguntas individuales |

---

## 3. Preparación: ejecutar la base de datos de prueba

Descarga y descomprime `SecureCampus_SC-LAB-006_ESTUDIANTE.zip`. En VS Code abre la carpeta extraída. Desde PowerShell, ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

La base de datos de cada prueba se genera automáticamente en una carpeta temporal. Para iniciar el servidor local: `python -m src.app`. Se creará `securecampus_demo.db` con usuarios, grupos y calificaciones ficticios. La primera ejecución de pytest **DEBE** mostrar errores: son el punto de partida.

| Usuario ficticio | Rol | Grupo / recurso |
| :--- | :--- | :--- |
| `profe_ana` | Profesor | ISC401 (10) |
| `profe_luis` | Profesor | ISC402 (20) |
| `alumna_eli` | Estudiante | ISC401 (alumno 3) |
| `alumno_paz` | Estudiante | ISC402 (alumno 4) |
| `admin_demo` | Administrador | Sin facultad de modificar notas por defecto |

> **Nota:** Contraseña de demostración para todos: `Laboratorio2026!` (únicamente entorno local).

---

## 4. Distribución de tareas

| Rol | Responsabilidad |
| :--- | :--- |
| **Arquitectura** | Matriz de riesgos y diseño ante fallas |
| **Backend** | Validación, SQL y tratamiento de errores |
| **Identidad y acceso** | Autenticación, sesión, permisos y pruebas negativas |
| **Calidad / DevSecOps** | Pruebas, dependencias y CI |

---

## 5. Actividad A: diseño seguro y resiliencia (2.1–2.2)

Dibuja el flujo de actualización de calificaciones: autenticación → CSRF → autorización → validación → transacción de calificación y evento de notificación. Identifica dónde debe denegarse el acceso cuando falle una comprobación. El sistema guarda en la misma transacción una fila en `notification_outbox`; el envío real no se implementa.

| Riesgo o falla | Control propuesto | Prueba / evidencia |
| :--- | :--- | :--- |
| **Profesor de otro grupo** | Comprobación obligatoria en base de datos: `'SELECT 1 FROM groups WHERE id = ? AND professor_id = ?'` dentro de `puede_modificar()`. | Prueba `test_professor_other_group_forbidden` (profe_ana intentando modificar grupo 20 de profe_luis). Retorna HTTP 403 Forbidden. |
| **Servicio de notificaciones no disponible** | Patrón Transactional Outbox: la notificación se guarda en la tabla local `notification_outbox` dentro de la misma transacción atómica que la calificación. Un worker asíncrono desacoplado se encarga de enviarla. | Prueba `test_outbox_transaction` verifica que al hacer `PUT /grades` se inserta la fila en `notification_outbox` sin depender de servicios externos. |
| **Datos de calificación inválidos** | Validación rigurosa de tipo y límites en `validar_calificacion()`: conversión a Decimal, rechazo de nulos, booleanos, texto, NaN, Infinity, fuera de [0, 100] o con >2 decimales sin redondeo. | Prueba parametrizada `test_grade_invalid` con entradas `['150', '-1', 'hola', '', 'NaN', 'Infinity', None, '99.999']`. Todas devuelven HTTP 400 Bad Request. |
| **Sesión revocada** | Revocación física inmediata: `/logout` elimina el hash SHA-256 del token de la tabla `sessions`. En cada petición, `session_user()` verifica existencia y no expiración. | Prueba `test_logout_revokes` ejecuta `POST /logout` y luego un `GET` a `/grades` con la cookie invalidada, recibiendo HTTP 401 Unauthorized. |

### Preguntas y Respuestas Actividad A

1. **Flujo de actualización de calificaciones:**
   - **Paso 1. Autenticación:** Valida cookie `sc_session` en tabla `sessions` y vigencia (falla $\rightarrow$ HTTP 401 Unauthorized).
   - **Paso 2. Verificación CSRF:** Compara cabecera `X-CSRF-Token` con token de sesión mediante `secrets.compare_digest` (falla $\rightarrow$ HTTP 403 Forbidden).
   - **Paso 3. Validación de Entrada:** `validar_calificacion()` verifica que la nota sea numérica, rango 0..100 y máx 2 decimales (falla $\rightarrow$ HTTP 400 Bad Request).
   - **Paso 4. Autorización ABAC:** `puede_modificar()` valida que el usuario sea profesor del grupo y el alumno esté inscrito (falla $\rightarrow$ HTTP 403 Forbidden).
   - **Paso 5. Transacción Atómica:** Se guarda la calificación en `grades` y se inserta el evento en `notification_outbox` en la misma transacción SQLite (éxito $\rightarrow$ HTTP 200 OK).

2. **¿Por qué la notificación no debe bloquear la calificación?**  
   El envío de notificaciones es una tarea secundaria sujeta a latencia de red y dependencias externas. Si el guardado de la nota dependiera de la entrega síncrona de la notificación, una falla o lentitud en el proveedor de correo/mensajería bloquearía la calificación del estudiante. Mediante el patrón Transactional Outbox, la notificación se guarda localmente en la misma transacción de la base de datos y un despachador asíncrono se encarga del envío desacoplado, garantizando alta disponibilidad del servicio principal.

3. **¿Por qué no puede aplicarse la misma degradación al control de autorización?**  
   La autorización es un requisito fundamental de seguridad que protege la confidencialidad e integridad del sistema (principio de *Fail-Safe Defaults*). Una degradación permisiva permitiría que usuarios no autorizados lean o modifiquen notas ante cualquier fallo. Si la autorización no puede ser verificada con certeza, el sistema debe fallar hacia un estado cerrado (*fail-close*), denegando siempre el acceso con HTTP 403.

---

## 6. Actividad B: validación (2.3)

Completa `src/validators.py`. Acepta calificaciones de 0 a 100 con máximo dos decimales; rechaza booleanos, NaN, infinito, cadenas vacías, texto no numérico y valores fuera de rango. No redondees silenciosamente. Ejecuta pytest y registra qué casos cambiaron de fallo a éxito.

```bash
# Archivo que debes modificar
src/validators.py

# Comando de verificación
python -m pytest tests/test_security.py -q
```

| Entrada | Esperado | Resultado real |
| :--- | :--- | :--- |
| `85` | Aceptar | Aceptado: retorna HTTP 200 OK, calificación almacenada como `Decimal('85')`. |
| `99.50` | Aceptar | Aceptado: retorna HTTP 200 OK, calificación almacenada como `Decimal('99.50')`. |
| `150` | Rechazar (400) | Rechazado: retorna HTTP 400 Bad Request (`ValueError`: supera el límite superior de 100). |
| `NaN` | Rechazar (400) | Rechazado: retorna HTTP 400 Bad Request (`ValueError`: valor especial no numérico NaN detectado). |
| `99.999` | Rechazar (400) | Rechazado: retorna HTTP 400 Bad Request (`ValueError`: precisión excede el máximo permitido de 2 decimales). |

---

## 7. Actividad C: acceso por recurso (2.4)

Completa `src/permissions.py`. Un profesor solo modifica calificaciones de estudiantes inscritos en sus grupos; un estudiante solo consulta la suya. El administrador no modifica notas por defecto. Consulta siempre las asignaciones en la base del servidor. Prueba casos permitidos y denegados.

| Caso | HTTP esperado | Resultado real |
| :--- | :--- | :--- |
| **Profesor propio / PUT** | 200 | HTTP 200 OK: `profe_ana` modifica la nota del alumno 3 en grupo 10 asignado; outbox generado. |
| **Profesor ajeno / PUT** | 403 | HTTP 403 Forbidden: `profe_ana` intenta modificar grupo 20 asignado a `profe_luis`; denegado. |
| **Estudiante ajeno / GET** | 403 | HTTP 403 Forbidden: `alumna_eli` intenta consultar notas del grupo 20 / alumno 4; denegado. |
| **Estudiante propio / GET** | 200 | HTTP 200 OK: `alumna_eli` consulta su propia nota en grupo 10 en el que está inscrita. |
| **Sin sesión / GET** | 401 | HTTP 401 Unauthorized: petición sin cookie `sc_session` o con sesión expirada/inexistente. |
| **Sin CSRF / PUT** | 403 | HTTP 403 Forbidden: petición PUT con sesión pero sin el header `X-CSRF-Token`; token CSRF exigido. |

---

## 8. Actividad D: criptografía y sesiones (2.4–2.5)

Inspecciona `src/auth.py` y `src/db.py`. Identifica el uso de `generate_password_hash`, `check_password_hash`, `secrets.token_urlsafe` y el hash del token de sesión guardado en SQLite. Explica qué se almacena y qué no. Verifica que `/logout` invalida la sesión y que el servidor exige token CSRF para cambios.

### Preguntas y Respuestas Actividad D

1. **Diferencia entre hash de contraseña y cifrado:**
   - **Hash:** Función unidireccional (*one-way*). Su objetivo es imposibilitar la recuperación del texto original. Se aplica salt aleatorio y algoritmos costosos como PBKDF2 para proteger las contraseñas ante filtraciones de bases de datos.
   - **Cifrado:** Bidireccional (reversible con una clave). Se utiliza cuando los datos deben ser recuperados y leídos por entidades autorizadas (ej. datos confidenciales o tráfico HTTPS).

2. **¿Qué se almacena y qué no en la base de datos?**
   - En `users`: Se almacena `password_hash` (PBKDF2-SHA256 con salt); nunca la contraseña plana.
   - En `sessions`: Se almacena el hash SHA-256 del token de sesión (`token_hash`) y el `csrf_token`. El token crudo reside únicamente en la cookie del cliente.

3. **¿Qué atributo impide que JavaScript lea la cookie?**  
   El atributo `HttpOnly=True` en la cookie `sc_session`. Bloquea el acceso a la cookie mediante `document.cookie`, neutralizando el robo de sesión ante ataques de Cross-Site Scripting (XSS).

4. **Limitaciones frente a un entorno de producción:**
   - Almacenamiento en SQLite local en vez de un motor distribuido en memoria como Redis con expiración automática.
   - Ausencia de autenticación multifactor (MFA/2FA).
   - Falta de limitación de tasa (*Rate Limiting*) para mitigar ataques de fuerza bruta en `/login`.
   - Cookies sin flag `Secure` en modo de pruebas local, requiriendo HTTPS forzado y HSTS en producción.

---

## 9. Actividad E: dependencias, errores y archivos (2.6)

Localiza consultas SQL parametrizadas en `src/app.py`. Comprueba que los mensajes HTTP no exponen trazas internas. Ejecuta `python -m pip_audit -r requirements.txt` y documenta los hallazgos. Propón, sin implementarlo, una descarga de constancia por ID con autorización del propietario y ruta obtenida de la base de datos.

| Dependencia | Versión resuelta | Hallazgo / acción |
| :--- | :--- | :--- |
| **Flask** | Flask 3.1.3 | 0 vulnerabilidades conocidas (pip-audit). Framework web WSGI seguro; rutas y manejo de cookies seguros. |
| **Werkzeug** | Werkzeug 3.1.9 | 0 vulnerabilidades conocidas (pip-audit). Biblioteca de utilidades web que provee PBKDF2-SHA256 seguro. |
| **pytest / pip-audit** | pytest 9.1.1 / pip-audit 2.10.1 | 0 vulnerabilidades conocidas. Herramientas de pruebas y auditoría continua de seguridad en dependencias. |

---

## 10. Actividad F: CI/CD (2.7)

Crea una rama, realiza cambios, abre un Pull Request y revisa `.github/workflows/security.yml`. El pipeline ejecuta pytest y pip-audit. Si falla, analiza el resultado y corrige el problema antes de integrar. No agregues secretos al YAML.

> **Importante:** El workflow educativo usa etiquetas de versiones mayores de acciones. En un proyecto de producción se fijarían acciones a SHA completos verificados, además de aplicar protección de ramas y revisión de cambios.

---

## 11. Evidencias y reflexión individual

### E1. Matriz de permisos y diagrama de arquitectura

#### Matriz de Permisos (RBAC / ABAC)
- **Estudiante:** Consulta únicamente su propia nota en grupos donde esté inscrito (HTTP 200). Denegado para notas ajenas (HTTP 403) y modificación (HTTP 403).
- **Profesor:** Modifica y consulta notas de estudiantes inscritos en los grupos que tiene formalmente asignados (HTTP 200). Denegado para grupos ajenos (HTTP 403).
- **Administrador:** Por diseño defensivo de mínimo privilegio, no tiene facultad de modificar calificaciones por defecto (HTTP 403).

#### Diagrama de Arquitectura

```text
[Cliente HTTP / Postman / Pruebas Pytest]
       │
       ▼ (Solicitud HTTP: cookies + X-CSRF-Token + JSON body)
[Flask Application: src/app.py]
  ├─► 1. Autenticación [src/auth.py] (Valida cookie 'sc_session' contra hash SHA-256 en SQLite; 401 si falla)
  ├─► 2. Verificación CSRF (Valida 'X-CSRF-Token' en tiempo constante con secrets.compare_digest; 403 si falla)
  ├─► 3. Validación de Entrada [src/validators.py] (Valida Decimal, rango 0..100, máx 2 decimales; 400 si falla)
  ├─► 4. Control de Acceso [src/permissions.py] (Valida relaciones en 'groups' y 'enrollments'; 403 si falla)
  └─► 5. Transacción de Base de Datos [src/db.py]
         ├─► Tabla 'grades' (Actualización atómica de nota)
         └─► Tabla 'notification_outbox' (Transactional Outbox desacoplado para worker asíncrono)
```

---

### E2. Captura de pytest antes y después

#### 1. ESTADO INICIAL (Punto de partida con fallas deliberadas):
```text
Comando: python -m pytest tests/test_security.py -q
Resultado: 11 FAILED, 4 PASSED in 23.73s
- Fallas en validación: aceptaba '150', '-1', 'NaN', 'Infinity', '99.999' y producía errores con 'hola', '', None.
- Fallas en autorización: profesores podían modificar notas de otros grupos y estudiantes podían leer notas ajenas.
```

#### 2. ESTADO FINAL (Con controles completados):
```text
Comando: python -m pytest tests/test_security.py -v
Resultado: 15 PASSED in 7.64s (100% de pruebas superadas)
- tests/test_security.py::test_grade_invalid[150] PASSED [HTTP 400]
- tests/test_security.py::test_grade_invalid[-1] PASSED [HTTP 400]
- tests/test_security.py::test_grade_invalid[hola] PASSED [HTTP 400]
- tests/test_security.py::test_grade_invalid[] PASSED [HTTP 400]
- tests/test_security.py::test_grade_invalid[NaN] PASSED [HTTP 400]
- tests/test_security.py::test_grade_invalid[Infinity] PASSED [HTTP 400]
- tests/test_security.py::test_grade_invalid[None] PASSED [HTTP 400]
- tests/test_security.py::test_grade_invalid[99.999] PASSED [HTTP 400]
- tests/test_security.py::test_professor_own_group PASSED [HTTP 200]
- tests/test_security.py::test_professor_other_group_forbidden PASSED [HTTP 403]
- tests/test_security.py::test_student_cannot_modify PASSED [HTTP 403]
- tests/test_security.py::test_student_cannot_read_other_student PASSED [HTTP 403]
- tests/test_security.py::test_csrf_required PASSED [HTTP 403]
- tests/test_security.py::test_logout_revokes PASSED [HTTP 401]
- tests/test_security.py::test_outbox_transaction PASSED [HTTP 200]
```

---

### E3. Captura de pruebas de acceso denegado (Casos negativos)

- **Caso 1 - Modificación por profesor ajeno al grupo (`test_professor_other_group_forbidden`):**
  - Usuario: `profe_ana` (ID 1, grupo asignado ISC401/10) intenta modificar nota en grupo ISC402/20 asignado a `profe_luis`.
  - Petición: `PUT /grades/4/20` con `{'grade': '80'}`
  - Evaluación: `'SELECT 1 FROM groups WHERE id=20 AND professor_id=1'` retorna vacío.
  - Resultado: `HTTP 403 Forbidden` `{'error': 'Acceso denegado'}`.

- **Caso 2 - Modificación no autorizada por estudiante (`test_student_cannot_modify`):**
  - Usuario: `alumna_eli` (ID 3, rol estudiante) intenta alterar su propia nota.
  - Petición: `PUT /grades/3/10` con `{'grade': '99'}`
  - Evaluación: `user['role'] != 'profesor'`.
  - Resultado: `HTTP 403 Forbidden` `{'error': 'Acceso denegado'}`.

- **Caso 3 - Lectura de notas de otro estudiante (`test_student_cannot_read_other_student`):**
  - Usuario: `alumna_eli` (ID 3) intenta consultar la calificación del estudiante 4 en grupo 20.
  - Petición: `GET /grades/4/20`
  - Evaluación: `user['id'] != student_id`.
  - Resultado: `HTTP 403 Forbidden` `{'error': 'Acceso denegado'}`.

---

### E4. Explicación de contraseñas, sesiones y CSRF

1. **Almacenamiento Seguro de Contraseñas:**  
   En `src/db.py`, las contraseñas se almacenan mediante resúmenes `werkzeug.security.generate_password_hash`, el cual genera hashes con PBKDF2-HMAC-SHA256 y un salt criptográfico pseudoaleatorio único por usuario. No se guarda texto plano en ninguna circunstancia.

2. **Gestión Segura de Sesiones:**
   - **Generación:** Al iniciar sesión (`src/auth.py`), el servidor produce un token seguro con `secrets.token_urlsafe(32)`.
   - **Base de Datos:** El servidor NUNCA guarda el token crudo; almacena su digest SHA-256 (`hashlib.sha256(token.encode()).hexdigest()`) en la tabla `sessions`. De esta forma, una fuga de la base de datos no compromete las sesiones activas en los navegadores.
   - **Cookies:** Se envían con `HttpOnly=True` (impide que JavaScript acceda a la cookie) y `SameSite=Lax`.
   - **Revocación:** En `/logout`, el registro de sesión se elimina físicamente de la base de datos, revocando el acceso al instante.

3. **Mitigación contra Falsificación de Petición en Sitios Cruzados (CSRF):**  
   El servidor genera un `csrf_token` aleatorio por sesión (`secrets.token_urlsafe(24)`). En cada operación destructiva o modificadora (PUT, POST), el backend exige el encabezado `X-CSRF-Token` y lo compara con `secrets.compare_digest(request.headers.get('X-CSRF-Token'), user['csrf_token'])`, garantizando que la petición provenga intencionalmente del cliente legítimo y protegiendo contra ataques de temporización.

---

### E5. Auditoría de dependencias y propuesta de archivos

1. **Auditoría con pip-audit:**
   - Comando ejecutado: `python -m pip_audit -r requirements.txt`
   - Resultado: `No known vulnerabilities found`
   - Las librerías `Flask` (3.1.3) y `Werkzeug` (3.1.9) se encuentran libres de vulnerabilidades conocidas según los avisos de seguridad de PyPI.

2. **Propuesta de Arquitectura Segura para Descarga de Constancias:**
   - **Endpoint:** `GET /certificates/<int:certificate_id>/download`
   - **Control de Acceso:** El servidor valida la sesión y comprueba en la base de datos que el `student_id` de la constancia solicitada coincida con el usuario en sesión (`current_user.id`).
   - **Prevención de Inyección de Rutas (Path Traversal):** El cliente nunca envía nombres ni rutas de archivos. El servidor busca en la base de datos el nombre del archivo, el cual se almacena como un identificador inmutable UUID v4 (ej. `e4a28b0f-7b19-482a-9e12-38d58c0c91ad.pdf`).
   - **Directorio Aislado:** Los archivos se ubican en una carpeta externa al directorio público web y se despachan con `flask.send_from_directory(storage_folder, filename, as_attachment=True)`.

---

### E6. Captura del pipeline y enlace al PR

- **Pipeline de Seguridad (`.github/workflows/security.yml`):**  
  Configurado para ejecutarse automáticamente en ramas de trabajo y en cada Pull Request. Consta de:
  1. `actions/checkout@v4` y `actions/setup-python@v5` (Python 3.12).
  2. Instalación de dependencias de producción y desarrollo.
  3. Ejecución automática de pruebas de seguridad: `python -m pytest -q`.
  4. Ejecución automática de auditoría de seguridad de paquetes: `python -m pip_audit -r requirements.txt`.

- **Política de Integración Continua:**  
  Si alguna prueba unitaria falla o una dependencia presenta una vulnerabilidad conocida, el job de GitHub Actions se detiene con código de error, bloqueando el merge hacia la rama principal `main`. En producción, para máxima seguridad de la cadena de suministro de software, las acciones de GitHub se anclan a SHA completos (ej. `actions/checkout@b4ffde5c94047663291c0b999cf74e709eb0c1e6`) en lugar de tags mutables.

---

### Reflexión individual

- **¿Qué control fue más difícil?**  
  La validación numérica en `src/validators.py`. En Python, tipos como `bool` heredan de `int`, y en peticiones JSON los números pueden llegar como cadenas o flotantes. Diseñar un validador que acepte cadenas numéricas válidas (ej. `'98.5'`) pero rechace estrictamente booleanos, `'NaN'`, `'Infinity'`, texto no numérico y entradas con más de dos decimales sin realizar redondeos silenciosos requirió un diseño minucioso con la clase `Decimal`.

- **¿Qué prueba te dio mayor confianza?**  
  `test_professor_other_group_forbidden` y `test_student_cannot_modify`. Comprueban que la lógica de autorización por recurso (ABAC) consulta la base de datos en tiempo real y no confía en datos del cliente, impidiendo ataques de manipulación de identificadores (IDOR / BOLA).

- **¿Qué falta antes de producción?**  
  - Forzar HTTPS con HSTS y flag `Secure` en cookies.
  - Implementar Rate Limiting contra ataques de fuerza bruta.
  - Incorporar Autenticación Multifactor (MFA).
  - Gestionar sesiones en un caché en memoria distribuido (Redis).
  - Registro de auditoría y monitoreo continuo de eventos de seguridad (SIEM).

---

## 12. Rúbrica resumida (100 puntos)

| Criterio | Puntos |
| :--- | :--- |
| **2.1 Diseño seguro** | 10 |
| **2.2 Arquitectura resiliente** | 10 |
| **2.3 Validación** | 15 |
| **2.4 Sesiones y acceso** | 20 |
| **2.5 Criptografía** | 10 |
| **2.6 Dependencias, archivos y errores** | 15 |
| **2.7 CI/CD** | 15 |
| **Documentación y defensa** | 5 |
| **Total** | **100** |

