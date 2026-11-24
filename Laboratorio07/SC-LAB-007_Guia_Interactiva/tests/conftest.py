import pytest
from src.db import seed_demo
from src.app import create_app

@pytest.fixture
def client(tmp_path):
    path=tmp_path/'test.db'
    seed_demo(path)
    return create_app(path,testing=True).test_client()

def authenticate(client,username):
    res=client.post('/login',json={'username':username,'password':'Laboratorio2026!'})
    assert res.status_code==200
    return {'X-CSRF-Token':res.get_json()['csrf_token']}
