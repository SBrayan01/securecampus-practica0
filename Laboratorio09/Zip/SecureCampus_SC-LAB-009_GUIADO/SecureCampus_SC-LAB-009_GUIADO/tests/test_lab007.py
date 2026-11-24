from .conftest import authenticate

def test_graphql_autorizado(client):
    authenticate(client, 'alumna_eli')
    r = client.post('/graphql', json={'query':'{ grade(studentId: 3, groupId: 10) { grade } }'})
    assert r.status_code == 200 and r.get_json()['data']['grade']['grade'] == '85'

def test_graphql_denegado(client):
    authenticate(client, 'alumna_eli')
    r = client.post('/graphql', json={'query':'{ grade(studentId: 4, groupId: 20) { grade } }'})
    assert r.status_code == 403

def test_profesor_estudiante_no_inscrito(client):
    h = authenticate(client, 'profe_ana')
    assert client.put('/grades/4/10', json={'grade':'80'}, headers=h).status_code == 403
    assert client.get('/grades/4/10').status_code == 403
