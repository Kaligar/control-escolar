from flask import Blueprint, jsonify, request
import uuid
import datetime

# entities
from models.entities.alumno import Alumno
# Models
from models.AlumnoModel import AlumnoModel

main = Blueprint('movie_blueprint', __name__)


@main.route('/')
def get_alumos():
    try:
        alumnos = AlumnoModel.get_alumnos()
        print("Alumnos:", alumnos)  # Add this line
        return jsonify(alumnos)
    except Exception as ex:
        print("Exception:", ex)  # Add this line
        return jsonify({'message': str(ex)}), 500


@main.route('/ver/<id>')
def get_alumo(id):
    try:
        alumno = AlumnoModel.get_alumno(id)
        if alumno is not None:
            return jsonify(alumno)
        else:
            return jsonify({}), 404

    except Exception as ex:
        return jsonify({'message': str(ex)}), 500


@main.route('/add', methods=['POST'])
def add_alumno():
    try:
        id_alumno = request.json['id_alumno']
        nombre = request.json['nombre']
        apellido = request.json['apellido']
        segundo_apellido = request.json['segundo_apellido']
        nacimiento = request.json['nacimiento']
        direccion = request.json['direccion']
        telefono = request.json['telefono']
        matricula = request.json['matricula']
        generacion = request.json['generacion']
        estado = request.json['estado']
        id_carrera = request.json['id_carrera']
        correo = request.json['correo']
        genero = request.json['genero']

        # Convertir la cadena de fecha a un objeto datetime.date

        alumno = Alumno(id_alumno, nombre, apellido, segundo_apellido, nacimiento, direccion,
                        telefono, matricula, generacion, estado, id_carrera, correo, genero)

        affected_rows = AlumnoModel.add_alumno(alumno)
        if affected_rows == 1:
            return jsonify({'id_alumno': id})
        else:
            return jsonify({'message': "error on insert"}), 500
    except Exception as ex:
        return jsonify({'message': str(ex)}), 500
