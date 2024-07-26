from database.db import get_connection
# Asegúrate de que el nombre de la clase sea correcto
from .entities.alumno import Alumno


class AlumnoModel:
    @classmethod
    def get_alumnos(cls):
        try:
            connection = get_connection()
            alumnos = []

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_alumno, nombre, apellido, segundo_apellido,matricula FROM alumno")
                resultset = cursor.fetchall()

                for row in resultset:
                    alumno_obj =  {
                        'id_alumno': row[0],
                        'nombre': row[1],
                        'apellido': row[2],
                        'segundo_apellido': row[3],
                        'matricula': row[4]
                    }
                    
                    alumnos.append(alumno_obj)

            connection.close()
            return alumnos

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_id_alumno_by_user_id(cls, user_id):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_alumno FROM alumno WHERE id_usuario = %s", (user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as ex:
            raise Exception(f"Error al obtener id_alumno: {ex}")
        finally:
            if connection:
                connection.close()
    @classmethod
    def get_alumno(cls, id_alumno):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_alumno, nombre, apellido, segundo_apellido, fecha_nacimiento, direccion, numero, correo,id_carrera, matricula,fecha_ingreso, generacion, estado, preparatoria_egreso,id_usuario FROM alumno WHERE id_alumno = %s", (id_alumno,))
                row = cursor.fetchone()

                alumno_obj = None
                if row:
                    alumno_obj = Alumno(
                        row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]
                    )

                    alumno_json = alumno_obj.to_JSON()

            connection.close()
            return alumno_json

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def add_alumno(cls, alumno):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                query = """INSERT INTO  alumno ( id_alumno,nombre, apellido, segundo_apellido, nacimiento, direccion, telefono, matricula, generacion, estado, id_carrera, correo, genero)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (alumno.id_alumno, alumno.nombre, alumno.apellido, alumno.segundo_apellido, alumno.nacimiento, alumno.direccion,
                          alumno.telefono, alumno.matricula, alumno.generacion, alumno.estado, alumno.id_carrera, alumno.correo, alumno.genero)

                print("SQL Query:", query)
                print("Values:", values)

                cursor.execute(query, values)
                affected_rows = cursor.rowcount
                connection.commit()

            connection.close()
            return affected_rows

        except Exception as ex:
            raise Exception(ex)
    @classmethod
    def get_alumno_by_matricula(cls, matricula):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_alumno, nombre, apellido, segundo_apellido, fecha_nacimiento, direccion, numero, correo,id_carrera, matricula,fecha_ingreso, generacion, estado, preparatoria_egreso,id_usuario FROM alumno WHERE matricula = %s", (matricula,))
                resultset = cursor.fetchone()
                if resultset:
                    alumno={
                    'id_alumno': resultset[0],
                    'nombre': resultset[1],
                    'apellido': resultset[2],
                    'segundo_apellido': resultset[3],
                    'fecha_nacimiento': resultset[4],# Convert date to string
                    'direccion': resultset[5],
                    'numero': resultset[6],
                    'correo': resultset[7],
                    'id_carrera': resultset[8],
                    'matricula': resultset[9],
                    'fecha_ingreso': resultset[10],
                    'generacion': resultset[11],
                    'estado': resultset[12],
                    'preparatoria_egreso': resultset[13],
                    'id_usuario': resultset[14]
                    }
                    
                return alumno
        except Exception as ex:
            raise Exception(ex)
        finally:
            connection.close()