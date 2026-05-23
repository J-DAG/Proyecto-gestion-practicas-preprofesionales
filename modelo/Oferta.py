import uuid
from dataclasses import dataclass
from datetime import datetime, date
from typing import ClassVar

from modelo.BasePersistencia import BasePersistente

@dataclass
class Oferta(BasePersistente):
    id_oferta: str
    id_empresa: str
    titulo: str
    descripcion: str
    requisitos: str
    area: str
    cupos: int
    fecha_publicacion: date
    fecha_cierre: date
    estado: str = "abierta"

    archivo: ClassVar[str] = "ofertas"
    campo_id: ClassVar[str] = "id_oferta"

    def __post_init__(self) -> None:
        self.id = self.id_oferta

    def esta_disponible(self) -> bool:
        return self.estado == "abierta" and self.cupos > 0 and self.fecha_cierre >= date.today()
