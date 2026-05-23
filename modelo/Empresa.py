from dataclasses import dataclass
from typing import ClassVar

from modelo.BasePersistencia import BasePersistente

@dataclass
class Empresa(BasePersistente):
    id_empresa: str
    nombre_empresa: str
    email: str
    razon_social: str
    ruc: str
    sector: str
    ubicacion: str
    mision: str
    vision: str
    convenio_vigente: bool = True

    archivo: ClassVar[str] = "empresas"
    campo_id: ClassVar[str] = "id_empresa"

    def __post_init__(self) -> None:
        self.id = self.id_empresa
        self.migrar_campos_legacy()

    def __setstate__(self, estado: dict[str, object]) -> None:
        self.__dict__.update(estado)
        self.migrar_campos_legacy()

    def editar_estado_convenio(self, estado: bool) -> None:
        self.convenio_vigente = estado

    def migrar_campos_legacy(self) -> None:
        if hasattr(self, "tiene_convenio"):
            self.convenio_vigente = bool(getattr(self, "tiene_convenio"))
            delattr(self, "tiene_convenio")

        if not getattr(self, "nombre_empresa", ""):
            self.nombre_empresa = self.razon_social

        if not getattr(self, "email", ""):
            self.email = ""
