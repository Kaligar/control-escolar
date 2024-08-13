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
            return None  # Add this line to return None in case of an error

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
            return None  # Add this line to return None in case of an error
        finally:
            if connection:
                connection.close()
                
    @classmethod
    def insertar_o_actualizar_calificacion_final(cls, id_alumno, id_materia):
        connection = None
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                # Obtener las calificaciones de los parciales
                cursor.execute("""
                    SELECT fase, calificacion
                    FROM calificacion
                    WHERE id_alumno = %(id_alumno)s AND id_materia = %(id_materia)s AND fase IN ('Parcial 1', 'Parcial 2', 'Parcial 3')
                """, {'id_alumno': id_alumno, 'id_materia': id_materia})
                parciales = cursor.fetchall()

                # Verificar si tenemos los 3 parciales
                if len(parciales) != 3:
                    logging.warning(f"No hay suficientes parciales para calificar el final")
                    return False

                # Calcular el promedio
                promedio = sum(float(parcial[1]) for parcial in parciales) / 3

                # Insertar o actualizar la calificación final
                cursor.execute("""
                    INSERT INTO calificacion (id_alumno, id_materia, calificacion, fase, tipo)
                    VALUES (%(id_alumno)s, %(id_materia)s, %(promedio)s, 'Final', 'ordinario')
                    ON CONFLICT (id_alumno, id_materia, fase, tipo) DO UPDATE SET calificacion = %(promedio)s
                """, {'id_alumno': id_alumno, 'id_materia': id_materia, 'promedio': promedio})

                if promedio >= 70:  # Changed from 75 to 70
                    cursor.execute("""
                        SELECT modulo
                        FROM materia
                        WHERE id_materia = %(id_materia)s
                    """, {'id_materia': id_materia})
                    modulo = cursor.fetchone()[0]

                    cursor.execute("""
                        SELECT ROUND(100.0 * SUM(CASE WHEN c.calificacion >= 70 THEN 1 ELSE 0 END) / COUNT(*), 2) AS porcentaje_materias_aprobadas
                        FROM materia m
                        JOIN calificacion c ON m.id_materia = c.id_materia
                        WHERE m.modulo = %(modulo)s AND c.id_alumno = %(id_alumno)s AND c.fase = 'Final' AND c.tipo = 'ordinario'
                    """, {'modulo': modulo, 'id_alumno': id_alumno})
                    porcentaje_materias_aprobadas = cursor.fetchone()[0]

                    if porcentaje_materias_aprobadas == 100.0:
                        cursor.execute("""
                            UPDATE alumno
                            SET cuatrimestre = cuatrimestre + 1
                            WHERE id_alumno = %(id_alumno)s
                        """, {'id_alumno': id_alumno})

            connection.commit()
            return True
        except Exception as ex:
            if connection:
                connection.rollback()
            logging.error(f"Error al insertar o actualizar la calificación final: {ex}")
            return False
        finally:
            if connection:
                connection.close()