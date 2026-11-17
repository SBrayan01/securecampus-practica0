import pytest
from .conftest import authenticate
from src.db import connect

@pytest.mark.parametrize('bad',['150','-1','hola','','NaN','Infinity',None,'99.999'])
def test_grade_invalid(client,bad):
    headers=authenticate(client,'profe_ana')
    assert client.put('/grades/3/10',json={'grade':bad},headers=headers).status_code==400


@pytest.mark.parametrize('valid', [0, 100, '0', '100', '99.50'])
def test_grade_valid_boundaries(client, valid):
    headers = authenticate(client, 'profe_ana')
    response = client.put('/grades/3/10', json={'grade': valid}, headers=headers)
    assert response.status_code == 200
    assert response.get_json()['grade'] == str(valid)


@pytest.mark.parametrize('bad', [True, False, '  ', '1e3', '1.000', '-0.01'])
def test_grade_rejects_non_decimal_or_excess_precision(client, bad):
    headers = authenticate(client, 'profe_ana')
    response = client.put('/grades/3/10', json={'grade': bad}, headers=headers)
    assert response.status_code == 400

def test_professor_own_group(client):
    headers=authenticate(client,'profe_ana')
    res=client.put('/grades/3/10',json={'grade':'98.5'},headers=headers)
    assert res.status_code==200
    assert client.get('/grades/3/10').get_json()['grade']=='98.5'

def test_professor_other_group_forbidden(client):
    headers=authenticate(client,'profe_ana')
    assert client.put('/grades/4/20',json={'grade':'80'},headers=headers).status_code==403
    assert client.get('/grades/4/20').status_code==403


def test_professor_can_read_assigned_group(client):
    authenticate(client, 'profe_ana')
    response = client.get('/grades/3/10')
    assert response.status_code == 200


def test_admin_cannot_modify_grades(client):
    headers = authenticate(client, 'admin_demo')
    response = client.put('/grades/3/10', json={'grade': '90'}, headers=headers)
    assert response.status_code == 403


def test_admin_can_read_grades(client):
    authenticate(client, 'admin_demo')
    response = client.get('/grades/3/10')
    assert response.status_code == 200

def test_student_cannot_modify(client):
    headers=authenticate(client,'alumna_eli')
    assert client.put('/grades/3/10',json={'grade':'99'},headers=headers).status_code==403

def test_student_cannot_read_other_student(client):
    authenticate(client,'alumna_eli')
    assert client.get('/grades/4/20').status_code==403
    assert client.get('/grades/3/10').status_code==200

def test_csrf_required(client):
    authenticate(client,'profe_ana')
    assert client.put('/grades/3/10',json={'grade':'90'}).status_code==403


def test_missing_session_is_unauthorized(client):
    assert client.get('/grades/3/10').status_code == 401
    assert client.put('/grades/3/10', json={'grade': '90'}).status_code == 401


def test_logout_requires_csrf(client):
    authenticate(client, 'profe_ana')
    assert client.post('/logout').status_code == 403

def test_logout_revokes(client):
    headers=authenticate(client,'profe_ana')
    assert client.post('/logout',headers=headers).status_code==200
    assert client.get('/grades/3/10').status_code==401


def test_session_cookie_is_httponly_and_secure_in_production(client):
    response = client.post(
        '/login',
        json={'username': 'profe_ana', 'password': 'Laboratorio2026!'},
    )
    cookie = response.headers['Set-Cookie']
    assert 'HttpOnly' in cookie
    assert 'SameSite=Lax' in cookie
    assert 'Secure' not in cookie


def test_session_token_is_stored_as_a_hash(client):
    response = client.post(
        '/login',
        json={'username': 'profe_ana', 'password': 'Laboratorio2026!'},
    )
    token = response.headers['Set-Cookie'].split('sc_session=', 1)[1].split(';', 1)[0]
    with connect(client.application.config['DB_PATH']) as con:
        stored = con.execute('SELECT token_hash FROM sessions').fetchone()['token_hash']
    assert stored != token
    assert len(stored) == 64

def test_outbox_transaction(client):
    headers=authenticate(client,'profe_ana')
    assert client.put('/grades/3/10',json={'grade':'77'},headers=headers).status_code==200
    with connect(client.application.config['DB_PATH']) as con:
        assert con.execute('SELECT COUNT(*) FROM notification_outbox').fetchone()[0]==1


def test_invalid_grade_does_not_create_outbox_event(client):
    headers = authenticate(client, 'profe_ana')
    response = client.put('/grades/3/10', json={'grade': '99.999'}, headers=headers)
    assert response.status_code == 400
    with connect(client.application.config['DB_PATH']) as con:
        assert con.execute('SELECT COUNT(*) FROM notification_outbox').fetchone()[0] == 0


def test_error_response_does_not_expose_internal_traceback(client):
    headers = authenticate(client, 'profe_ana')
    response = client.put('/grades/3/10', json={'grade': 'not-a-number'}, headers=headers)
    assert response.status_code == 400
    assert 'traceback' not in response.get_data(as_text=True).lower()
