import Usuario

class Administrador(Usuario):
    def __init__(self,
                 nombre,
                 email,
                 clave):
        super().__init__(nombre,email,clave,tipo_usuario = "administrador")
        self.permisos_globales = True