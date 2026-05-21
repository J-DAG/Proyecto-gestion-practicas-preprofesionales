import uuid
from datetime import datetime

class Postulacion:
    def __init__(self,
                 id_estudiante,
                 id_oferta
                 ):
        self.id_postulacion = str(uuid.uuid4())
        self.id_estudiante = id_estudiante
        self.id_oferta = id_oferta
        self.fecha_postulacion = datetime.now()
        self.estado = 'pendiente'