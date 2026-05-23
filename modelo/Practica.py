
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import ClassVar

from modelo.BasePersistente import BasePersistente


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
        self._migrar_campos_legacy()

    def __setstate__(self, estado: dict[str, object]) -> None:
        self.__dict__.update(estado)
        self._migrar_campos_legacy()

    def completar(self) -> None:
        self.estado = "finalizada"

    def calificar(self, calificacion: int, id_tutor_academico: str) -> None:
        self.calificacion = calificacion
        self.id_tutor_academico_calificador = id_tutor_academico
        self.fecha_calificacion = date.today()

    def _migrar_campos_legacy(self) -> None:
        if "calificacion" not in self.__dict__:
            self.calificacion = None
        if "id_tutor_academico_calificador" not in self.__dict__:
            self.id_tutor_academico_calificador = None
        if "fecha_calificacion" not in self.__dict__:
            self.fecha_calificacion = None
        if "formularios_finales_enviados" not in self.__dict__:
            self.formularios_finales_enviados = False


@dataclass
class Actividad(BasePersistente):
    id_actividad: str
    id_practica: str
    descripcion: str
    horas: int
    fecha: date
    aprobada_por_tutor_academico: bool = False
    completada_por_tutor_empresarial: bool = False
    id_tutor_academico_aprobador: str | None = None
    tutor_empresarial_completador: str | None = None
    fecha_aprobacion: date | None = None
    fecha_completado: date | None = None

    archivo: ClassVar[str] = "actividades"
    campo_id: ClassVar[str] = "id_actividad"

    def __post_init__(self) -> None:
        self.id = self.id_actividad
        self._migrar_campos_legacy()

    def __setstate__(self, estado: dict[str, object]) -> None:
        self.__dict__.update(estado)
        self._migrar_campos_legacy()

    @property
    def validada(self) -> bool:
        return self.completada_por_tutor_empresarial

    def aprobar(self, id_tutor_academico: str) -> None:
        self.aprobada_por_tutor_academico = True
        self.id_tutor_academico_aprobador = id_tutor_academico
        self.fecha_aprobacion = date.today()

    def completar(self, tutor_empresarial: str) -> None:
        self.completada_por_tutor_empresarial = True
        self.tutor_empresarial_completador = tutor_empresarial
        self.fecha_completado = date.today()

    def validar(self, id_tutor_academico: str) -> None:
        self.aprobar(id_tutor_academico)

    def obtener_estado(self) -> str:
        if self.completada_por_tutor_empresarial:
            return "Completado"
        if self.aprobada_por_tutor_academico:
            return "Aprobado por tutor academico"
        return "Pendiente de aprobacion academica"

    def _migrar_campos_legacy(self) -> None:
        if "aprobada_por_tutor_academico" not in self.__dict__:
            self.aprobada_por_tutor_academico = False
        if "completada_por_tutor_empresarial" not in self.__dict__:
            self.completada_por_tutor_empresarial = False
        if "id_tutor_academico_aprobador" not in self.__dict__:
            self.id_tutor_academico_aprobador = None
        if "tutor_empresarial_completador" not in self.__dict__:
            self.tutor_empresarial_completador = None
        if "fecha_aprobacion" not in self.__dict__:
            self.fecha_aprobacion = None
        if "fecha_completado" not in self.__dict__:
            self.fecha_completado = None

        if "validada" in self.__dict__:
            validada_legacy = bool(self.__dict__["validada"])
            self.aprobada_por_tutor_academico = validada_legacy
            self.completada_por_tutor_empresarial = validada_legacy
            del self.__dict__["validada"]

        if "id_tutor_academico_validador" in self.__dict__:
            self.id_tutor_academico_aprobador = self.__dict__["id_tutor_academico_validador"]
            del self.__dict__["id_tutor_academico_validador"]
