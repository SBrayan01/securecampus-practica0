import pytest
from .conftest import authenticate

@pytest.mark.parametrize('bad',['150','-1','hola','','NaN','Infinity',None,'99.999'])
def test_grade_invalid(client,bad):
    headers=authenticate(client,'profe_ana')
    assert client.put('/grades/3/10',json={'grade':bad},headers=headers).status_code==400

def test_professor_own_group(client):
    headers=authenticate(client,'profe_ana')
    res=client.put('/grades/3/10',json={'grade':'98.5'},headers=headers)
    assert res.status_code==200
    assert client.get('/grades/3/10').get_json()['grade']=='98.5'

def test_professor_other_group_forbidden(client):
    headers=authenticate(client,'profe_ana')
    assert client.put('/grades/4/20',json={'grade':'80'},headers=headers).status_code==403
    assert client.get('/grades/4/20').status_code==403

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

def test_logout_revokes(client):
    headers=authenticate(client,'profe_ana')
    assert client.post('/logout',headers=headers).status_code==200
    assert client.get('/grades/3/10').status_code==401

def test_outbox_transaction(client):
    from src.db import connect
    headers=authenticate(client,'profe_ana')
    assert client.put('/grades/3/10',json={'grade':'77'},headers=headers).status_code==200
    with connect(client.application.config['DB_PATH']) as con:
        assert con.execute('SELECT COUNT(*) FROM notification_outbox').fetchone()[0]==1
