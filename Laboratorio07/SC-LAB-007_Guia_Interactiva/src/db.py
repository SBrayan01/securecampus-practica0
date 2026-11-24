import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'securecampus_demo.db'

def connect(path=None):
    con = sqlite3.connect(str(path or DB_PATH))
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con

def init_db(path=None):
    with connect(path) as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, role TEXT NOT NULL, password_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY, name TEXT NOT NULL, professor_id INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS enrollments (student_id INTEGER NOT NULL, group_id INTEGER NOT NULL, PRIMARY KEY(student_id, group_id));
        CREATE TABLE IF NOT EXISTS grades (student_id INTEGER NOT NULL, group_id INTEGER NOT NULL, grade TEXT NOT NULL, PRIMARY KEY(student_id, group_id));
        CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL, csrf_token TEXT NOT NULL, expires_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS notification_outbox (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL, group_id INTEGER NOT NULL, payload TEXT NOT NULL, sent INTEGER NOT NULL DEFAULT 0);
        """)

def seed_demo(path=None):
    from werkzeug.security import generate_password_hash
    init_db(path)
    with connect(path) as con:
        for uid, username, role in [(1,'profe_ana','profesor'),(2,'profe_luis','profesor'),(3,'alumna_eli','estudiante'),(4,'alumno_paz','estudiante'),(5,'admin_demo','administrador')]:
            con.execute('INSERT OR IGNORE INTO users VALUES (?,?,?,?)', (uid,username,role,generate_password_hash('Laboratorio2026!')))
        con.executemany('INSERT OR IGNORE INTO groups VALUES (?,?,?)',[(10,'ISC401',1),(20,'ISC402',2)])
        con.executemany('INSERT OR IGNORE INTO enrollments VALUES (?,?)',[(3,10),(4,20)])
        con.executemany('INSERT OR IGNORE INTO grades VALUES (?,?,?)',[(3,10,'85'),(4,20,'91')])
