
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Optional, TypeVar

from utilidades.Excepciones import EntidadNoEncontradaError
from utilidades.ManejoDatos import ManejoDatos


T = TypeVar("T", bound="BasePersistente")


@dataclass
class BasePersistente:
    id: str = field(init=False)

    archivo: ClassVar[str] = ""
    campo_id: ClassVar[str] = "id"

    def guardar(self) -> None:
        ManejoDatos(self.archivo).actualizar(self, self.campo_id)

    @classmethod
    def cargar_todos(cls: type[T]) -> list[T]:
        return ManejoDatos(cls.archivo).cargar()

    @classmethod
    def buscar_por_id(cls: type[T], identificador: str) -> Optional[T]:
        return ManejoDatos(cls.archivo).buscar_por_id(identificador, cls.campo_id)

    @classmethod
    def obtener_por_id(cls: type[T], identificador: str) -> T:
        entidad = cls.buscar_por_id(identificador)
        if entidad is None:
            raise EntidadNoEncontradaError(
                f"{cls.__name__} con id '{identificador}' no existe."
            )
        return entidad

    def obtener_campo(self, campo: str) -> Any:
        return getattr(self, campo)
