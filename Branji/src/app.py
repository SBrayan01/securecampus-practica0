import os
import secrets
from flask import Flask, request, jsonify, make_response
from .db import connect
from .auth import login, logout, session_user
from .validators import validar_calificacion
from .permissions import puede_modificar, puede_consultar

def create_app(db_path=None, testing=False):
    app=Flask(__name__)
    app.config.update(TESTING=testing, DB_PATH=db_path, SESSION_COOKIE_SECURE=not testing)

    def current():
        return session_user(request.cookies.get('sc_session'),app.config['DB_PATH'])
    def csrf_ok(user):
        return secrets.compare_digest(request.headers.get('X-CSRF-Token',''),user['csrf_token'])

    @app.post('/login')
    def do_login():
        data=request.get_json(silent=True) or {}
        result=login(data.get('username',''),data.get('password',''),app.config['DB_PATH'])
        if not result: return jsonify(error='Credenciales incorrectas'),401
        token,csrf=result
        response=make_response(jsonify(message='Sesión iniciada',csrf_token=csrf))
        response.set_cookie('sc_session',token,httponly=True,secure=app.config['SESSION_COOKIE_SECURE'],samesite='Lax',max_age=1800)
        return response

    @app.post('/logout')
    def do_logout():
        user=current()
        if not user:return jsonify(error='Autenticación requerida'),401
        if not csrf_ok(user):return jsonify(error='CSRF inválido'),403
        logout(request.cookies.get('sc_session'),app.config['DB_PATH'])
        response=make_response(jsonify(message='Sesión terminada'))
        response.delete_cookie('sc_session')
        return response

    @app.get('/grades/<int:student_id>/<int:group_id>')
    def get_grade(student_id,group_id):
        user=current()
        if not user:return jsonify(error='Autenticación requerida'),401
        with connect(app.config['DB_PATH']) as con:
            if not puede_consultar(user,student_id,group_id,con):return jsonify(error='Acceso denegado'),403
            row=con.execute('SELECT grade FROM grades WHERE student_id=? AND group_id=?',(student_id,group_id)).fetchone()
        if row is None:return jsonify(error='No encontrado'),404
        return jsonify(student_id=student_id,group_id=group_id,grade=row['grade'])

    @app.put('/grades/<int:student_id>/<int:group_id>')
    def put_grade(student_id,group_id):
        user=current()
        if not user:return jsonify(error='Autenticación requerida'),401
        if not csrf_ok(user):return jsonify(error='CSRF inválido'),403
        data=request.get_json(silent=True) or {}
        try: grade=validar_calificacion(data.get('grade'))
        except (ValueError,TypeError):return jsonify(error='Calificación inválida'),400
        with connect(app.config['DB_PATH']) as con:
            if not puede_modificar(user,student_id,group_id,con):return jsonify(error='Acceso denegado'),403
            con.execute('INSERT INTO grades(student_id,group_id,grade) VALUES(?,?,?) ON CONFLICT(student_id,group_id) DO UPDATE SET grade=excluded.grade',(student_id,group_id,str(grade)))
            con.execute('INSERT INTO notification_outbox(student_id,group_id,payload) VALUES(?,?,?)',(student_id,group_id,'Calificación actualizada'))
        return jsonify(message='Calificación guardada',grade=str(grade))

    return app

if __name__=='__main__':
    from .db import seed_demo
    seed_demo()
    create_app().run(debug=False)
