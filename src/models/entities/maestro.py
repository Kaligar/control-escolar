class Calificacion():
    def __init__(self, id_maestro, nombre=None, apellido=None, segundo_apellido=None, id_carrera=None, id_usuario=None):
        self.id_maestro = id_maestro
        self.nombre = nombre
        self.apellido = apellido
        self.segundo_apellido = segundo_apellido
        self.id_carrera = id_carrera
        self.id_usuario = id_usuario
    def to_JSON(self):
        return {
            'id_maestro': self.id_maestro,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'segundo_apellido': self.segundo_apellido,
            'id_carrera': self.id_carrera,
            'id_usuario': self.id_usuario
        }
