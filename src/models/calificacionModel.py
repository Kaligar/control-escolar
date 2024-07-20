from database.db import get_connection
from .entities.calificacion import Calificacion 

class CalificacionModel:
    @classmethod
    def en_curso(cls, id_alumno):
        try:
            connection = get_connection()
            calificaciones = []
            
            with connection.cursor() as cursor:
                cursor.execute(
                    '''SELECT 
                    C.id_calificacion, M.nombre AS materia, C.calificacion, C.tipo, M.clave AS clave, M.modulo AS modulo
                    FROM calificacion AS C
                    INNER JOIN materia AS M ON M.id_materia = C.id_materia
                    WHERE C.id_alumno = %s AND C.fase IN ('Parcial 1', 'Parcial 2', 'Parcial 3') AND C.cursado = 0
                    ORDER BY modulo
                    ''',
                    (id_alumno,))
                resultset = cursor.fetchall()

                for row in resultset:
                    calificacion_obj = {
                        'materia': row[1],
                        'calificacion': row[2],
                        'tipo': row[3],
                        'clave': row[4],
                        'modulo': row[5]
                    }
                    
                    calificaciones.append(calificacion_obj)
                
            return calificaciones

        except Exception as ex:
            raise Exception(f"Error al obtener calificaciones en curso: {ex}")

        finally:
            if connection:
                connection.close()
    
    @classmethod
    def calificaciones_parciales(cls, id_alumno):
        try:
            connection = get_connection()
            calificaciones = {}
            
            with connection.cursor() as cursor:
                cursor.execute('''SELECT 
                    M.modulo, M.clave, M.nombre AS materia, C.calificacion, C.tipo, C.fase
                    FROM calificacion AS C
                    INNER JOIN materia AS M ON M.id_materia = C.id_materia
                    WHERE C.id_alumno = %s AND C.cursado = 0 AND C.fase IN ('Parcial 1', 'Parcial 2', 'Parcial 3')
                    ORDER BY M.modulo, M.nombre, C.fase
                ''', (id_alumno,))
                resultset = cursor.fetchall()

                for row in resultset:
                    modulo, clave, materia, calificacion, tipo, fase = row
                    
                    if materia not in calificaciones:
                        calificaciones[materia] = {
                            'modulo': modulo,
                            'clave': clave,
                            'parciales': {}
                        }
                    
                    calificaciones[materia]['parciales'][fase] = {
                        'calificacion': calificacion,
                        'tipo': tipo
                    }
            
            return calificaciones

        except Exception as ex:
            raise Exception(f"Error al obtener calificaciones parciales: {ex}")

        finally:
            if connection:
                connection.close()
    @classmethod
    def calificaciones_anteriores(cls, id_alumno):
        try:
            connection = get_connection()
            calificaciones = []
            
            with connection.cursor() as cursor:
                cursor.execute('''SELECT 
                    C.id_calificacion, M.nombre AS materia, C.calificacion, C.tipo, M.clave AS clave, M.modulo AS modulo
                    FROM calificacion AS C
                    INNER JOIN materia AS M ON M.id_materia = C.id_materia
                    WHERE C.id_alumno = %s AND C.cursado = 1
                    ORDER BY M.modulo, M.nombre
                ''', (id_alumno,))
                resultset = cursor.fetchall()

                for row in resultset:
                    calificacion_obj = {
                        'id_calificacion': row[0],
                        'materia': row[1],
                        'calificacion': row[2],
                        'tipo': row[3],
                        'clave': row[4],
                        'modulo': row[5]
                    }
                    
                    calificaciones.append(calificacion_obj)
                
            return calificaciones

        except Exception as ex:
            raise Exception(f"Error al obtener calificaciones anteriores: {ex}")

        finally:
            if connection:
                connection.close()