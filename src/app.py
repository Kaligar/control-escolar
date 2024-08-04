import logging
from functools import wraps
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import config
from database.db import get_connection
import pdfkit
from routes import Alumno
from models.entities.user import User
from models.modelUser import ModelUser
from models.AlumnoModel import AlumnoModel
from models.calificacionModel import CalificacionModel
from models.maestroModel import MaestroModel
from models.ModelGrupo import ModelGrupo
from models.AdministradorModel import AdminModel

app = Flask(__name__)
app.config.from_object(config['development'])

csrf = CSRFProtect(app)
csrf.init_app(app)

# Solo para debugging, no uses en producción
app.config['WTF_CSRF_ENABLED'] = False
login_manager = LoginManager(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.INFO)

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.rol.lower() not in [role.lower() for role in allowed_roles]:
                flash('No tienes permiso para acceder a esta página')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
@role_required(['maestro'])
def maestro():
    try:
        id_maestro = MaestroModel.get_id_maestro_by_user_id(current_user.id)
        logging.info(f"ID de maestro obtenido: {id_maestro}")
        
        if id_maestro is None:
            flash('No se encontró un maestro asociado a este usuario')
            return redirect(url_for('index'))
        
        maestro_data = MaestroModel.get_maestro(id_maestro)
        materias_data = ModelGrupo.get_materias_maestro(id_maestro)
        
        return render_template('auth/maestro.html', 
                               maestro=maestro_data,
                               materias=materias_data)
    
    except Exception as e:
        logging.error(f"Error inesperado en la ruta /maestro: {str(e)}", exc_info=True)
        flash('Ocurrió un error inesperado al cargar los datos del maestro')
        return redirect(url_for('index'))

@app.route('/grupo/<int:id_grupo>', methods=['GET', 'POST'])
@login_required
@role_required(['maestro'])
def grupo_detalle(id_grupo):
    try:
        
        if request.method == 'POST':
            parcial = request.form.get('parcial')
            id_materia = request.form.get('id_materia')
            
            app.logger.info(f"Recibido POST para grupo {id_grupo}, parcial {parcial}, id_materia {id_materia}")
            
            if not id_materia:
                app.logger.error("id_materia está vacío")
                flash('Error: No se pudo obtener el ID de la materia', 'error')
                return redirect(url_for('grupo_detalle', id_grupo=id_grupo))
            
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
            return redirect(url_for('grupo_detalle', id_grupo=id_grupo))
        else:

            grupo_data = ModelGrupo.get_grupo_detalle(id_grupo)
            alumnos = ModelGrupo.get_alumnos_grupo(id_grupo)
            return render_template('auth/grupo_detalle.html', grupo=grupo_data, alumnos=alumnos)
    except Exception as e:
        app.logger.error(f"Error al procesar datos del grupo: {str(e)}", exc_info=True)
        flash('Ocurrió un error al procesar los datos del grupo', 'error')
        return redirect(url_for('maestro'))

@app.route('/control-escolar/grupos/<string:nombre_grupo>/<int:id_grupo>')
@login_required
@role_required(['administrativo'])
def grupo_detalle_admin(nombre_grupo, id_grupo):
    try:
        alumnos = ModelGrupo.get_alumnos_grupo(id_grupo)  # Asumiendo que este método existe y usa id_grupo
        return render_template('auth/grupo-detalle-admin.html', alumnos=alumnos,nombre_grupo=nombre_grupo, id_grupo=id_grupo)
    except Exception as ex:
        logging.error(f"error en grupo_detalle_admin: {str(ex)}")
        return redirect(url_for('administrativo'))
    
@app.route('/control-escolar/grupos')
@login_required
@role_required(['administrativo'])
def control_escolar_grupos():
    try:
        grupos = ModelGrupo.get_grupos()
        return render_template('auth/lista-grupos.html', grupos=grupos)
    except Exception as ex:
        logging.error(f"Error en control_escolar_grupos: {str(ex)}")
        return redirect(url_for('administrativo'))

@app.route('/estudiante')
@login_required
@role_required(['estudiante'])
def estudiante():
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

@app.route('/lista_alumno', methods=['GET', 'POST'])
@login_required
@role_required(['administrativo'])
def lista_alumno():
    search_term = request.args.get('search', '')
    
    if search_term:
        alumnos = AlumnoModel.buscar_alumnos(search_term)
    else:
        alumnos = AlumnoModel.get_alumnos()
    
    return render_template('auth/lista-alumno.html', alumnos=alumnos, search_term=search_term)

