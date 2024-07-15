from utils.DateFormat import DateFormat


class Alumno():
    def __init__(self, id_alumno, nombre=None, apellido=None, segundo_apellido=None, fecha_nacimiento=None, direccion=None, numero=None,
                 correo=None, id_carrera=None, matricula=None, fecha_ingreso=None, generacion=None, estado=None, preparatoria_egreso=None, id_usuario=None):
        self.id_alumno = id_alumno
        self.nombre = nombre
        self.apellido = apellido
        self.segundo_apellido = segundo_apellido
        self.fecha_nacimineto = fecha_nacimiento
        self.direccion = direccion
        self.numero = numero
        self.correo = correo
        self.id_carrera = id_carrera
        self.matricula = matricula
        self.fecha_ingreso = fecha_ingreso
        self.generacion = generacion
        self.estado = estado
        self.preparatoria_egreso = preparatoria_egreso
        self.id_usuario = id_usuario

    def to_JSON(self):
        return {
            'id_alumno': self.id_alumno,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'segundo_apellido': self.segundo_apellido,
            'fecha_nacimiento': str(self.fecha_nacimineto),# Convert date to string
            'direccion': self.direccion,
            'numero': self.numero,
            'correo': self.correo,
            'id_carrera': self.id_carrera,
            'matricula': self.matricula,
            'fecha_ingreso': self.fecha_ingreso,
            'generacion': self.generacion,
            'estado': self.estado,
            'preparatoria_egreso': self.preparatoria_egreso,
            'id_usuario': self.id_usuario
        }
