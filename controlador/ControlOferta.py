from pathlib import Path
from utilidades.ManejoDatos import ManejoDatos
from modelo.Oferta import Oferta

class ControlOferta:
    archivo_ofertas = Path('datos/ofertas.dat')
    def crear_ofertas(self,datos: []):
        oferta = Oferta(
            id_empresa=datos['id_empresa'],
            titulo=datos['titulo'],
            descripcion=datos['descripcion'],
            requisitos=datos['requisitos'],
            cupos=datos['cupos']
        )

        registros = ManejoDatos.cargar_datos(self.archivo_ofertas)
        registros.append(oferta)
        ManejoDatos.guardar_datos(self.archivo_ofertas, registros)

    def listar_ofertas(self):
        return ManejoDatos.cargar_datos(self.archivo_ofertas)