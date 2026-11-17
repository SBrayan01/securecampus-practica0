Search for `generate_password_hash|check_password_hash|hashlib\.sha256|token_urlsafe|set_...`

Search for `@app\.(post|get|put)|def validar_calificacion|def puede_modificar|def puede_c...`

## ¿Qué es este proyecto?

SecureCampus es una **API web educativa** hecha con Python y Flask. Sirve para consultar y modificar calificaciones de estudiantes, aplicando controles de seguridad.

No es una página web visual con HTML. Es principalmente un servidor que recibe solicitudes HTTP y devuelve respuestas JSON.

La aplicación usa:

- **Flask**: servidor web.
- **SQLite**: base de datos local.
- **Werkzeug**: hash de contraseñas.
- **pytest**: pruebas automatizadas.
- **pip-audit**: revisión de vulnerabilidades en dependencias.

---

## ¿Qué significa “API web”?

Una API permite que un cliente, por ejemplo un navegador, frontend o programa, se comunique con el servidor.

Ejemplo:

```text
Cliente                         Servidor Flask
   |                                |
   | POST /login                   |
   |------------------------------>|
   |                                |
   |   Respuesta JSON + cookie     |
   |<------------------------------|
```

El cliente envía una solicitud y el servidor responde.

En este proyecto se utilizan estas rutas:

| Método | Ruta | Función |
|---|---|---|
| `POST` | `/login` | Iniciar sesión |
| `POST` | `/logout` | Cerrar sesión |
| `GET` | `/grades/3/10` | Consultar una calificación |
| `PUT` | `/grades/3/10` | Modificar una calificación |

El código de las rutas está en `src/app.py`.

---

# Flujo completo del proyecto

## 1. Inicio de la aplicación

Cuando se ejecuta:

```powershell
python -m src.app
```

Flask inicia un servidor local. La base SQLite se encuentra en:

```text
securecampus_demo.db
```

La función `seed_demo()` crea usuarios, grupos, inscripciones y calificaciones ficticias en `src/db.py`.

Por ejemplo:

```text
profe_ana  -> profesor del grupo ISC401
profe_luis -> profesor del grupo ISC402
alumna_eli -> estudiante del grupo ISC401
alumno_paz -> estudiante del grupo ISC402
admin_demo -> administrador
```

---

## 2. Inicio de sesión

El usuario envía:

```http
POST /login
```

Con este JSON:

```json
{
  "username": "profe_ana",
  "password": "Laboratorio2026!"
}
```

El servidor:

1. Busca al usuario en SQLite.
2. Verifica la contraseña.
3. Genera un token de sesión.
4. Genera un token CSRF.
5. Guarda la sesión en la base de datos.
6. Envía el token de sesión dentro de una cookie.

La respuesta es similar a:

```json
{
  "message": "Sesión iniciada",
  "csrf_token": "token-csrf-generado"
}
```

La cookie se llama:

```text
sc_session
```

---

## 3. Consulta de una calificación

El estudiante o profesor solicita:

```http
GET /grades/3/10
```

Esto significa:

```text
student_id = 3
group_id   = 10
```

El servidor:

1. Lee la cookie `sc_session`.
2. Busca la sesión en la base de datos.
3. Comprueba que no haya expirado.
4. Identifica al usuario.
5. Verifica si tiene permiso para consultar.
6. Busca la calificación.
7. Devuelve una respuesta JSON.

Ejemplo:

```json
{
  "student_id": 3,
  "group_id": 10,
  "grade": "85"
}
```

Si el usuario no tiene sesión:

```http
401 Unauthorized
```

Si tiene sesión pero no permiso:

```http
403 Forbidden
```

---

## 4. Modificación de una calificación

Un profesor puede enviar:

```http
PUT /grades/3/10
```

Con este JSON:

```json
{
  "grade": "98.50"
}
```

También debe enviar:

```http
X-CSRF-Token: token-csrf-generado
```

