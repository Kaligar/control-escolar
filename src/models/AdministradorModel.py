from database.db import get_connection
import logging
    
class AdminModel:
    @classmethod
    def get_id_Admin_by_user_id(cls, user_id):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT id_administrativo 
                               FROM administrativo 
                               WHERE id_usuario = %s
                               """,
                               (user_id,))
                result = cursor.fetchone()
                connection.close()
                if result:
                    return result[0]
                else:
                    logging.warning(f"No se encontró maestro con id_usuario: {user_id}")
                    return None
        except Exception as ex:
            logging.error(f"Error en get_id_Admin_by_user_id: {str(ex)}")
        finally:
            connection.close()
            
    @classmethod
    def agregar_alumno(cls, nombre, apellido, email, matricula, id_carrera):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                            INSERT INTO alumno 
                            (nombre, apellido, email, matricula, id_carrera)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (nombre, apellido, email, matricula, id_carrera))
            connection.commit()
        except Exception as ex:
            logging.error(f"Error en agregar_alumno: {str(ex)}")
        finally:
            connection.close()

    @classmethod
    def get_carreras(cls):
        try:
            connection = get_connection()
            carrera = []
            with connection.cursor() as cursor:
                cursor.execute("""SELECT 
                               id_carrera, nombre 
                               FROM carrera
                               ORDER BY tipo desc   
                               """)
                carreras = cursor.fetchall()
                for row in carreras:
                    carrera.append({
                        'id_carrera': row[0],
                        'nombre': row[1]
                    })
                    
            return carrera
        except Exception as ex:
            logging.error(f"Error en get_carreras: {str(ex)}")
        finally:
            connection.close()