@app.route('/alumno/<string:matricula>')
@login_required
@role_required(['administrativo'])
def alumno_detalle(matricula):
    alumno = AlumnoModel.get_alumno_by_matricula(matricula)
    if alumno:
        return render_template('auth/alumno_detalle.html', alumno=alumno)
    else:
        flash('Alumno no encontrado', 'error')
        return redirect(url_for('lista_alumno'))

@app.route('/alumno/<string:matricula>/pdf')
@login_required
@role_required(['administrativo'])
def alumno_pdf(matricula):
    alumno = AlumnoModel.get_alumno_by_matricula(matricula)
    if not alumno:
        flash('No se encontró información del alumno.')
        return redirect(url_for('lista_alumno'))
    
    html = render_template('auth/alumno_pdf.html', alumno=alumno)
    pdf = pdfkit.from_string(html, False)

    return send_file(
        BytesIO(pdf),
        mimetype='application/pdf',
        download_name=f"alumno_{alumno['matricula']}.pdf",
        as_attachment=True
    )
@app.route('/administrativo')
@login_required
@role_required(['administrativo'])
def administrativo():
    try:
        id_administrativo = AdminModel.get_id_Admin_by_user_id(current_user.id)
        if id_administrativo is None:
            flash('No se encontró un adm asociado a este usuario')
            return redirect(url_for('index'))
        
        return render_template('auth/administrador-tier1.html')
    except Exception as e:
        print(id_administrativo)
        app.logger.error(f"Error al obtener datos del administrador: {str(e)}")
        flash('Ocurrió un error al cargar los datos del administrador')
        return redirect(url_for('index'))

@app.route('/control-escolar/alumno/<string:matricula>/modificar')
@login_required
@role_required(['administrativo'])
def modificar_alumno(matricula):
    try:
        if matricula:
            alumno = AlumnoModel.get_alumno_by_matricula(matricula)
            carrera = AdminModel.get_carreras()   
            return render_template('auth/alumno-modificacion.html', alumno=alumno, carreras=carrera)
    except Exception as ex:
        logging.error(f"Error en modificar_alumno: {str(ex)}")

@app.route('/control-escolar/agregar-alumno', methods=['GET', 'POST'])
@login_required
@role_required(['administrativo'])
def agregar_alumno():
    try:
        if request.method == 'POST':
            # Crear un diccionario con los datos del formulario
            nuevo_alumno = {
                'nombre': request.form['nombre'],
                'apellido': request.form['apellido'],
                'segundo_apellido': request.form['segundo_apellido'],
                'fecha_nacimiento': request.form['fecha_nacimiento'],
                'direccion': request.form['direccion'],
                'numero': request.form['numero'],
                'correo': request.form['correo'],
                'id_carrera': request.form['carrera'],
                'matricula': request.form['matricula'],
                'fecha_ingreso': request.form['fecha_ingreso'],
                'generacion': request.form['generacion'],
                'estado': request.form['estado'],
                'preparatoria_egreso': request.form['preparatoria_egreso'],
                'cuatrimestre': request.form['cuatrimestre']
            }
            
            # Agregar el nuevo alumno a la base de datos
            resultado = AlumnoModel.add_alumno(nuevo_alumno)
            
            if resultado:
                flash('Alumno agregado exitosamente', 'success')
            else:
                flash('Error al agregar alumno', 'error')
            
            return redirect(url_for('administrativo'))
        else:
            carreras = AdminModel.get_carreras()
            return render_template('auth/agregar-alumno.html', carreras=carreras)
    except Exception as ex:
        logging.error(f"Error al agregar alumno: {str(ex)}")
        flash('Ocurrió un error al agregar el alumno', 'error')
        return redirect(url_for('agregar_alumno'))
    
@app.route('/control-escolar/grupos/<string:nombre_grupo>/<int:id_grupo>/modificar')
@login_required
@role_required(['administrativo'])
def ver_detalles_grupo(nombre_grupo, id_grupo):
    try:
        alumnos = ModelGrupo.get_alumnos_grupo(id_grupo)
        return render_template('auth/modificar-grupo-admin.html', alumnos=alumnos, nombre_grupo=nombre_grupo, id_grupo=id_grupo)
    except Exception as ex:
        logging.error(f"Error en ver_detalles_grupo: {str(ex)}")
        return "Error al obtener detalles del grupo", 500
    
