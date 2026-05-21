import uuid


class Usuario:
    def __init__(self,
                 nombre,
                 email,
                 clave,
                 tipo_usuario,
                 activo = True
                 ):

        self.id_usuario = str(uuid.uuid4())
        self.nombre = nombre
        self.email = email
        self.clave = clave
        self.tipo_usuario = tipo_usuario,
        self.activo = activo

    def autenticar(self,correo,clave):
        if correo == self.correo and clave == self.clave:
            return True
        return False

    def guardar(self):
        #procedimiento de cerrar sesion y guardado de datos
        return True

    def actualizar(self):
        #cargar datos de usuario
        return True

    def eliminar(self):
        return True