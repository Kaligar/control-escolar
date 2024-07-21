import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import config
from database.db import get_connection
from routes import Alumno
from models.entities.user import User
from models.modelUser import ModelUser
from models.AlumnoModel import AlumnoModel
from models.calificacionModel import CalificacionModel
from models.maestroModel import MaestroModel
from models.ModelGrupo import ModelGrupo

app = Flask(__name__)
app.config.from_object(config['development'])

csrf = CSRFProtect(app)
csrf.init_app(app)

# Solo para debugging, no uses en producción
app.config['WTF_CSRF_ENABLED'] = False
login_manager = LoginManager(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.INFO)

@login_manager.user_loader
def load_user(id_usuario):
    return ModelUser.get_by_id(id_usuario)

def redirect_based_on_role(role):
    role_routes = {
        'maestro': 'maestro',
        'estudiante': 'estudiante',
        'administrativo': 'administrativo',
    }
    role = role.lower()
    if role in role_routes:
        return redirect(url_for(role_routes[role]))
    else:
        app.logger.warning(f"Rol no reconocido: {role}")
        flash(f'Rol de usuario no reconocido: {role}')
        return render_template('auth/login.html')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['username'], request.form['password'], 0)
        logged_user = ModelUser().login(user)
        if logged_user:
            login_user(logged_user)
            app.logger.info(f"Rol del usuario: {logged_user.rol}")
            return redirect_based_on_role(logged_user.rol)
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/maestro')
@login_required
def maestro():
    if current_user.rol.lower() != 'maestro':
        flash('No tienes permiso para acceder a esta página')
        return redirect(url_for('index'))
    
    try:
        id_maestro = MaestroModel.get_id_maestro_by_user_id(current_user.id)
        logging.info(f"ID de maestro obtenido: {id_maestro}")
        
        if id_maestro is None:
            flash('No se encontró un maestro asociado a este usuario')
            return redirect(url_for('index'))
        
        maestro_data = MaestroModel.get_maestro(id_maestro)
        logging.info(f"Datos del maestro: {maestro_data}")
        
        grupo_data = ModelGrupo.get_grupo_maestro(id_maestro)
        logging.info(f"Datos del grupo: {grupo_data}")
        
        return render_template('auth/maestro.html', 
                               maestro=maestro_data,
                               grupo=grupo_data)
    
    except Exception as e:
        logging.error(f"Error inesperado en la ruta /maestro: {str(e)}", exc_info=True)
        flash('Ocurrió un error inesperado al cargar los datos del maestro')
        return redirect(url_for('index'))



@app.route('/grupo/<string:grupo_id>', methods=['GET', 'POST'])
@login_required
def grupo_detalle(grupo_id):
    if current_user.rol.lower() != 'maestro':
        flash('No tienes permiso para acceder a esta página')
        return redirect(url_for('index'))
    
    try:
        if request.method == 'POST':
            parcial = request.form.get('parcial')
            id_materia = request.form.get('id_materia')
            
            app.logger.info(f"Recibido POST para grupo {grupo_id}, parcial {parcial}, id_materia {id_materia}")
            
            if not id_materia:
                app.logger.error("id_materia está vacío")
                flash('Error: No se pudo obtener el ID de la materia', 'error')
                return redirect(url_for('grupo_detalle', grupo_id=grupo_id))
            
            for key, value in request.form.items():
                if key.startswith(('hacer_', 'saber_', 'ser_')):
                    tipo, matricula = key.split('_')
                    hacer = float(request.form.get(f'hacer_{matricula}', 0))
                    saber = float(request.form.get(f'saber_{matricula}', 0))
                    ser = float(request.form.get(f'ser_{matricula}', 0))
                    tipo = 'ordinario'
                    
                    id_alumno = request.form.get(f'id_alumno_{matricula}')
                    
                    app.logger.info(f"Procesando alumno: matricula {matricula}, id_alumno {id_alumno}")
                    
                    if id_alumno is None:
                        app.logger.error(f"id_alumno es None para matricula {matricula}")
                        continue
                    
                    try:
                        id_alumno = int(id_alumno)
                        id_materia = int(id_materia)
                    except ValueError as e:
                        app.logger.error(f"No se pudo convertir id_alumno ({id_alumno}) o id_materia ({id_materia}) a entero para matricula {matricula}: {str(e)}")
                        continue
                    
                    fase = parcial
                    calificacion = hacer * 0.6 + saber * 0.3 + ser * 0.1
                    
                    app.logger.info(f"Guardando calificación: id_alumno {id_alumno}, calificacion {calificacion}, tipo {tipo}, id_materia {id_materia}, fase {fase}")
                    
                    MaestroModel.guardar_calificacion(id_alumno, calificacion, tipo, id_materia, fase)
                    if fase == 'Parcial 3':
                        try:
                            resultado = CalificacionModel.insertar_o_actualizar_calificacion_final(id_alumno, id_materia)
                            if resultado:
                                print("Se insertó o actualizó la calificación final")
                            else:
                                print("No se insertó la calificación final (promedio <= 75)")
                        except Exception as e:
                            print(f"Ocurrió un error: {str(e)}")
            
            flash('Calificaciones guardadas exitosamente', 'success')
            return redirect(url_for('grupo_detalle', grupo_id=grupo_id))
        else:
            grupo_data = ModelGrupo.get_grupo_detalle(grupo_id)
            alumnos = ModelGrupo.get_alumnos_grupo(grupo_id)
            return render_template('auth/grupo_detalle.html', grupo=grupo_data, alumnos=alumnos)
    except Exception as e:
        app.logger.error(f"Error al procesar datos del grupo: {str(e)}", exc_info=True)
        flash('Ocurrió un error al procesar los datos del grupo', 'error')
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
        calificaciones_anteriores = CalificacionModel.calificaciones_anteriores(id_alumno)
        
        return render_template('auth/estudiante.html', 
                               alumno=alumno_data, 
                               calificaciones_parciales=calificaciones_parciales,
                               calificaciones_anteriores=calificaciones_anteriores)
    except Exception as e:
        app.logger.error(f"Error al obtener datos del estudiante: {str(e)}")
        flash('Ocurrió un error al cargar los datos del estudiante')
        return redirect(url_for('index'))
    
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