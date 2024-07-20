class Calificacion():
    def __init__(self, id_comprobante, id_alumno=None, tipo=None, archivo=None):
        self.id_comprobante = id_comprobante
        self.id_alumno = id_alumno
        self.tipo = tipo
        self.archivo = archivo
        
    def to_JSON(self):
        return {
            'id_comprobante': self.id_comprobante,
            'id_alumno': self.id_alumno,
            'tipo': self.tipo,
            'archivo': self.archivo
        }
