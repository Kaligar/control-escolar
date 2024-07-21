from database.db import get_connection

class ModelGrupo:
        @classmethod
        def get_grupo_maestro(cls, id_maestro):
            try:
                connection = get_connection()
                grupos = []

                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT DISTINCT ON (g.nombre_grupo) g.nombre_grupo, g.id_grupo, c.nombre
                        FROM grupos as g
                        INNER JOIN carrera AS c ON c.id_carrera = g.id_carrera
                        WHERE g.id_maestro = %s
                        ORDER BY g.nombre_grupo, c.nombre;
                        '''
                        , (id_maestro,))
                    resultset = cursor.fetchall()

                for row in resultset:
                    grupos.append({
                        'grupo': row[0],  # nombre_grupo
                        'id_grupo': row[1],
                        'carrera': row[2],
                    })

                connection.close()
                return grupos

            except Exception as ex:
                raise Exception(ex)
        @staticmethod
        def get_grupo_detalle(grupo_id):
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT g.id_grupo, g.nombre_grupo, c.nombre as carrera, m.id_materia
                        FROM grupos g
                        JOIN carrera c ON g.id_carrera = c.id_carrera
                        JOIN materia m ON g.id_materia = m.id_materia
                        WHERE g.nombre_grupo = %s
                    """, (grupo_id,))
                    grupo = cursor.fetchone()
                    if grupo:
                        return {
                            'id_grupo': grupo[0],
                            'nombre_grupo': grupo[1],
                            'carrera': grupo[2],
                            'id_materia': grupo[3]
                        }
                    return None
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
                    SELECT a.id_alumno, a.nombre, a.apellido, a.segundo_apellido, a.matricula, g.id_materia
                    FROM alumno as a
                    INNER JOIN grupos AS g ON a.id_alumno = g.id_alumno
                    WHERE g.nombre_grupo = %s;
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
                        'id_materia': row[5]
                    })

                connection.close()
                return alumnos

            except Exception as ex:
                raise Exception(ex)