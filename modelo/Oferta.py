import uuid
from datetime import datetime

class Oferta:
    def __init__(self,
                 id_empresa,
                 titulo,
                 descripcion,
                 requisitos,
                 carreras_objetivo,
                 cupos
                 ):
        self.id_oferfa = str(uuid.uuid4())
        self.id_empresa = id_empresa
        self.titulo = titulo
        self.descripcion = descripcion
        self.requisitos = requisitos
        self.cupos = cupos
        self.fecha_publicacion = datetime.now()
        self.fecha_cierre = None
        self.estado = 'activa'

