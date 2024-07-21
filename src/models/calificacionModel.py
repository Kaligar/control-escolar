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
                    INNNER JOIN alumno AS A ON A.id_alumno = C.id_alumno
                    INNER JOIN materia AS M ON M.id_materia = C.id_materia
                    WHERE C.id_alumno = %s AND C.fase IN ('Parcial 1', 'Parcial 2', 'Parcial 3') AND modulo = A.cuatrimestre
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
                        INNER JOIN alumno AS A ON A.id_alumno = C.id_alumno
                        INNER JOIN materia AS M ON M.id_materia = C.id_materia
                        WHERE C.id_alumno = %s AND C.fase IN ('Parcial 1', 'Parcial 2', 'Parcial 3') AND M.modulo = A.cuatrimestre
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
                    INNER JOIN alumno AS A ON A.id_alumno = C.id_alumno
                    INNER JOIN materia AS M ON M.id_materia = C.id_materia
                    WHERE C.id_alumno = %s AND C.fase = 'Final' AND A.cuatrimestre > M.modulo
                    ORDER BY M.modulo, M.nombre 
                ''', (id_alumno,))
                resultset = cursor.fetchall()
                print(resultset)

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
    @classmethod
    def insertar_o_actualizar_calificacion_final(cls, id_alumno, id_materia):
        try:
            connection = get_connection()
            
            with connection.cursor() as cursor:
                # Primero, obtenemos las calificaciones de los parciales
                cursor.execute('''
                    SELECT fase, calificacion
                    FROM calificacion
                    WHERE id_alumno = %s AND id_materia = %s AND fase IN ('Parcial 1', 'Parcial 2', 'Parcial 3')
                ''', (id_alumno, id_materia))
                parciales = cursor.fetchall()
                
                # Verificamos si tenemos los 3 parciales
                if len(parciales) != 3:
                    raise Exception("No se encontraron los 3 parciales para calcular la calificación final")
                
                # Calculamos el promedio
                promedio = sum(float(parcial[1]) for parcial in parciales) / 3
                
                # Si el promedio es mayor a 75, insertamos o actualizamos la calificación final
                if promedio > 75:
                    # Verificamos si ya existe una calificación final
                    cursor.execute('''
                        SELECT id_calificacion
                        FROM calificacion
                        WHERE id_alumno = %s AND id_materia = %s AND fase = 'Final' AND tipo = 'ordinario'
                    ''', (id_alumno, id_materia))
                    existing_final = cursor.fetchone()
                    
                    if existing_final:
                        # Si ya existe, actualizamos
                        cursor.execute('''
                            UPDATE calificacion
                            SET calificacion = %s
                            WHERE id_calificacion = %s
                        ''', (promedio, existing_final[0]))
                    else:
                        # Si no existe, insertamos
                        cursor.execute('''
                            INSERT INTO calificacion (id_alumno, id_materia, calificacion, tipo, fase)
                            VALUES (%s, %s, %s, 'ordinario', 'Final')
                        ''', (id_alumno, id_materia, promedio))
                    
                    connection.commit()
                    return True
                else:
                    return False

        except Exception as ex:
            connection.rollback()
            raise Exception(f"Error al insertar o actualizar calificación final: {ex}")

        finally:
            if connection:
                connection.close()