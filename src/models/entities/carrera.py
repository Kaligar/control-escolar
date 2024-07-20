class Calificacion():
    def __init__(self, id_carrera, nombre=None, tipo=None, facultad=None):
        self.id_carrera = id_carrera
        self.nombre = nombre
        self.tipo = tipo
        self.facultad = facultad        
        
    def to_JSON(self):
        return {
            'id_carrera': self.id_carrera,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'facultad': self.facultad
        }
