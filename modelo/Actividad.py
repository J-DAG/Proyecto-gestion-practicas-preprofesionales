from dataclasses import dataclass
from datetime import date
from typing import ClassVar

from modelo.BasePersistencia import BasePersistente
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
        """Compatibilidad: antes validada significaba actividad cumplida."""

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
        """Alias legado: aprueba la actividad desde el tutor academico."""

        self.aprobar(id_tutor_academico)

    def obtener_estado(self) -> str:
        if self.completada_por_tutor_empresarial:
            return "Completado"
        if self.aprobada_por_tutor_academico:
            return "Aprobado por tutor academico"
        return "Pendiente de aprobacion academica"

    def _migrar_campos_legacy(self) -> None:
        """Adapta actividades guardadas antes de separar aprobacion y completado."""

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
