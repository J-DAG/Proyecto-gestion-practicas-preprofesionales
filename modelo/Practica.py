from dataclasses import dataclass
from datetime import date
from typing import ClassVar

from modelo.BasePersistencia import BasePersistente


@dataclass
class Practica(BasePersistente):
    id_practica: str
    id_postulacion: str
    id_estudiante: str
    id_empresa: str
    fecha_inicio: date
    fecha_fin: date
    id_tutor_academico: str
    tutor_empresarial: str
    estado: str = "activa"
    horas_cumplidas: int = 0
    calificacion: int | None = None
    id_tutor_academico_calificador: str | None = None
    fecha_calificacion: date | None = None
    formularios_finales_enviados: bool = False

    archivo: ClassVar[str] = "practicas"
    campo_id: ClassVar[str] = "id_practica"

    def __post_init__(self) -> None:
        self.id = self.id_practica
        self.migrar_campos_legacy()

    def __setstate__(self, estado: dict[str, object]) -> None:
        self.__dict__.update(estado)
        self.migrar_campos_legacy()

    def completar(self) -> None:
        self.estado = "finalizada"

    def calificar(self, calificacion: int, id_tutor_academico: str) -> None:
        self.calificacion = calificacion
        self.id_tutor_academico_calificador = id_tutor_academico
        self.fecha_calificacion = date.today()

    def migrar_campos_legacy(self) -> None:
        if "calificacion" not in self.__dict__:
            self.calificacion = None
        if "id_tutor_academico_calificador" not in self.__dict__:
            self.id_tutor_academico_calificador = None
        if "fecha_calificacion" not in self.__dict__:
            self.fecha_calificacion = None
        if "formularios_finales_enviados" not in self.__dict__:
            self.formularios_finales_enviados = False
