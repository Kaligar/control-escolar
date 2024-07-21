from database.db import get_connection
# Asegúrate de que el nombre de la clase sea correcto
from .entities.alumno import Alumno


import logging

class MaestroModel:
    @classmethod
    def get_maestro(cls, id_maestro):
        try:
            connection = get_connection()
            maestro = None

            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT id_maestro, nombre, apellido, segundo_apellido, id_carrera, id_usuario 
                    FROM maestro 
                    WHERE id_maestro = %s
                    ''', (id_maestro,))
                resultset = cursor.fetchone()

            if resultset:
                maestro = {
                    'id_maestro': resultset[0],
                    'nombre': resultset[1],
                    'apellido': resultset[2],
                    'segundo_apellido': resultset[3],
                    'id_carrera': resultset[4],
                    'id_usuario': resultset[5]
                }
            else:
                logging.warning(f"No se encontró maestro con id_maestro: {id_maestro}")

            return maestro

        except Exception as ex:
            logging.error(f"Error en get_maestro: {str(ex)}")
            raise

        finally:
            if connection:
                connection.close()

    @classmethod
    def get_id_maestro_by_user_id(cls, user_id):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_maestro FROM maestro WHERE id_usuario = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    logging.warning(f"No se encontró maestro con id_usuario: {user_id}")
                    return None
        except Exception as ex:
            logging.error(f"Error al obtener id_maestro: {str(ex)}")
            raise
        finally:
            if connection:
                connection.close()
    @classmethod
    def guardar_calificacion(cls, id_alumno, calificacion, tipo, id_materia, fase):
        try:
            connection = get_connection()
            calificacion = round(calificacion, 2) 
            with connection.cursor() as cursor:
                cursor.execute("""
INSERT INTO calificacion (id_alumno, calificacion, tipo, id_materia, fase)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (id_alumno, id_materia, fase)
DO UPDATE SET calificacion = EXCLUDED.calificacion, tipo = EXCLUDED.tipo;

                """, (id_alumno, calificacion, tipo, id_materia, fase))
            connection.commit()
            print("Calificación guardada exitosamente")
        except Exception as ex:
            print(f"Error al guardar la calificación: {str(ex)}")
            connection.rollback()
            raise
        finally:
            connection.close()