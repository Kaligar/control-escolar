#herramientas
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
#base de datos
from config import config
from database.db import get_connection
#rutas para consultas
from routes import Alumno
from models.entities.user import User
from models.modelUser import ModelUser
from models.AlumnoModel import AlumnoModel
from models.calificacionModel import CalificacionModel
from models.maestroModel import MaestroModel
from models.ModelGrupo import ModelGrupo

app = Flask(__name__)

csrf = CSRFProtect()
Login_manager_app = LoginManager(app)

@Login_manager_app.user_loader
def load_user(id_usuario):
    return ModelUser.get_by_id(id_usuario)

@app.route('/')
def index():
    return redirect(url_for('Login'))

def redirect_based_on_role(role):
    role_routes = {
        'maestro': 'maestro',
        'estudiante': 'estudiante',
        'administrativo': 'administrativo',
    }
    
    # Convertimos el rol a minúsculas para hacer la comparación más robusta
    role = role.lower()
    
    if role in role_routes:
        return redirect(url_for(role_routes[role]))
    else:
        # Imprimir el rol para depuración
        print(f"Rol no reconocido: {role}")
        flash(f'Rol de usuario no reconocido: {role}')
        return render_template('auth/login.html')

@app.route('/login', methods=['GET', 'POST'])
def Login():
    logout_user()
    if request.method == 'POST':
        user = User(0, request.form['username'], request.form['password'], 0)
        model_user = ModelUser()
        logged_user = model_user.login(user)

        if logged_user:
            login_user(logged_user)
            # Imprimir el rol para depuración
            print(f"Rol del usuario: {logged_user.rol}")
            return redirect_based_on_role(logged_user.rol)
        else:
            flash('Usuario o contraseña incorrectos')
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('Login'))

@app.route('/maestro')
@login_required
def maestro():
    if current_user.rol.lower() != 'maestro':
        flash('No tienes permiso para acceder a esta página')
        return redirect(url_for('index'))
    
    try:
        id_maestro = MaestroModel.get_id_maestro_by_user_id(current_user.id)
        
        
        if id_maestro is None:
            flash('No se encontró un alumno asociado a este usuario')
            return redirect(url_for('index'))
        
        maestro_data = MaestroModel.get_maestro(id_maestro)
        grupo_data = ModelGrupo.get_grupo_maestro(id_maestro)
        
        
        return render_template('auth/maestro.html', 
                               maestro=maestro_data,
                               grupo=grupo_data)
    except Exception as e:
        
        app.logger.error(f"Error al obtener datos del maestro: {str(e)}")
        flash('Ocurrió un error al cargar los datos del maestro')
        return redirect(url_for('index'))

@app.route('/grupo/<string:grupo_id>')
@login_required
def grupo_detalle(grupo_id):
    app.logger.info(f"Accediendo al grupo: {grupo_id}")
    if current_user.rol.lower() != 'maestro':
        flash('No tienes permiso para acceder a esta página')
        return redirect(url_for('index'))
    
    try:
        # Obtener detalles del grupo
        grupo_data = ModelGrupo.get_grupo_detalle(grupo_id)
        
        # Obtener lista de alumnos del grupo
        alumnos = ModelGrupo.get_alumnos_grupo(grupo_id)
        
        return render_template('auth/grupo_detalle.html', 
                               grupo=grupo_data,
                               alumnos=alumnos)
    except Exception as e:
        app.logger.error(f"Error al obtener datos del grupo: {str(e)}")
        flash('Ocurrió un error al cargar los datos del grupo')
        return redirect(url_for('maestro'))
@app.route('/estudiante')
@login_required
def estudiante():
    if current_user.rol.lower() != 'estudiante':
        flash('No tienes permiso para acceder a esta página')
        return redirect(url_for('index'))
    
    try:
        id_alumno = AlumnoModel.get_id_alumno_by_user_id(current_user.id)
        
        if id_alumno is None:
            flash('No se encontró un alumno asociado a este usuario')
            return redirect(url_for('index'))
        
        alumno_data = AlumnoModel.get_alumno(id_alumno)
        calificaciones_parciales = CalificacionModel.calificaciones_parciales(id_alumno)
        calificaciones_anteriores = CalificacionModel.calificaciones_anteriores(id_alumno)  # Asumiendo que tienes este método
        
        # Imprime las calificaciones para depuración
        print("Calificaciones en curso:", calificaciones_parciales)
        print("Calificaciones anteriores:", calificaciones_anteriores)
        
        return render_template('auth/estudiante.html', 
                               alumno=alumno_data, 
                               calificaciones_parciales=calificaciones_parciales,
                               calificaciones_anteriores=calificaciones_anteriores)
    except Exception as e:
        app.logger.error(f"Error al obtener datos del estudiante: {str(e)}")
        flash('Ocurrió un error al cargar los datos del estudiante')
        return redirect(url_for('index'))

@app.route('/protected')
@login_required
def protected():
    return "<h1>esto es una vista para usuarios registrados"

def status_401(error):
    return redirect(url_for('Login'))

def page_not_found(error):
    return "<h1>not found page</h1>", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    # blueprints
    app.register_blueprint(Alumno.main, url_prefix='/api/movies')
    # Error handlers
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(401, status_401)
    app.run()