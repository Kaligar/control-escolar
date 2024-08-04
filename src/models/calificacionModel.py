from database.db import get_connection
from .entities.calificacion import Calificacion 
import logging

class CalificacionModel:
    @classmethod
    def en_curso(cls, id_alumno):
        try:
            connection = get_connection()
            calificaciones = []
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT C.id_calificacion, M.nombre AS materia, C.calificacion, C.tipo, M.clave AS clave, M.modulo AS modulo
                    FROM calificacion AS C
                    INNNER JOIN alumno AS A ON A.id_alumno = C.id_alumno
                    INNER JOIN materia AS M ON M.id_materia = C.id_materia
                    WHERE C.id_alumno = %s AND C.fase IN ('Parcial 1', 'Parcial 2', 'Parcial 3') AND modulo = A.cuatrimestre
                    ORDER BY modulo
                    """,
                    (id_alumno,))
                result = cursor.fetchall()

                for row in result:
                    calificaciones.append( {
                        'materia': row[1],
                        'calificacion': row[2],
                        'tipo': row[3],
                        'clave': row[4],
                        'modulo': row[5]
                    })

            return calificaciones
        except Exception as ex:
            logging.error(f"Error en en_curso: {str(ex)}")
        finally:
                connection.close()
    
    @classmethod
    def calificaciones_parciales(cls, id_alumno):
        try:
            connection = get_connection()
            calificaciones = {}
            
            with connection.cursor() as cursor:
                cursor.execute("""
                        SELECT M.modulo, M.clave, M.nombre AS materia, C.calificacion, C.tipo, C.fase
                        FROM calificacion AS C
                        INNER JOIN alumno AS A ON A.id_alumno = C.id_alumno
                        INNER JOIN materia AS M ON M.id_materia = C.id_materia
                        WHERE C.id_alumno = %s AND C.fase IN ('Parcial 1', 'Parcial 2', 'Parcial 3') AND M.modulo = A.cuatrimestre
                        ORDER BY M.modulo, M.nombre, C.fase
                        """, (id_alumno,))
                result = cursor.fetchall()

                for row in result:
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
            logging.error(f"Error en calificaciones_parciales: {str(ex)}")

        finally:
            if connection:
                connection.close()
                
    @classmethod
    def calificaciones_anteriores(cls, id_alumno):
        try:
            connection = get_connection()
            calificaciones = []
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT C.id_calificacion, M.nombre AS materia, C.calificacion, C.tipo, M.clave AS clave, M.modulo AS modulo
                    FROM calificacion AS C
                    INNER JOIN alumno AS A ON A.id_alumno = C.id_alumno
                    INNER JOIN materia AS M ON M.id_materia = C.id_materia
                    WHERE C.id_alumno = %s AND C.fase = 'Final' AND A.cuatrimestre > M.modulo
                    ORDER BY M.modulo, M.nombre 
                    """, (id_alumno,))
                result = cursor.fetchall()
                

                for row in result:
                    calificaciones.append({
                        'id_calificacion': row[0],
                        'materia': row[1],
                        'calificacion': row[2],
                        'tipo': row[3],
                        'clave': row[4],
                        'modulo': row[5]
                    })
            return calificaciones
        except Exception as ex:
            logging.error(f"Error en calificaciones_anteriores: {str(ex)}")
        finally:
                connection.close()
                
    @classmethod
    def insertar_o_actualizar_calificacion_final(cls, id_alumno, id_materia):
        try:
            connection = get_connection()
            
            with connection.cursor() as cursor:
                # Primero, obtenemos las calificaciones de los parciales
                cursor.execute("""
                    SELECT fase, calificacion
                    FROM calificacion
                    WHERE id_alumno = %s AND id_materia = %s AND fase IN ('Parcial 1', 'Parcial 2', 'Parcial 3')
                    """, (id_alumno, id_materia))
                parciales = cursor.fetchall()
                
                # Verificamos si tenemos los 3 parciales
                if len(parciales) != 3:
                    logging.warning(f"No hay suficientes parciales para calificar el final")
                
                # Calculamos el promedio
                promedio = sum(float(parcial[1]) for parcial in parciales) / 3
                
                # Si el promedio es mayor a 75, insertamos o actualizamos la calificación final
                if promedio > 75:
                    # Verificamos si ya existe una calificación final
                    cursor.execute("""
                        SELECT m.modulo
                        FROM materia m
                        WHERE m.id_materia = %s
                        """, (id_materia,))
                    modulo = cursor.fetchone()[0]

                    cursor.execute("""
                        SELECT COUNT(*) as total_materias, 
                        SUM(CASE WHEN c.calificacion >= 75 THEN 1 ELSE 0 END) as materias_aprobadas
                        FROM materia m
                        JOIN calificacion c ON m.id_materia = c.id_materia
                        WHERE m.modulo = %s AND c.id_alumno = %s AND c.fase = 'Final' AND c.tipo = 'ordinario'
                    """, (modulo, id_alumno))
                    result = cursor.fetchone()
                    total_materias, materias_aprobadas = result

                    if total_materias == materias_aprobadas:
                        # El alumno ha aprobado todas las materias del módulo
                        cursor.execute("""
                            UPDATE alumno
                            SET modulo_completado = %s
                            WHERE id_alumno = %s
                        """, (modulo, id_alumno))
                        connection.commit()

                connection.commit()
                return True if promedio > 75 else False
        except Exception as ex:
            connection.rollback()
            raise Exception(f"Error en insertar_o_actualizar_calificacion_final: {ex}")
        finally:
                connection.close()