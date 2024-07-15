from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import config
from database.db import get_connection
# routes
from routes import Alumno
from models.entities.user import User
from models.modelUser import ModelUser
from models.AlumnoModel import AlumnoModel

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
    if current_user.rol != 'maestro':
        flash('No tienes permiso para acceder a esta página')
        return redirect(url_for('index'))
    return render_template('auth/maestro.html')

@app.route('/estudiante')
@login_required
def estudiante():
    if current_user.rol != 'estudiante':
        flash('No tienes permiso para acceder a esta página')
        return redirect(url_for('index'))
    
    # Obtener los datos del alumno actual
    alumno_data = AlumnoModel.get_alumno(current_user.id)
    return render_template('auth/estudiante.html', alumno=alumno_data)


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