El servidor valida en este orden:

```text
Sesión válida
    ↓
Token CSRF correcto
    ↓
Profesor autorizado para el grupo
    ↓
Estudiante inscrito en el grupo
    ↓
Calificación válida
    ↓
Guardar calificación
    ↓
Crear evento de notificación
```

La calificación solo se almacena si todas las validaciones pasan.

---

# ¿Cómo funcionan los permisos?

Los permisos se implementan en `src/permissions.py`.

## Profesor

Un profesor puede modificar una nota solamente si:

1. Su rol es `profesor`.
2. Está asignado al grupo.
3. El estudiante está inscrito en ese grupo.

Por ejemplo:

```text
profe_ana -> grupo 10 -> estudiante 3
```

Está permitido.

Pero:

```text
profe_ana -> grupo 20 -> estudiante 4
```

Está prohibido porque el grupo 20 pertenece a `profe_luis`.

## Estudiante

Un estudiante solo puede consultar su propia calificación.

```text
alumna_eli -> estudiante 3
```

Puede consultar:

```http
GET /grades/3/10
```

No puede consultar:

```http
GET /grades/4/20
```

Tampoco puede modificar calificaciones.

## Administrador

El administrador puede consultar, pero no puede modificar calificaciones por
defecto.

Esto es una decisión de mínimo privilegio: tener más privilegios administrativos
no significa automáticamente poder modificar notas.

---

# ¿Cómo funciona la validación?

La validación está en `src/validators.py`.

Se aceptan:

```text
0
85
99.50
100
```

Se rechazan:

```text
-1
150
NaN
Infinity
99.999
hola
""
None
True
False
```

Las reglas son:

- mínimo: `0`;
- máximo: `100`;
- máximo de dos decimales;
- no aceptar booleanos;
- no aceptar valores infinitos;
- no aceptar `NaN`;
- no redondear silenciosamente.

Por ejemplo, `99.999` no se convierte en `100.00`. Se rechaza.

La función devuelve un objeto `Decimal`, que es más apropiado que `float` para
valores decimales que requieren precisión.

---

# ¿Qué hashes utiliza el proyecto?

El proyecto utiliza **dos mecanismos diferentes**.

## 1. Hash de contraseñas

En `src/db.py:24` se usa:

```python
generate_password_hash('Laboratorio2026!')
```

Y en `src/auth.py:12`:

```python
check_password_hash(user['password_hash'], password)
```

### ¿Qué algoritmo utiliza?

Como no se especifica un algoritmo manualmente, Werkzeug utiliza su algoritmo
predeterminado.

En la versión instalada:

```text
Werkzeug 3.1.9
```

el algoritmo predeterminado de `generate_password_hash` es:

```text
scrypt
```

Por tanto, el hash de las contraseñas implementa:

```text
scrypt
```

con salt aleatorio y parámetros internos de costo.

Un hash guardado puede tener una estructura parecida a:

```text
scrypt:32768:8:1$...$...
```

La contraseña original no se almacena.

### ¿Cómo se verifica?

Cuando el usuario inicia sesión:

```text
Contraseña recibida
        ↓
check_password_hash()
        ↓
Compara contra el hash almacenado
        ↓
True o False
```

No se descifra la contraseña. Los hashes no se descifran.

---

## 2. Hash del token de sesión

En `src/auth.py:16` se usa:

```python
digest = hashlib.sha256(token.encode()).hexdigest()
```

Este mecanismo implementa:

```text
SHA-256
```

El flujo es:

```text
Token original:
secrets.token_urlsafe(32)

        ↓

SHA-256 del token

        ↓

Se almacena en:
sessions.token_hash
```

Cuando llega una solicitud posterior:

1. El servidor lee el token de la cookie.
2. Calcula nuevamente su SHA-256.
3. Busca ese hash en SQLite.
4. Verifica que la sesión no haya expirado.

La base de datos almacena algo parecido a:

