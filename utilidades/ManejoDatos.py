import pickle
from pathlib import Path
from typing import TypeVar, Optional, Any, Callable

from configuracion.Ajustes import ARCHIVO_DATOS, DATOS_DIR
from utilidades.Excepciones import PermisoArchivoError, PersistenciaError, FormatoDatosInvalidoError, \
    ArchivoDatosCorruptoError

T = TypeVar("T")
class ManejoDatos:
    def __init__(self, archivo: str | Path) -> None:
        self.ruta = ARCHIVO_DATOS.get(str(archivo), Path(archivo))
        self.asegurar_directorio()

    def cargar(self) -> list[T]:
        return list(self.cargar_diccionario().values())

    def guardar(self, datos: dict[str, T] | list[T], campo_id: str = "id") -> None:
        self.asegurar_directorio()
        datos_indexados = self.normalizar_diccionario(datos, campo_id)
        try:
            with self.ruta.open("wb") as archivo:
                pickle.dump(datos_indexados, archivo)
        except PermissionError as error:
            raise PermisoArchivoError(
                f"No tiene permisos para escribir en '{self.ruta}'."
            ) from error
        except OSError as error:
            raise PersistenciaError(
                f"No se pudo guardar el archivo '{self.ruta}': {error}"
            ) from error
        except pickle.PickleError as error:
            raise PersistenciaError(
                f"No se pudo serializar la informacion en '{self.ruta}'."
            ) from error

    def actualizar(self, entidad: T, campo_id: str = "id") -> None:
        datos = self.cargar_diccionario(campo_id)
        valor_id = str(getattr(entidad, campo_id))
        datos[valor_id] = entidad
        self.guardar(datos, campo_id)

    def buscar_por_id(self, identificador: str, campo_id: str = "id") -> Optional[T]:
        datos = self.cargar_diccionario(campo_id)
        entidad = datos.get(str(identificador))
        if entidad is not None:
            return entidad

        return self.buscar_por_campo(campo_id, identificador)

    def buscar_por_campo(self, campo: str, valor: Any) -> Optional[T]:
        for entidad in self.cargar():
            if getattr(entidad, campo, None) == valor:
                return entidad
        return None

    def filtrar(self, criterio: Callable[[T], bool] | None = None, **campos: Any) -> list[T]:
        datos = self.cargar()
        if criterio is not None:
            return [entidad for entidad in datos if criterio(entidad)]

        return [
            entidad
            for entidad in datos
            if all(getattr(entidad, campo, None) == valor for campo, valor in campos.items())
        ]

    def _leer_archivo(self) -> object:
        try:
            if not self.ruta.exists():
                self.ruta.touch()
                return {}
            if self.ruta.stat().st_size == 0:
                return {}

            with self.ruta.open("rb") as archivo:
                return pickle.load(archivo)
        except FileNotFoundError:
            return {}
        except EOFError:
            return {}
        except PermissionError as error:
            raise PermisoArchivoError(
                f"No tiene permisos para leer '{self.ruta}'."
            ) from error
        except (pickle.PickleError, AttributeError, ImportError, IndexError) as error:
            raise ArchivoDatosCorruptoError(
                f"El archivo '{self.ruta}' esta corrupto o no contiene datos validos."
            ) from error
        except OSError as error:
            raise PersistenciaError(
                f"No se pudo leer el archivo '{self.ruta}': {error}"
            ) from error

    def cargar_diccionario(self, campo_id: str = "id") -> dict[str, T]:
        return self.normalizar_diccionario(self._leer_archivo(), campo_id)

    def normalizar_diccionario(
            self,
            datos: object,
            campo_id: str = "id",
    ) -> dict[str, T]:
        if isinstance(datos, dict):
            return {str(clave): valor for clave, valor in datos.items()}

        if not isinstance(datos, list):
            raise FormatoDatosInvalidoError(
                f"El archivo '{self.ruta}' tiene un formato no soportado: "
                f"{type(datos).__name__}."
            )

        datos_indexados: dict[str, T] = {}
        for entidad in datos:
            valor_id = getattr(entidad, campo_id, None) or getattr(entidad, "id", None)
            if valor_id is not None:
                datos_indexados[str(valor_id)] = entidad
                continue

            raise FormatoDatosInvalidoError(
                f"No se pudo indexar una entidad de '{self.ruta}' porque no tiene "
                f"el campo '{campo_id}'."
            )

        return datos_indexados

    def asegurar_directorio(self) -> None:
        """Garantiza que el directorio de datos exista."""

        try:
            DATOS_DIR.mkdir(parents=True, exist_ok=True)
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as error:
            raise PermisoArchivoError(
                f"No tiene permisos para crear el directorio '{self.ruta.parent}'."
            ) from error
        except OSError as error:
            raise PersistenciaError(
                f"No se pudo preparar el directorio '{self.ruta.parent}': {error}"
            ) from error
