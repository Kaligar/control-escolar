from database.db import get_connection
from flask import flash
from models.entities.user import User


class ModelUser:
    def login(self, user):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                query = "SELECT id_usuario, username, password, rol FROM usuario WHERE username = %s"

                cursor.execute(query, (user.username,))
                row = cursor.fetchone()
                print(query)
                if row != None:
                    print(row)
                    stored_password = row[2]

                    if user.password == stored_password:

                        # Cambiamos row[2] por True
                        return User(row[0], row[1], True, row[3])
                 
                    else:
                        print('mal contraseña')

                else:
                    flash("Usuario invalido")
                    print('f')
                    print(row)

                return None
        except Exception as ex:

            raise Exception("An error occurred during login") from ex

    @classmethod
    def get_by_id(self, id_usuario):
        try:
            connection = get_connection()

            with connection.cursor() as cursor:
                query = "SELECT id_usuario, username, rol FROM usuario WHERE id_usuario = {}".format(
                    id_usuario)

                cursor.execute(query, (id_usuario))
                row = cursor.fetchone()

                if row is not None:
                    return User(row[0], row[1], None,  row[2])

                else:
                    flash("Usuario invalido")
                    print('sa')

                return None
        except Exception as ex:

            raise Exception("An error occurred during login") from ex
