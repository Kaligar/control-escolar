from database.db import get_connection
# Asegúrate de que el nombre de la clase sea correcto
from .entities.alumno import Alumno
import logging


class AlumnoModel:
    @classmethod
    def get_id_alumno_by_user_id(cls, user_id):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT id_alumno 
                               FROM alumno 
                               WHERE id_usuario = %s
                               """,(user_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as ex:
            logging.error(f"Error en get_id_alumno_by_user: {str(ex)}")
        finally:
                connection.close()
                
    @classmethod
    def get_alumnos(cls):
        try:
            connection = get_connection()
            alumnos = []

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id_alumno, nombre, apellido, segundo_apellido, matricula 
                    FROM alumno
                    """)
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
                    
            return alumnos
        except Exception as ex:
            logging.error(f"Error en get_alumnos: {str(ex)}")
        finally:
            connection.close()


    @classmethod
    def get_alumno(cls, id_alumno):
        try:
            connection = get_connection()
            alumno=[]
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT id_alumno, nombre, apellido, segundo_apellido, fecha_nacimiento, direccion, numero, correo,id_carrera, matricula,fecha_ingreso, generacion, estado, preparatoria_egreso,id_usuario 
                               FROM alumno
                               WHERE id_alumno = %s
                               """, (id_alumno,))
                result = cursor.fetchone()

                if result:
                    alumno={
                    'id_alumno': result[0],
                    'nombre': result[1],
                    'apellido': result[2],
                    'segundo_apellido': result[3],
                    'fecha_nacimiento': result[4],
                    'direccion': result[5],
                    'numero': result[6],
                    'correo': result[7],
                    'id_carrera': result[8],
                    'matricula': result[9],
                    'fecha_ingreso': result[10],
                    'generacion': result[11],
                    'estado': result[12],
                    'preparatoria_egreso': result[13],
                    'id_usuario': result[14]
                    }

            return alumno

        except Exception as ex:
            logging.error(f"Error en get_alumno: {str(ex)}")
        finally:
            connection.close()


    @classmethod
    def add_alumno(cls, alumno):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO alumno 
                    (nombre, apellido, segundo_apellido, fecha_nacimiento, direccion, numero, 
                    correo, id_carrera, matricula, fecha_ingreso, generacion, estado, 
                    preparatoria_egreso, cuatrimestre)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                    alumno['nombre'], alumno['apellido'], alumno['segundo_apellido'],
                    alumno['fecha_nacimiento'], alumno['direccion'], alumno['numero'],
                    alumno['correo'], alumno['id_carrera'], alumno['matricula'],
                    alumno['fecha_ingreso'], alumno['generacion'], alumno['estado'],
                    alumno['preparatoria_egreso'], alumno['cuatrimestre']
                ))
                connection.commit()
            return True
        except Exception as ex:
            logging.error(f"Error en add_alumno: {str(ex)}")
            return False
        finally:
            connection.close()
    @classmethod
    def get_alumno_by_matricula(cls, matricula):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT id_alumno, nombre, apellido, segundo_apellido, fecha_nacimiento, direccion, numero, correo,id_carrera, matricula,fecha_ingreso, generacion, estado, preparatoria_egreso,id_usuario 
                               FROM alumno 
                               WHERE matricula = %s
                               """, (matricula,))
                result = cursor.fetchone()
                if result:
                    alumno={
                    'id_alumno': result[0],
                    'nombre': result[1],
                    'apellido': result[2],
                    'segundo_apellido': result[3],
                    'fecha_nacimiento': result[4],# Convert date to string
                    'direccion': result[5],
                    'numero': result[6],
                    'correo': result[7],
                    'id_carrera': result[8],
                    'matricula': result[9],
                    'fecha_ingreso': result[10],
                    'generacion': result[11],
                    'estado': result[12],
                    'preparatoria_egreso': result[13],
                    'id_usuario': result[14]
                    }
                    
                return alumno
        except Exception as ex:
            logging.error(f"Error en get_alumno_by_matricula: {str(ex)}")
        finally:
            connection.close()
            
    @classmethod
    def buscar_alumnos(cls, search_term):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                alumnos=[]
                cursor.execute("""
                SELECT id_alumno, nombre, apellido, segundo_apellido, fecha_nacimiento, direccion, numero, correo,id_carrera, matricula,fecha_ingreso, generacion, estado, preparatoria_egreso,id_usuario FROM alumno
                WHERE LOWER(nombre) LIKE LOWER(%s) 
                OR LOWER(apellido) LIKE LOWER(%s) 
                OR LOWER(segundo_apellido) LIKE LOWER(%s)
                OR LOWER(matricula) LIKE LOWER(%s)
                """
                , ('%' + search_term + '%',) * 4)
                result = cursor.fetchall()
                
                for resultset in result:
                    alumnos.append({
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
                    })
                    
                return alumnos
        except Exception as ex:
            logging.error(f"Error en buscar_alumnos: {str(ex)}")
        finally:
            connection.close()