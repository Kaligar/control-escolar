class Calificacion():
    def __init__(self, id_contacto_emergencia, nombre=None, numero_telefono=None, id_alumno=None):
        self.id_contacto_emergencia = id_contacto_emergencia
        self.nombre = nombre
        self.numero_telefono = numero_telefono
        self.id_alumno = id_alumno
        
    def to_JSON(self):
        return {
            'id_contacto_emergencia': self.id_contacto_emergencia,
            'nombre': self.nombre,
            'numero_telefono': self.numero_telefono,
            'id_alumno': self.id_alumno
        }
