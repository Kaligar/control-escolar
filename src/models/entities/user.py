from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id_usuario, username, password, rol, fullname="") -> None:
        self.id = id_usuario  # Cambia id_login a id
        self.username = username
        self.password = password
        self.fullname = fullname
        self.rol = rol

    def get_id(self):
        return str(self.id)  # Asegúrate de que sea una cadena

    @staticmethod
    def check_password(provided_password, stored_password_hash):
        return check_password_hash(stored_password_hash, provided_password)
