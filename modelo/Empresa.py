import Usuario
class Empresa:
    def __init__(self,
                 id_empresa: str,
                 nombre_empresa: str,
                 email: str,
                 ruc: str,
                 razon_social: str,
                 ubicacion: str,
                 mision: str,
                 vision: str,
                 sector: str,
                 ):
        self.id_empresa = id_empresa
        self.nombre_empresa = nombre_empresa
        self.email = email
        self.ruc = ruc
        self.razon_social = razon_social
        self.ubicacion = ubicacion
        self.mision = mision
        self.vision = vision
        self.sector = sector
        self.convenio_vigente = True

    def editar_estado_convenio(self,estado: bool):
        self.convenio_vigente = estado

