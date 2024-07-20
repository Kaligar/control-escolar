class Calificacion():
    def __init__(self, id_calificacion, id_alumno=None, id_materia=None, calificacion=None, tipo=None):
        self.id_calificacion = id_calificacion
        self.id_alumno = id_alumno
        self.id_materia = id_materia
        self.calificacion = calificacion
        self.tipo = tipo
        
    def to_JSON(self):
        return {
            'id_calificacion': self.id_alumno,
            'id_alumno': self.id_alumno,
            'id_materia': self.id_materia,
            'calificacion': self.calificacion,
            'tipo': self.tipo
        }