@app.route('/control-escolar/grupos/<string:nombre_grupo>/<int:id_grupo>/modificar/agregar-alumno', methods=['GET', 'POST'])
@login_required
@role_required(['administrativo'])
def agregar_alumno_grupo(nombre_grupo, id_grupo):
    search_term = request.args.get('search', '')
    try:
        alumnos = ModelGrupo.get_alumnos_not_in_group(id_grupo, search_term)
        
        if request.method == 'POST':
            alumno_id = request.form.get('alumno_id')
            if alumno_id:
                agregado = ModelGrupo.agregar_alumno(id_grupo, alumno_id)
                if agregado:
                    flash('Alumno agregado al grupo exitosamente', 'success')
                    return redirect(url_for('agregar_alumno_grupo', nombre_grupo=nombre_grupo, id_grupo=id_grupo))
                
        return render_template('auth/agregar-alumno-grupo.html', alumnos=alumnos, search_term=search_term, nombre_grupo=nombre_grupo, id_grupo=id_grupo)
    except Exception as ex:
        logging.error(f"Error en agregar_alumno_grupo: {str(ex)}")
        return "Error al buscar alumnos", 500
@app.route('/control-escolar/grupos/agregar-grupo', methods=['GET', 'POST'])
@login_required
@role_required(['administrativo'])
def agregar_grupo():
    try:
        if request.method == 'POST':
            # Debug logging
            logging.debug(f"Form data received: {request.form}")
            
            nuevo_grupo = {
                'nombre': request.form.get('nombre'),
                'descripcion': request.form.get('descripcion'),
                'id_carrera': request.form.get('carrera')
            }
            
            # More debug logging
            logging.debug(f"Nuevo grupo data: {nuevo_grupo}")
            
            if not all(nuevo_grupo.values()):
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('agregar_grupo'))

            resultado = ModelGrupo.agregar_grupo(nuevo_grupo)
            if resultado:
                flash('Grupo agregado exitosamente', 'success')
            else:
                flash('Error al agregar grupo', 'error')
            
            return redirect(url_for('administrativo'))
        else:
            carreras = AdminModel.get_carreras()
            return render_template('auth/agregar-grupo.html', carreras=carreras)
    except Exception as ex:
        logging.error(f"Error en agregar_grupo: {str(ex)}")
        flash('Ocurrió un error al procesar la solicitud', 'error')
        return redirect(url_for('administrativo'))
    
@app.route('/control-escolar/grupos/modificar')
@login_required
@role_required(['administrativo'])
def lista_modificar_grupos():
    try:
        grupos = ModelGrupo.get_grupos()
        
        return render_template('auth/lista-modifica-grupos.html', grupos=grupos)
    except Exception as ex:
        logging.error(f"Error en lista_modificar_grupos: {str(ex)}")
@app.route('/control-escolar/grupos/modificar/<int:id_grupo>', methods=['POST','GET'])
@login_required
@role_required(['administrativo'])
def modificar_grupo(id_grupo):
    try:
        if request.method == 'POST':
            grupo = ModelGrupo.get_grupo(id_grupo)  # Assume this method exists and retrieves the group data
            carreras = AdminModel.get_carreras()
            return render_template('auth/modificar-grupo.html', grupo=grupo, carreras=carreras)
        else:
                grupo = ModelGrupo.get_grupo(id_grupo)  # Assume this method exists and retrieves the group data
                carreras = AdminModel.get_carreras()
                return render_template('auth/modificar-grupo.html', grupo=grupo, carreras=carreras)
    except Exception as ex:
        logging.error(f"Error en modificar_grupo: {str(ex)}")
@app.route('/control-escolar/grupos/<string:nombre_grupo>/<int:id_grupo>/modificar/eliminado/<int:id_alumno>', methods=['GET', 'POST'])
@login_required
@role_required(['administrativo'])
def eliminar_alumno_grupo(nombre_grupo,id_alumno, id_grupo):
    try:


                eliminado = ModelGrupo.eliminar_alumno(id_grupo, id_alumno)
                if eliminado:
                    flash('Alumno agregado al grupo exitosamente', 'success')
                    return redirect(url_for('ver_detalles_grupo', nombre_grupo=nombre_grupo, id_grupo=id_grupo))
                else:
                    print('nigga')
                
                
    except Exception as ex:
        logging.error(f"Error en agregar_alumno_grupo: {str(ex)}")
        return "Error al buscar alumnos", 500



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