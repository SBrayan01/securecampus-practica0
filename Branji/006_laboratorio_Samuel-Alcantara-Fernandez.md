# SC-LAB-006: Laboratorio integrador

**Proyecto:** SecureCampus  
**Bloque:** 2 — Patrones, resiliencia, validación, sesiones, criptografía,
dependencias y CI/CD  
**Fuente principal:** `SC-LAB-006_Guia_del_Estudiante.docx`  
**Entorno:** local, con datos ficticios

## 1. Propósito y reglas del laboratorio

SecureCampus es una API Flask de calificaciones con una base SQLite que se
crea con datos de demostración. El objetivo no es construir toda la aplicación,
sino completar controles de seguridad, demostrar su funcionamiento con pruebas
y explicar las decisiones de diseño.

Las credenciales del ejercicio son ficticias y solo deben usarse localmente:

| Usuario | Rol | Grupo o recurso |
|---|---|---|
| `profe_ana` | Profesor | `ISC401`, id `10` |
| `profe_luis` | Profesor | `ISC402`, id `20` |
| `alumna_eli` | Estudiante | `ISC401`, estudiante id `3` |
| `alumno_paz` | Estudiante | `ISC402`, estudiante id `4` |
| `admin_demo` | Administrador | Sin permiso predeterminado para modificar notas |

La contraseña ficticia es `Laboratorio2026!`. No debe usarse en producción.

### Comandos de preparación y ejecución

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
python -m src.app
```

Cada prueba genera su propia base temporal. La aplicación crea
`securecampus_demo.db` cuando se inicia directamente.

## 2. Distribución de responsabilidades

| Rol del equipo | Responsabilidad |
|---|---|
| Arquitectura | Matriz de riesgos, flujo y diseño ante fallas |
| Backend | Validación, SQL parametrizado y errores |
| Identidad y acceso | Autenticación, sesiones, CSRF, permisos y pruebas negativas |
| Calidad / DevSecOps | Pruebas, dependencias, auditoría y CI |

## 3. Actividad A — Diseño seguro (2.1)

### 3.1 Flujo de actualización de una calificación

```text
Cliente
  |
  v
PUT /grades/<student_id>/<group_id>
  |
  v
Autenticación: cookie sc_session vigente
  |
  +-- falla --> 401 Autenticación requerida
  |
  v
CSRF: header X-CSRF-Token
  |
  +-- falla --> 403 CSRF inválido
  |
  v
Autorización: profesor asignado + estudiante inscrito
  |
  +-- falla --> 403 Acceso denegado
  |
  v
Validación: Decimal, rango 0..100 y máximo 2 decimales
  |
  +-- falla --> 400 Calificación inválida
  |
  v
Transacción SQLite:
  grades UPDATE/INSERT
  notification_outbox INSERT
  |
  v
