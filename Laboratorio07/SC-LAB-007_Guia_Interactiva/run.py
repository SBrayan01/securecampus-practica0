from src.db import seed_demo
from src.app import create_app

if __name__ == '__main__':
    seed_demo()
    print('Abre http://127.0.0.1:5000 en tu navegador')
    create_app().run(host='127.0.0.1', port=5000, debug=False)
