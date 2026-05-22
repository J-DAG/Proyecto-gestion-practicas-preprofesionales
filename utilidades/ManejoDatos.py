import pickle
from pathlib import Path
from typing import TypeVar

from configuracion.Ajustes import ARCHIVO_DATOS, DATOS_DIR
from utilidades.Excepciones import PermisoArchivoError, PersistenciaError, FormatoDatosInvalidoError, \
    ArchivoDatosCorruptoError

T = TypeVar("T")
class ManejoDatos:
    def __init__(self,archivo:str | Path):
        self.ruta = ARCHIVO_DATOS.get(str(archivo),Path(archivo))
        self.asegurar_directorio()
    def cargar(self)->list[T]:
        return list(self.cargar_diccionario().values())

    def cargar_diccionario(self,campo_id: str = "id")-> dict[str, T]:
        return self.normalizar_diccionario(self.leer_archivo(),campo_id)

    def leer_archivo(self) -> object:
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

    def normalizar_diccionario(self,
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

    def asegurar_directorio(self)-> None:
        try:
            DATOS_DIR.mkdir(parents=True,exist_ok=True)
            self.ruta.parent.mkdir(parents=True,exist_ok=True)
        except PermissionError as error:
            raise PermisoArchivoError(
                f"No se pudo crear el directorio '{self.ruta.parent}"
            ) from error
        except OSError as error:
            raise PersistenciaError(
                f"No se pudo iniciar el directorio '{self.ruta.parent}': {error}"
            ) from error

    @staticmethod
    def guardar_datos(ruta: Path,datos):
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with open(ruta, 'wb') as archivo:
                pickle.dump(datos, archivo)
        except Exception as e:
            raise RuntimeError(f'Error al guardar el archivo: {e}')

    @staticmethod
    def actualizar_datos(ruta: Path,objeto,atributo_id: str):
        registros = ManejoDatos.cargar_datos(ruta)
        registros = [
            r for r in registros
            if getattr(r, atributo_id) != getattr(objeto, atributo_id)
        ]
        registros.append(objeto)
        ManejoDatos.guardar_datos(ruta,registros)
