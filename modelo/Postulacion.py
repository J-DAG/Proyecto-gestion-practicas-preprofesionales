import uuid
from dataclasses import dataclass
from datetime import datetime, date
from typing import ClassVar

from modelo.BasePersistencia import BasePersistente

@dataclass
@dataclass
class Postulacion(BasePersistente):
    id_postulacion: str
    id_estudiante: str
    id_oferta: str
    fecha_postulacion: date
    estado: str = "pendiente"

    archivo: ClassVar[str] = "postulaciones"
    campo_id: ClassVar[str] = "id_postulacion"

    def __post_init__(self) -> None:
        self.id = self.id_postulacion

    def validar(self) -> None:
        self.estado = "validada"

    def aceptar(self) -> None:
        self.estado = "aceptada"

    def rechazar(self) -> None:
        self.estado = "rechazada"

    def marcar_en_terna(self) -> None:
        self.estado = "en_terna"