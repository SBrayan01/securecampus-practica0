import hashlib
import secrets
import time
from werkzeug.security import check_password_hash
from .db import connect

SESSION_SECONDS = 1800

def login(username, password, path=None):
    with connect(path) as con:
        user = con.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if user is None or not check_password_hash(user['password_hash'], password):
            return None
        token = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(24)
        digest = hashlib.sha256(token.encode()).hexdigest()
        con.execute('INSERT INTO sessions VALUES (?,?,?,?)',(digest,user['id'],csrf,int(time.time())+SESSION_SECONDS))
        return token,csrf

def session_user(token, path=None):
    if not token: return None
    digest=hashlib.sha256(token.encode()).hexdigest()
    with connect(path) as con:
        return con.execute('SELECT u.*,s.csrf_token FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires_at>?',(digest,int(time.time()))).fetchone()

def logout(token,path=None):
    if token:
        with connect(path) as con:
            con.execute('DELETE FROM sessions WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),))