```text
a8f4...c921
```

El token original no se almacena en SQLite.

### Diferencia entre ambos hashes

| Uso | Función | Algoritmo |
|---|---|---|
| Contraseñas | Proteger contraseñas | `scrypt` mediante Werkzeug |
| Tokens de sesión | No guardar el token original | `SHA-256` mediante `hashlib` |
| CSRF | Generar un token aleatorio | `secrets.token_urlsafe`, no es un hash |

Importante: SHA-256 es adecuado aquí para identificar el token aleatorio de
sesión, pero no debe utilizarse directamente para guardar contraseñas. Las
contraseñas necesitan funciones lentas y resistentes a ataques de diccionario,
como `scrypt`.

---

# ¿Qué es el token CSRF?

CSRF significa **Cross-Site Request Forgery**, o falsificación de solicitudes
entre sitios.

El proyecto genera un token CSRF con:

```python
secrets.token_urlsafe(24)
```

Ese token se devuelve al cliente después del login.

Para hacer operaciones que modifican información, como `PUT` o `POST`, el cliente
debe enviarlo:

```http
X-CSRF-Token: token-generado
```

El servidor lo compara con:

```python
secrets.compare_digest(...)
```

Si falta o no coincide, responde:

```http
403 CSRF inválido
```

Esto evita que otra página intente realizar cambios usando una sesión existente.

---

# ¿Qué protege la cookie?

La cookie se crea en `src/app.py:25`:

```python
response.set_cookie(
    'sc_session',
    token,
    httponly=True,
    secure=app.config['SESSION_COOKIE_SECURE'],
    samesite='Lax',
    max_age=1800
)
```

| Atributo | Función |
|---|---|
| `HttpOnly` | JavaScript no puede leer la cookie |
| `Secure` | En producción debe viajar solo por HTTPS |
| `SameSite=Lax` | Reduce solicitudes cruzadas |
| `max_age=1800` | Expira aproximadamente en 30 minutos |

En las pruebas locales `Secure` está desactivado porque se utiliza HTTP local.
En producción debe activarse HTTPS y `Secure`.

---

# ¿Qué ocurre al cerrar sesión?

Cuando se solicita:

```http
POST /logout
```

el servidor:

1. Verifica la sesión.
2. Verifica el CSRF.
3. Calcula el SHA-256 del token.
4. Elimina esa sesión de SQLite.
5. Borra la cookie del navegador.

Después del logout, aunque el cliente conserve el token, ya no aparece en la tabla
`sessions`, por lo que las solicitudes posteriores reciben:

```http
401 Unauthorized
```

---

# ¿Para qué sirve `notification_outbox`?

Cuando se modifica una nota, se realizan dos operaciones:

```text
Actualizar grades
Crear registro en notification_outbox
```

Esto permite que la calificación se guarde aunque el servicio externo de
notificaciones esté caído.

La aplicación no envía realmente el correo o notificación. Solo registra el
evento pendiente:

```text
student_id
group_id
payload
sent
```

Después, otro proceso podría leer los eventos pendientes y enviarlos.

---

# Resumen general

El proyecto es una API de calificaciones que demuestra:

```text
Login
  ↓
Cookie de sesión
  ↓
Validación de sesión
  ↓
Control CSRF
  ↓
Autorización por rol y recurso
  ↓
Validación de calificación
  ↓
Consulta o actualización en SQLite
  ↓
Registro de notificación
```

Los hashes principales son:

```text
Contraseñas: scrypt mediante Werkzeug
Tokens de sesión: SHA-256 mediante hashlib
Tokens CSRF: secrets.token_urlsafe, no hash
```

La aplicación está diseñada como laboratorio de seguridad, no como sistema listo
para producción. Antes de usarla en un entorno real necesitaría MFA, rate
limiting, HTTPS obligatorio, HSTS, sesiones distribuidas, monitoreo y auditoría
de seguridad.