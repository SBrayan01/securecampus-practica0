from flask import abort, g

def puede_modificar(user, student_id, group_id, db):
    """
    Verifica si el usuario actual puede MODIFICAR (PUT) la calificación.
    
    Parámetros:
      user: Objeto sqlite3.Row con los datos del usuario autenticado (user['id'], user['role'])
      student_id: int / str ID del estudiante a modificar
      group_id: int / str ID del grupo
      db: Conexión activa a SQLite (sqlite3.Connection)
    """
    if not user:
        return False

    # Extraemos el ID y el ROL directamente del objeto user
    user_id = user['id']
    role = user['role']

    # 1. Solo los profesores pueden modificar calificaciones
    if role != 'profesor':
        return False

    # 2. Verificar que el profesor imparta clase en ese grupo
    assigned = db.execute(
        "SELECT 1 FROM groups WHERE professor_id = ? AND id = ?",
        (user_id, group_id)
    ).fetchone()

    if not assigned:
        return False

    # 3. Verificar que el estudiante esté inscrito en ese grupo
    enrolled = db.execute(
        "SELECT 1 FROM enrollments WHERE student_id = ? AND group_id = ?",
        (student_id, group_id)
    ).fetchone()

    return bool(enrolled)


def puede_consultar(user, student_id, group_id, db):
    """
    Verifica si el usuario actual puede CONSULTAR (GET) la calificación.
    
    Parámetros:
      user: Objeto sqlite3.Row con los datos del usuario autenticado (user['id'], user['role'])
      student_id: int / str ID del estudiante
      group_id: int / str ID del grupo
      db: Conexión activa a SQLite (sqlite3.Connection)
    """
    if not user:
        return False

    user_id = user['id']
    role = user['role']

    # 1. Estudiantes: solo pueden consultar su propia calificación
    if role == 'estudiante':
        return int(user_id) == int(student_id)

    # 2. Profesores: deben ser el docente asignado a ese grupo
    if role == 'profesor':
        assigned = db.execute(
            "SELECT 1 FROM groups WHERE professor_id = ? AND id = ?",
            (user_id, group_id)
        ).fetchone()
        return bool(assigned)

    # 3. Administradores: pueden consultar
    if role == 'administrador':
        return True

    return False