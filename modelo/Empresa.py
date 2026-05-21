import Usuario
class Empresa(Usuario):
    def __init__(self,
                 id_usuario,
                 nombre,
                 email,
                 clave,
                 ruc,
                 razon_social,
                 ubicacion,
                 mision,
                 vision,
                 sector
                 ):
        super().__init__(id_usuario,nombre,email,clave,tipo_usuario ="Empresa")
        self.ruc = ruc
        self.razon_social = razon_social
        self.ubicacion = ubicacion
        self.mision = mision
        self.vision = vision
        self.sector = sector
        self.convenio_vigente = True

