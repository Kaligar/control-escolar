class Calificacion():
    def __init__(self, id_administrativo, nombre=None, id_alumno=None):
        self.id_administrativo = id_administrativo
        self.nombre = nombre
        self.id_alumno = id_alumno
        
    def to_JSON(self):
        return {
            'id_administrativo': self.id_administrativo,
            'nombre': self.nombre,
            'id_alumno': self.id_alumno
        }
