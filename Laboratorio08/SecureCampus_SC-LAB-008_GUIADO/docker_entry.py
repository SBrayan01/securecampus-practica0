from src.db import seed_demo
from src.app import create_app

seed_demo()
app = create_app()
