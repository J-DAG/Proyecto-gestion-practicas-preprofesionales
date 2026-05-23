from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from modelo.BasePersistente import BasePersistente


@dataclass
class Notificacion(BasePersistente):
    id_notificacion: str
    id_usuario: str
    titulo: str
    mensaje: str
    fecha_creacion: datetime
    tipo: str = "informativa"
    leida: bool = False

    archivo: ClassVar[str] = "notificaciones"
    campo_id: ClassVar[str] = "id_notificacion"

    def __post_init__(self) -> None:
        self.id = self.id_notificacion

    def marcar_como_leida(self) -> None:
        self.leida = True
