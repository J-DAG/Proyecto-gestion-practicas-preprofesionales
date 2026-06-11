from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import ClassVar

from modelo.BasePersistente import BasePersistente


@dataclass
class Formulario(BasePersistente):
    id_formulario: str
    id_practica: str
    tipo: str
    fecha_registro: date
    observaciones: str = ""
    contenido: str = ""
    calificacion: int | None = None

    archivo: ClassVar[str] = "formularios"
    campo_id: ClassVar[str] = "id_formulario"

    def __post_init__(self) -> None:
        self.id = self.id_formulario
        self._migrar_campos_legacy()

    def __setstate__(self, estado: dict[str, object]) -> None:
        self.__dict__.update(estado)
        self._migrar_campos_legacy()

    def _migrar_campos_legacy(self) -> None:
        if "contenido" not in self.__dict__:
            self.contenido = ""
        if "calificacion" not in self.__dict__:
            self.calificacion = None


@dataclass
class Documento(BasePersistente):
    id_documento: str
    id_practica: str
    tipo: str
    gestionado_por: str
    fecha_emision: date
    contenido: str = ""

    archivo: ClassVar[str] = "documentos"
    campo_id: ClassVar[str] = "id_documento"

    def __post_init__(self) -> None:
        self.id = self.id_documento
        self._migrar_campos_legacy()

    def __setstate__(self, estado: dict[str, object]) -> None:
        self.__dict__.update(estado)
        self._migrar_campos_legacy()

    def _migrar_campos_legacy(self) -> None:
        if "contenido" not in self.__dict__:
            self.contenido = ""


@dataclass
class SolicitudAutorizacion(BasePersistente):
    id_solicitud: str
    id_estudiante: str
    id_empresa: str
    motivo: str
    fecha_solicitud: date
    estado: str = "pendiente"

    archivo: ClassVar[str] = "solicitudes"
    campo_id: ClassVar[str] = "id_solicitud"

    def __post_init__(self) -> None:
        self.id = self.id_solicitud
