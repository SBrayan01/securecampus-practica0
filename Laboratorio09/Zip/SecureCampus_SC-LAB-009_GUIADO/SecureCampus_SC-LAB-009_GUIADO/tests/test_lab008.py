from .conftest import authenticate

def test_simulador_movil_disponible(client):
    response = client.get('/mobile-demo')
    assert response.status_code == 200
    assert b'DEMO-NO-ES-UN-TOKEN-REAL' in response.data

def test_salud_app(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}

def test_consulta_propia_permitida_desde_cliente(client):
    authenticate(client, 'alumna_eli')
    assert client.get('/grades/3/10').status_code == 200

def test_consulta_ajena_rechazada_desde_cliente(client):
    authenticate(client, 'alumna_eli')
    assert client.get('/grades/4/20').status_code == 403
