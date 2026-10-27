def buscar_estudiante(nombre):
    conexion = sqlite3.connect("securecampus.db")
    cursor = conexion.cursor()

    consulta = (
        "SELECT id, nombre, correo "
        "FROM estudiantes "
        "WHERE nombre = ?"
    )
    
    cursor.execute(consulta, (nombre,))
    
    resultado = cursor.fetchall()
    conexion.close()

    return resultado