from database.db import get_connection
import logging
    
class AdminModel:
    @classmethod
    def get_id_Admin_by_user_id(cls, user_id):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("select id_administrativo from administrativo where id_usuario = %s", (user_id,))
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
    def agregar_alumno(cls, nombre, apellido, email, matricula, id_carrera):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO alumno (nombre, apellido, email, matricula, id_carrera)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nombre, apellido, email, matricula, id_carrera))
            connection.commit()
        except Exception as ex:
            raise Exception(ex)
        finally:
            connection.close()

    @classmethod
    def get_carreras(cls):
        try:
            connection = get_connection()
            carreras = []
            with connection.cursor() as cursor:
                cursor.execute("SELECT id_carrera, nombre FROM carrera")
                carreras = cursor.fetchall()
            return carreras
        except Exception as ex:
            raise Exception(ex)
        finally:
            connection.close()