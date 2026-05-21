from pathlib import Path

from modelo.Estudiante import Estudiante
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from utilidades.ManejoDatos import ManejoDatos


class ControlPostulacion:
    ARCHIVO_POSTULACIONES = Path('datos/postulaciones.dat')
    def crear_postulacion(self,estudiate: Estudiante,oferta: Oferta):
        if not estudiate.puede_realizar_practicas():
            raise ValueError('El estudiante no puede realizar practicas')
        if estudiate.tiene_practica_activa():
            raise Exception('El estudiante tiene una practica activa')

        postulacion = Postulacion(
            estudiate.id_usuario,
            oferta.id_oferfa
        )
        registros = ManejoDatos.cargar_datos(self.ARCHIVO_POSTULACIONES)
        registros.append(postulacion)
        ManejoDatos.guardar_datos(self.ARCHIVO_POSTULACIONES, registros)
        return postulacion
