from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import ClassVar

from modelo.BasePersistente import BasePersistente


@dataclass
class Postulacion(BasePersistente):
    id_postulacion: str
    id_estudiante: str
    id_oferta: str
    fecha_postulacion: date
    estado: str = "pendiente"
    ruta_documento_malla: str = ""

    archivo: ClassVar[str] = "postulaciones"
    campo_id: ClassVar[str] = "id_postulacion"

    def __post_init__(self) -> None:
        self.id = self.id_postulacion
        self._migrar_campos_legacy()

    def __setstate__(self, estado: dict[str, object]) -> None:
        self.__dict__.update(estado)
        self._migrar_campos_legacy()

    def validar(self) -> None:
        self.estado = "validada"

    def aceptar(self) -> None:
        self.estado = "aceptada"

    def rechazar(self) -> None:
        self.estado = "rechazada"

    def marcar_en_terna(self) -> None:
        self.estado = "en_terna"

    def adjuntar_documento_malla(self, ruta_documento: str) -> None:
        self.ruta_documento_malla = ruta_documento

    def tiene_documento_malla(self) -> bool:
        return bool(self.ruta_documento_malla)

    def _migrar_campos_legacy(self) -> None:
        if "ruta_documento_malla" not in self.__dict__:
            self.ruta_documento_malla = ""
