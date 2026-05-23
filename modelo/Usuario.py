import hashlib
import uuid
from dataclasses import dataclass
from typing import ClassVar

from configuracion.Ajustes import ROLES
from modelo.BasePersistencia import BasePersistente


@dataclass
class Usuario(BasePersistente):
    id_usuario: str
    nombre: str
    email: str
    password: str
    rol: str
    activo: bool = True
    archivo: ClassVar[str] = "usuarios"
    campo_id: ClassVar[str] = "id_usuario"

    def __post_init__(self) -> None:
        self.id = self.id_usuario
        if len(self.password) != 64:
            self.password = self.encriptar_password(self.password)

    def encriptar_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verificar_password(self, password: str) -> bool:
        return self.password == self.encriptar_password(password)

    def autenticar(self, password: str) -> bool:
        return self.activo and self.verificar_password(password)


@dataclass
class Estudiante(Usuario):
    cedula: str = ""
    carrera: str = ""
    ciclo_actual: int = 1
    matriculado: bool = False
    practicas_previas: int = 0
    practica_activa: bool = False
    id_practica_activa: str | None = None

    def __post_init__(self) -> None:
        self.rol = ROLES["ESTUDIANTE"]
        super().__post_init__()

    def puede_realizar_practicas(self) -> bool:
        return self.matriculado and self.ciclo_actual >= 6 and not self.practica_activa

    def tiene_practica_activa(self) -> bool:
        return self.practica_activa or self.id_practica_activa is not None

    def asignar_practica_activa(self, id_practica: str) -> None:
        self.practica_activa = True
        self.id_practica_activa = id_practica

    def liberar_practica_activa(self) -> None:
        self.practica_activa = False
        self.id_practica_activa = None


@dataclass
class Coordinador(Usuario):
    def __post_init__(self) -> None:
        self.rol = ROLES["COORDINADOR"]
        super().__post_init__()


@dataclass
class TutorAcademico(Usuario):
    carrera: str = ""

    def __post_init__(self) -> None:
        self.rol = ROLES["TUTOR_ACADEMICO"]
        super().__post_init__()


@dataclass
class TutorEmpresarial(Usuario):
    id_empresa: str = ""
    cargo: str = ""

    def __post_init__(self) -> None:
        self.rol = ROLES["TUTOR_EMPRESARIAL"]
        super().__post_init__()


@dataclass
class Administrador(Usuario):
    def __post_init__(self) -> None:
        self.rol = ROLES["ADMINISTRADOR"]
        super().__post_init__()
