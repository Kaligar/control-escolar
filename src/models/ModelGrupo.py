from database.db import get_connection
import logging
class ModelGrupo:
    @classmethod
    def get_materias_maestro(cls, id_maestro):
        try:
            connection = get_connection()
            materias = []

            with connection.cursor() as cursor:
                cursor.execute(
                    '''
SELECT DISTINCT 
    m.id_materia, 
    m.nombre AS nombre_materia, 
    c.nombre AS nombre_carrera,
	g.nombre_grupo ,
    array_agg(DISTINCT g.id_grupo) AS id_grupo
		
FROM materia AS m
INNER JOIN cursoimpartido AS ci ON ci.id_materia = m.id_materia
INNER JOIN grupos AS g ON g.id_grupo = ci.id_grupo
INNER JOIN carrera AS c ON c.id_carrera = g.id_carrera
WHERE ci.id_maestro = 1
GROUP BY m.id_materia, m.nombre, c.nombre,g.nombre_grupo, g.id_grupo
ORDER BY m.nombre;
                    '''
                    , (id_maestro,))
                resultset = cursor.fetchall()

            for row in resultset:
                materias.append({
                    'id_materia': row[0],
                    'nombre_materia': row[1],
                    'nombre_carrera': row[2],
                    'nombre_grupo': row[3],
                    'id_grupo': row[4]
                })
            print(materias)
            connection.close()
            return materias

        except Exception as ex:
            raise Exception(ex)
    @staticmethod
    def get_grupo_detalle(grupo_id):
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT g.id_grupo,g.nombre_grupo,CA.nombre,MT.id_materia
                        FROM cursoimpartido AS C 
                        INNER JOIN grupos AS G ON C.id_grupo = G.id_grupo
                        INNER JOIN materia AS MT ON MT.id_materia = C.id_materia
                        INNER JOIN maestro AS MA ON MA.id_maestro = C.id_maestro
                        INNER JOIN carrera AS CA ON CA.id_carrera = G.id_carrera
                        WHERE g.id_grupo = %s
                    """, (grupo_id,))
                    grupo = cursor.fetchone()
                    if grupo:
                        return {
                            'id_grupo': grupo[0],
                            'nombre_grupo': grupo[1],
                            'carrera': grupo[2],
                            'id_materia': grupo[3]
                        }
                    
            except Exception as e:
                print(f"Error en get_grupo_detalle: {str(e)}")
                return None
            finally:
                if connection:
                    connection.close()
    @classmethod
    def get_alumnos_grupo(cls, nombre_grupo):
            try:
                connection = get_connection()
                alumnos = []
                with connection.cursor() as cursor:
                    cursor.execute(
                    '''
                    SELECT a.id_alumno, a.nombre, a.apellido, a.segundo_apellido, a.matricula, g.nombre_grupo
                    from grupos as g
                    inner join integrantes AS i ON i.id_grupo = g.id_grupo
                    inner join alumno AS a ON i.id_alumno = a.id_alumno
                    WHERE g.id_grupo = %s
                    '''
                    , (nombre_grupo,))
                    resultset = cursor.fetchall()
                
                for row in resultset:
                    alumnos.append({
                        'id_alumno': row[0],
                        'nombre': row[1],
                        'apellido': row[2],
                        'segundo_apellido': row[3],
                        'matricula': row[4],
                        'nombre_grupo': row[5]
                    })

                connection.close()
                return alumnos

            except Exception as ex:
                raise Exception(ex)
    @classmethod
    def get_grupos(cls):
        try:
            connection = get_connection()
            grupos = []
            with connection.cursor() as cursor:
                cursor.execute('''
                SELECT DISTINCT ON (nombre_grupo) id_grupo, nombre_grupo, descripcion, id_carrera
                FROM grupos 
                ORDER BY nombre_grupo, id_carrera;
                ''')
                
                resultset = cursor.fetchall()
                for row in resultset:
                    grupos.append({
                    'id_grupo': row[0],
                    'nombre_grupo': row[1],
                    'descripcion': row[2],
                    'id_carrera': row[3]
                    })
                
                connection.close()
                return grupos
        except Exception as ex:
            raise Exception
        
    @classmethod
    def agregar_alumno(cls,id_grupo,id_alumno):
        try:
            connection= get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               INSERT INTO integrantes (id_grupo, id_alumno)
                                VALUES (%s,%s);
                               """
                               ,(id_grupo, id_alumno))
                connection.commit()
                return True
        except Exception as ex:
            logging.error(f"Error en ModelGrupo.Agregar_alumno: {str(ex)}")
    @classmethod
    def eliminar_alumno(cls,id_grupo,id_alumno):
        try:
            connection= get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               DELETE FROM integrantes
                               WHERE id_alumno = %s AND id_grupo = %s;
                               """
                               ,(id_alumno, id_grupo))
                connection.commit()
                return True
        except Exception as ex:
            logging.error(f"Error en ModelGrupo.eliminar_alumno: {str(ex)}")

    @classmethod
    def get_alumnos_not_in_group(cls, id_grupo, search_term=''):
        try:
            connection = get_connection()
            alumnos = []
            with connection.cursor() as cursor:
                query = """
                SELECT a.id_alumno, a.nombre, a.apellido, a.segundo_apellido, a.matricula
                FROM alumno a
                LEFT JOIN integrantes ag ON a.id_alumno = ag.id_alumno AND ag.id_grupo = %s
                WHERE ag.id_alumno IS NULL
                """
                params = [id_grupo]
                
                if search_term:
                    query += " AND (a.nombre LIKE %s OR a.apellido LIKE %s OR a.matricula LIKE %s)"
                    params.extend([f"%{search_term}%"] * 3)
                
                cursor.execute(query, params)
                results = cursor.fetchall()

                for row in results:
                    alumnos.append({
                        'id_alumno': row[0],
                        'nombre': row[1],
                        'apellido': row[2],
                        'segundo_apellido': row[3],
                        'matricula': row[4]
                    })

            return alumnos
        except Exception as ex:
            logging.error(f"Error en get_alumnos_not_in_group: {str(ex)}")
            return []
        finally:
            connection.close()

    @classmethod
    def agregar_grupo(cls, grupo):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("""
                               INSERT INTO grupos (nombre_grupo, descripcion, id_carrera)
                               VALUES (%s, %s, %s);
                               """,
                               (grupo['nombre'], grupo['descripcion'], grupo['id_carrera']))
                connection.commit()
                return True
        except Exception as ex:
            logging.error(f"Error en ModelGrupo.agregar_grupo: {str(ex)}")
            return False
        finally:
            if connection:
                connection.close()
    @classmethod
    def get_grupo(cls,id_grupo):
        try:
            connection = get_connection()
            grupo = []
            with connection.cursor() as cursor:
                cursor.execute('''
                SELECT id_grupo, nombre_grupo, descripcion, id_carrera
                FROM grupos 
                WHERE id_grupo = %s
                ORDER BY nombre_grupo, id_carrera;;
                ''',(id_grupo,))
                
                resultset = cursor.fetchone()
                if resultset:
                    grupo.append({
                    'id_grupo': resultset[0],
                    'nombre_grupo': resultset[1],
                    'descripcion': resultset[2],
                    'id_carrera': resultset[3]
                    })
                
                connection.close()
                return grupo
        except Exception as ex:
            logging.error(f"Error en ModelGrupo.get_grupo: {str(ex)}")    