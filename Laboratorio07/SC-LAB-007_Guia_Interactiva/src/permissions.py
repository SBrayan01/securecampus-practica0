def inscrito(con, student_id, group_id):
    return con.execute("SELECT 1 FROM enrollments WHERE student_id=? AND group_id=?", (student_id, group_id)).fetchone() is not None

def profesor_del_grupo(con, professor_id, group_id):
    return con.execute("SELECT 1 FROM groups WHERE id=? AND professor_id=?", (group_id, professor_id)).fetchone() is not None

def puede_modificar(user, student_id, group_id, con):
    return (user["role"] == "profesor" and profesor_del_grupo(con, user["id"], group_id)
            and inscrito(con, student_id, group_id))

def puede_consultar(user, student_id, group_id, con):
    if not inscrito(con, student_id, group_id):
        return False
    if user["role"] == "estudiante":
        return user["id"] == student_id
    if user["role"] == "profesor":
        return profesor_del_grupo(con, user["id"], group_id)
    return False
