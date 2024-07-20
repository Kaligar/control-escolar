from database.db import get_connection
# Asegúrate de que el nombre de la clase sea correcto
from .entities.alumno import Alumno


class MaestroModel:
        @classmethod
        def get_maestro(cls, id_maestro):
            try:
                connection = get_connection()
                maestro = None  # Cambiar a None para manejar el caso de no encontrar ningún maestro

                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT id_maestro, nombre, apellido, segundo_apellido, id_carrera, id_usuario 
                        FROM maestro 
                        WHERE id_maestro = %s
                        '''
                        , (id_maestro,))
                    resultset = cursor.fetchone()

                if resultset:  # Verificar si se encontró un maestro
                    maestro = {
                        'id_maestro': resultset[0],
                        'nombre': resultset[1],
                        'apellido': resultset[2],
                        'segundo_apellido': resultset[3],
                        'id_carrera': resultset[4],
                        'id_usuario': resultset[5]
                    }

                connection.close()
                return maestro

            except Exception as ex:
                raise Exception(ex)



        @classmethod
        def get_id_maestro_by_user_id(cls, user_id):
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id_maestro FROM maestro WHERE id_usuario = %s", (user_id,))
                    result = cursor.fetchone()
                    return result[0] if result else None
            except Exception as ex:
                raise Exception(f"Error al obtener id_maestro: {ex}")
            finally:
                if connection:
                    connection.close()
