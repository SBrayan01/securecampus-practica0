"""
Pruebas de seguridad para el rol ADMINISTRADOR (usuario `admin_demo`, id=5).

Reglas que se verifican (ver SC-LAB-006 y src/permissions.py):
  * El administrador SI puede CONSULTAR (GET) cualquier calificación.
  * El administrador NO puede MODIFICAR (PUT) calificaciones (mínimo privilegio -> 403).
  * El administrador sigue sujeto a las mismas defensas que cualquier usuario:
    autenticación, token CSRF y revocación de sesión en logout.

Datos de prueba (los crea `seed_demo` en conftest.py en una BD temporal):
  * Grupo 10 (ISC401, profe_ana)  -> alumna_eli (id 3) con nota '85'
  * Grupo 20 (ISC402, profe_luis) -> alumno_paz (id 4) con nota '91'
"""
import pytest
from .conftest import authenticate
from src.db import connect

ADMIN = 'admin_demo'


def contar_outbox(client):
    """Cuenta cuántas notificaciones hay en la tabla notification_outbox."""
    with connect(client.application.config['DB_PATH']) as con:
        return con.execute('SELECT COUNT(*) FROM notification_outbox').fetchone()[0]


# ---------------------------------------------------------------------------
# 1. Autenticación del administrador
# ---------------------------------------------------------------------------
def test_admin_login_ok(client):
    # authenticate() hace POST /login y ya comprueba internamente que sea 200.
    headers = authenticate(client, ADMIN)
    # El servidor debe devolver un token CSRF no vacío para usarlo en peticiones que cambian estado.
    assert headers['X-CSRF-Token']


def test_admin_wrong_password_rejected(client):
    # Con contraseña incorrecta no debe crearse sesión.
    res = client.post('/login', json={'username': ADMIN, 'password': 'incorrecta'})
    assert res.status_code == 401
    # Y como no hay cookie de sesión, cualquier consulta exige autenticación.
    assert client.get('/grades/3/10').status_code == 401


# ---------------------------------------------------------------------------
# 2. Consulta (GET): el administrador puede leer cualquier calificación
# ---------------------------------------------------------------------------
@pytest.mark.parametrize('student_id,group_id,esperado', [
    (3, 10, '85'),   # alumna de profe_ana
    (4, 20, '91'),   # alumno de profe_luis
])
def test_admin_can_read_any_grade(client, student_id, group_id, esperado):
    authenticate(client, ADMIN)  # el test_client guarda la cookie sc_session
    res = client.get(f'/grades/{student_id}/{group_id}')
    assert res.status_code == 200
    assert res.get_json()['grade'] == esperado


def test_admin_read_nonexistent_grade_404(client):
    # El alumno 3 no está en el grupo 20: el admin pasa el permiso,
    # pero el registro no existe, así que debe responder 404 (no 200 ni 500).
    authenticate(client, ADMIN)
    assert client.get('/grades/3/20').status_code == 404


# ---------------------------------------------------------------------------
# 3. Modificación (PUT): el administrador NO puede modificar notas
# ---------------------------------------------------------------------------
@pytest.mark.parametrize('student_id,group_id,original', [
    (3, 10, '85'),
    (4, 20, '91'),
])
def test_admin_cannot_modify_grade(client, student_id, group_id, original):
    headers = authenticate(client, ADMIN)
    # Envía CSRF válido y una nota válida: lo ÚNICO que debe frenarlo es el permiso.
    res = client.put(f'/grades/{student_id}/{group_id}', json={'grade': '100'}, headers=headers)
    assert res.status_code == 403
    # La nota en la BD debe seguir intacta.
    assert client.get(f'/grades/{student_id}/{group_id}').get_json()['grade'] == original


def test_admin_cannot_create_grade(client):
    # Intentar crear una nota en una combinación alumno/grupo inexistente (el PUT hace UPSERT).
    headers = authenticate(client, ADMIN)
    assert client.put('/grades/4/10', json={'grade': '70'}, headers=headers).status_code == 403
    # No se insertó nada: sigue sin existir.
    assert client.get('/grades/4/10').status_code == 404


def test_admin_denied_put_no_outbox(client):
    # Si la modificación se deniega, no debe generarse ninguna notificación
    # (la escritura en grades y outbox va en la misma transacción).
    headers = authenticate(client, ADMIN)
    client.put('/grades/3/10', json={'grade': '60'}, headers=headers)
    assert contar_outbox(client) == 0


# ---------------------------------------------------------------------------
# 4. CSRF y sesión también aplican al administrador
# ---------------------------------------------------------------------------
def test_admin_put_without_csrf_forbidden(client):
    # Tiene cookie de sesión válida pero NO envía la cabecera X-CSRF-Token.
    authenticate(client, ADMIN)
    assert client.put('/grades/3/10', json={'grade': '90'}).status_code == 403


def test_admin_put_with_wrong_csrf_forbidden(client):
    # Envía un token CSRF falso.
    authenticate(client, ADMIN)
    res = client.put('/grades/3/10', json={'grade': '90'}, headers={'X-CSRF-Token': 'falso'})
    assert res.status_code == 403


def test_admin_logout_without_csrf_forbidden(client):
    # El logout también es una acción que cambia estado: sin CSRF se rechaza
    # y la sesión sigue activa.
    authenticate(client, ADMIN)
    assert client.post('/logout').status_code == 403
    assert client.get('/grades/3/10').status_code == 200


def test_admin_logout_revokes(client):
    headers = authenticate(client, ADMIN)
    assert client.post('/logout', headers=headers).status_code == 200
    # Tras cerrar sesión, la sesión se borró en el servidor: ya no puede consultar.
    assert client.get('/grades/3/10').status_code == 401


def test_admin_stolen_cookie_after_logout_is_useless(client):
    # Simula que alguien copió la cookie antes del logout y la reutiliza después.
    headers = authenticate(client, ADMIN)
    cookie = client.get_cookie('sc_session').value
    client.post('/logout', headers=headers)
    client.set_cookie('sc_session', cookie)  # reinyecta la cookie robada
    assert client.get('/grades/3/10').status_code == 401

