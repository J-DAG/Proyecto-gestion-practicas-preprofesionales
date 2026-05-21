import pickle
from pathlib import Path


class ManejoDatos:
    @staticmethod
    def cargar_datos(ruta: Path):
        try:
            with open(ruta, 'rb') as archivo:
                return pickle.load(archivo)
        except FileNotFoundError:
            return []
        except EOFError:
            return []
        except Exception as e:
            raise RuntimeError(f'Error al caragr el archivo: {e}')

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
        registros = ManejoDatos.cargarDatos(ruta)
        registros = [
            r for r in registros
            if getattr(r, atributo_id) != getattr(objeto, atributo_id)
        ]
        registros.append(objeto)
        ManejoDatos.guardarDatos(ruta,registros)
