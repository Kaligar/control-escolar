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
        @classmethod
        def get_grupo_detalle(cls, nombre_grupo):
            try:
                connection = get_connection()
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT g.id_grupo, g.nombre_grupo, c.nombre as carrera
                        FROM grupos as g
                        INNER JOIN carrera AS c ON c.id_carrera = g.id_carrera
                        WHERE g.nombre_grupo = %s;
                        '''
                        , (nombre_grupo,))
                    result = cursor.fetchone()
                
                if result:
                    grupo = {
                        'id_grupo': result[0],
                        'nombre_grupo': result[1],
                        'carrera': result[2]
                    }
                else:
                    grupo = None

                connection.close()
                return grupo

            except Exception as ex:
                raise Exception(ex)

        @classmethod
        def get_alumnos_grupo(cls, nombre_grupo):
            try:
                connection = get_connection()
                alumnos = []
                with connection.cursor() as cursor:
                    cursor.execute(
                    '''
                    SELECT a.id_alumno, a.nombre, a.apellido, a.segundo_apellido, a.matricula
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
                        'matricula': row[4]
                    })

                connection.close()
                return alumnos

            except Exception as ex:
                raise Exception(ex)