200 Calificación guardada
```

El orden es importante. La autorización se realiza antes de modificar la base
de datos y no se puede sustituir por una degradación permisiva. La notificación
no bloquea la calificación porque el envío es un proceso independiente; el
evento queda guardado en `notification_outbox` para procesarse posteriormente.

### 3.2 Matriz de riesgos y controles

| Riesgo o falla | Control propuesto | Evidencia o prueba |
|---|---|---|
| Profesor de otro grupo intenta modificar una nota | Consultar `groups.professor_id` usando el id de la sesión y comprobar también `enrollments` | `test_professor_other_group_forbidden` devuelve 403 |
| Estudiante intenta modificar una nota | `puede_modificar` solo acepta el rol `profesor` | `test_student_cannot_modify` devuelve 403 |
| Estudiante consulta a otro estudiante | Comparar el usuario autenticado con `student_id` solicitado | `test_student_cannot_read_other_student` devuelve 403 |
| Servicio de notificaciones no disponible | Guardar el evento en `notification_outbox` dentro de la transacción | `test_outbox_transaction` confirma el evento |
| Calificación inválida | Convertir con `Decimal`, validar finitud, rango y precisión | `test_grade_invalid` y `test_grade_rejects_non_decimal_or_excess_precision` |
| Sesión revocada o inexistente | Consultar la sesión por hash y expiración antes de cada solicitud | `test_logout_revokes` y `test_missing_session_is_unauthorized` |
| Petición de cambio sin CSRF | Comparar `X-CSRF-Token` con `secrets.compare_digest` | `test_csrf_required` y `test_logout_requires_csrf` |
| Inyección SQL | Usar consultas con parámetros `?` | Consultas de `src/app.py` y `src/permissions.py` |

### 3.3 Preguntas de la actividad A

**¿Por qué la notificación no debe bloquear la calificación?**  
Porque son procesos independientes. Si el servicio de notificaciones falla, el
profesor todavía debe poder guardar una calificación válida. El evento se
conserva en `notification_outbox` para reintentar el envío sin perder la
actualización.

**¿Por qué no puede aplicarse la misma degradación al control de autorización?**  
La autorización es un control de seguridad obligatorio. Si el sistema no puede
comprobar que el profesor tiene permiso sobre el grupo y el estudiante, debe
rechazar la operación. Permitirla sin verificar el permiso produciría una
modificación no autorizada.

## 4. Actividad B — Validación (2.3)

La función `validar_calificacion` de [src/validators.py](src/validators.py)
devuelve un `Decimal` o lanza `ValueError`. El endpoint convierte ese error en
HTTP 400 y no almacena la entrada inválida.

### 4.1 Reglas implementadas

| Regla | Implementación |
|---|---|
| Rechazar nulos | `None` se rechaza antes de convertir |
| Rechazar booleanos | `bool` se filtra porque hereda de `int` en Python |
| Aceptar valores numéricos | Conversión controlada a `Decimal` |
| Rechazar texto vacío | Se eliminan espacios externos y se comprueba que no quede vacío |
| Rechazar texto no numérico | `InvalidOperation` se convierte en `ValueError` |
| Rechazar `NaN` e infinito | `is_nan()` e `is_infinite()` |
| Validar rango | `0 <= valor <= 100` |
| Validar precisión | Exponente mínimo de -2; no se redondea silenciosamente |

### 4.2 Casos solicitados por la guía

| Entrada | Esperado | Resultado |
|---|---|---|
| `85` | Aceptar | 200; se almacena como `Decimal('85')` |
| `99.50` | Aceptar | 200; se conserva como `Decimal('99.50')` |
| `150` | Rechazar | 400; supera el límite superior |
| `NaN` | Rechazar | 400; valor especial no numérico |
| `99.999` | Rechazar | 400; supera dos decimales |

### 4.3 Casos adicionales probados

| Entrada | Motivo de rechazo |
|---|---|
| `-1` | Menor que cero |
| `-0.01` | Menor que cero |
| `Infinity` | No es finito |
| `hola` | Texto no numérico |
| `''` y `'  '` | Cadena vacía |
| `None` | Valor nulo |
| `True` y `False` | Booleanos |
| `'1.000'` | Más de dos decimales |
| `'1e3'` | Notación científica no aceptada por la regla de precisión |

También se probaron los límites válidos `0`, `100`, `'0'`, `'100'` y `'99.50'`.

### 4.4 Pregunta de reflexión sobre validación

**¿Qué control fue más difícil?**  
La validación decimal. En Python, `bool` hereda de `int`, y los valores JSON
pueden llegar como números o cadenas. Fue necesario aceptar números válidos sin
aceptar booleanos, `NaN`, infinito, texto, valores fuera de rango o más de dos
decimales. La solución usa `Decimal` y rechaza la precisión excesiva en lugar
de redondear silenciosamente.

## 5. Actividad C — Acceso por recurso (2.4)

Las funciones de [src/permissions.py](src/permissions.py) consultan siempre
las asignaciones del servidor. No confían en que el cliente indique un grupo
autorizado.

### 5.1 Matriz de permisos solicitada

| Rol | Consultar calificación (GET) | Modificar calificación (PUT) |
|---|---|---|
| Profesor | Sí, solo estudiantes de un grupo que imparte | Sí, solo estudiantes inscritos en un grupo que imparte |
| Estudiante | Sí, únicamente su propia calificación | No, HTTP 403 |
| Administrador | Sí, puede consultar | No por defecto, HTTP 403 |
| Sin sesión | No, HTTP 401 | No, HTTP 401 |

### 5.2 Casos de acceso

| Caso | HTTP esperado | Resultado verificado |
|---|---:|---|
| `profe_ana` modifica alumno 3 del grupo 10 | 200 | Permitido y genera outbox |
| `profe_ana` modifica alumno 4 del grupo 20 | 403 | Denegado: el grupo pertenece a `profe_luis` |
| `profe_ana` consulta su grupo 10 | 200 | Permitido |
| `alumna_eli` modifica su propia nota | 403 | Denegado por rol |
| `alumna_eli` consulta alumno 4 del grupo 20 | 403 | Denegado por identidad |
| `alumna_eli` consulta alumno 3 del grupo 10 | 200 | Permitido |
| `admin_demo` consulta una nota | 200 | Permitido |
| `admin_demo` modifica una nota | 403 | Denegado por defecto |
| Petición sin sesión | 401 | Denegada |
| PUT sin CSRF | 403 | Denegada |

### 5.3 Pregunta de seguridad

**¿Qué riesgo se evita al consultar las asignaciones en la base del servidor?**  
Se evita IDOR/BOLA: un usuario no puede cambiar los identificadores enviados en
la URL para acceder a otro grupo o estudiante. La decisión se toma con
`groups.professor_id` y `enrollments`, no con datos confiados del cliente.

## 6. Actividad D — Criptografía y sesiones (2.4–2.5)

### 6.1 Qué se almacena y qué no

| Elemento | Implementación | Se almacena |
|---|---|---|
| Contraseña | `generate_password_hash` en `db.py` | Hash con salt y función costosa |
| Verificación | `check_password_hash` en `auth.py` | No se guarda la contraseña recibida |
| Token de sesión | `secrets.token_urlsafe(32)` | Solo su SHA-256 en `sessions.token_hash` |
| Token CSRF | `secrets.token_urlsafe(24)` | Token asociado a la sesión |
| Cookie | `sc_session` | Token de sesión para identificar la sesión |

La base de datos no necesita guardar el token de sesión original: si se filtra
SQLite, el atacante no obtiene directamente el valor que debe presentar en la
cookie.

### 6.2 Atributos de la cookie y sesión

| Control | Evidencia | Propósito |
|---|---|---|
| `HttpOnly=True` | Cookie `sc_session` | Impide que JavaScript lea la cookie con `document.cookie` |
| `SameSite='Lax'` | Cookie de login | Reduce envíos cruzados de la cookie |
| `Secure` | Activado fuera de `testing` | Obliga HTTPS en producción |
| Expiración de cookie | `max_age=1800` | Limita la duración del navegador |
| Expiración de sesión | `expires_at` | Rechaza sesiones vencidas |
| Logout | `DELETE FROM sessions` | Revoca el token |

### 6.3 Hash frente a cifrado

| Característica | Hash | Cifrado |
|---|---|---|
| Dirección | Unidireccional | Bidireccional |
| Recuperación del original | No se debe poder recuperar | Sí, con una clave |
| Uso en este proyecto | Contraseñas y token de sesión | No se usa para almacenar contraseñas |
| Objetivo | Verificar sin guardar el secreto original | Proteger datos que después deben leerse |

### 6.4 Preguntas de la guía

**¿Cuál es la diferencia entre hash de contraseña y cifrado?**  
El hash es una función unidireccional; busca impedir la recuperación del texto
original y usa salt y un algoritmo costoso como PBKDF2. El cifrado es
bidireccional y permite recuperar el dato con una clave para que una entidad
autorizada lo lea.

**¿Qué atributo impide que JavaScript lea la cookie?**  
`HttpOnly=True` en `sc_session`. Esto bloquea `document.cookie` y reduce el robo
de sesión mediante XSS.

**¿Qué limitaciones presenta el ejemplo frente a producción?**  

1. Usa SQLite local en vez de un almacén distribuido como Redis.
2. No incorpora MFA/2FA.
3. No implementa rate limiting contra fuerza bruta en `/login`.
4. En pruebas locales `Secure` está desactivado; producción debe usar HTTPS,
   HSTS y cookies seguras.
5. Falta auditoría y monitoreo continuo de eventos de seguridad.

## 7. Actividad E — Dependencias, errores y archivos (2.6)

### 7.1 Dependencias

`requirements.txt` declara Flask y Werkzeug; `requirements-dev.txt` declara
pytest y pip-audit.

| Paquete | Restricción declarada | Versión instalada en la evidencia | Resultado |
|---|---|---:|---|
| Flask | `>=3.1,<4` | 3.1.3 | Sin vulnerabilidades conocidas |
| Werkzeug | `>=3.1,<4` | 3.1.9 | Sin vulnerabilidades conocidas |
| pytest | `>=8,<10` | 9.1.1 | Herramienta de pruebas |
| pip-audit | `>=2.8,<3` | 2.10.1 | Herramienta de auditoría |

Comando ejecutado:

```powershell
.\.venv\Scripts\python.exe -m pip_audit -r requirements.txt
```

Salida obtenida:

```text
No known vulnerabilities found
```

### 7.2 SQL parametrizado y manejo de errores

Las consultas de `src/app.py` y `src/permissions.py` usan parámetros `?`, por
ejemplo:

```python
con.execute(
    'SELECT grade FROM grades WHERE student_id=? AND group_id=?',
    (student_id, group_id),
)
```

Esto evita concatenar directamente datos de la URL o del JSON en una consulta.
Los errores de validación devuelven `400`, los accesos no autorizados `403` y
la ausencia de sesión `401`. La prueba
`test_error_response_does_not_expose_internal_traceback` confirma que la
respuesta no contiene `traceback`.

### 7.3 Propuesta de descarga de constancia

La guía solicita proponerla sin implementarla. El diseño seguro sería:

1. Recibir únicamente un `certificate_id`, no una ruta.
2. Autenticar la sesión.
3. Consultar en la base de datos el propietario y la ruta registrada.
4. Autorizar que el usuario sea el propietario o tenga un rol permitido.
5. Resolver la ruta dentro de un directorio permitido.
6. Evitar path traversal y comprobar que el archivo existe.
7. Servir el archivo con `send_file` después de todas las verificaciones.

Nunca se debe aceptar una ruta arbitraria enviada por el cliente.

## 8. Actividad F — CI/CD (2.7)

El workflow versionado en `.github/workflows/security.yml` se ejecuta en
`push` y `pull_request`, usa Python 3.12 y realiza:

| Paso | Propósito |
|---|---|
| `actions/checkout@v4` | Descargar el código |
| `actions/setup-python@v5` | Preparar Python 3.12 |
| Install | Instalar dependencias de producción y desarrollo |
| Tests | Ejecutar `python -m pytest -q` |
| Dependency audit | Ejecutar `python -m pip_audit -r requirements.txt` |

El workflow no contiene secretos. Para producción se recomienda fijar las
acciones a SHA completos verificados, proteger la rama principal, exigir
revisión de cambios y conservar los resultados de auditoría.

## 9. Evidencias y resultados

### E1. Matriz de permisos y arquitectura

La matriz completa está en la sección 5. El flujo de arquitectura está en la
sección 3 y muestra dónde se rechaza una solicitud antes de tocar la base de
datos.

### E2. Antes y después de las pruebas

El reporte inicial `ERRORES_INICIALES_Y_SOLUCIONES.md` registra:

```text
Antes: 11 failed, 4 passed
```

Los fallos iniciales correspondían a ocho entradas inválidas y tres problemas
de autorización: profesor en grupo ajeno, estudiante modificando y estudiante
consultando a otro estudiante.

Después de corregir las validaciones y permisos, la evidencia anterior registró
15 pruebas exitosas. Con las pruebas adicionales implementadas para este
reporte, el resultado actual es:

```text
35 passed in 67.16s
```

### E3. Pruebas de acceso denegado

Las pruebas negativas cubren profesor en otro grupo, estudiante modificando,
estudiante consultando a otro usuario, administrador modificando, ausencia de
sesión, ausencia de CSRF y cierre de sesión.

### E4. Contraseñas, sesiones y CSRF

Las contraseñas se derivan con Werkzeug y no se guardan en texto plano. La
cookie es `HttpOnly`, `SameSite=Lax` y se vuelve `Secure` fuera del modo de
pruebas. Los cambios de estado requieren `X-CSRF-Token`, que se verifica con
`secrets.compare_digest` para evitar comparaciones vulnerables a timing attacks.

### E5. Auditoría de dependencias y propuesta de archivos

La auditoría local terminó con `No known vulnerabilities found`. La propuesta
de descarga segura de constancias está documentada en la sección 7.3.

### E6. CI/CD y Pull Request

El workflow queda descrito en la sección 8. El historial Git del proyecto
contiene commits relacionados con correcciones, documentación y configuración
del laboratorio. La ejecución reproducible de CI debe demostrar pytest y
pip-audit sin fallos.

## 10. Reflexión individual

**¿Qué control fue más difícil?**  
La validación numérica, por la diferencia entre enteros, booleanos, cadenas,
flotantes, valores especiales y precisión decimal.

**¿Qué prueba dio mayor confianza?**  
`test_professor_other_group_forbidden` y `test_student_cannot_modify`, porque
comprueban autorización por recurso y bloquean modificaciones tipo IDOR/BOLA.

**¿Qué falta antes de producción?**  
HTTPS obligatorio con HSTS y `Secure`, MFA, rate limiting, sesiones distribuidas
con expiración, logs de auditoría, monitoreo y acciones de GitHub fijadas a SHA.

## 11. Rúbrica cubierta

| Criterio | Evidencia en este reporte |
|---|---|
| 2.1 Diseño seguro | Flujo y matriz de riesgos de la sección 3 |
| 2.2 Arquitectura resiliente | `notification_outbox` y preguntas respondidas |
| 2.3 Validación | Reglas, tablas y pruebas de la sección 4 |
| 2.4 Sesiones y acceso | Matriz de permisos, sesiones, CSRF y logout |
| 2.5 Criptografía | Comparación hash/cifrado y almacenamiento de secretos |
| 2.6 Dependencias, archivos y errores | pip-audit, SQL parametrizado y constancias |
| 2.7 CI/CD | Workflow, pasos, auditoría y recomendaciones |
| Documentación y defensa | Evidencias E1–E6 y reflexión individual |
