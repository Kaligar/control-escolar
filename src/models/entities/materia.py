class Calificacion():
    def __init__(self, id_materia, clave=None, nombre=None, id_carrera=None):
        self.id_materia = id_materia
        self.clave = clave
        self.nombre = nombre
        self.id_carrera = id_carrera
        
    def to_JSON(self):
        return {
            'id_materia': self.id_materia,
            'clave': self.clave,
            'nombre': self.nombre,
            'id_carrera': self.id_carrera
        }
