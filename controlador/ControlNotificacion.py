from datetime import datetime

from modelo.Notificacion import Notificacion
from modelo.Usuario import Usuario
from utilidades.IDGenerador import id_generador
from utilidades.ManejoDatos import ManejoDatos


class ControlNotificacion:

    def crear_notificacion(
            self,
            id_usuario: str,
            titulo: str,
            mensaje: str,
            tipo: str = "informativa",
            validar_usuario: bool = True,
    ) -> Notificacion:
        if validar_usuario:
            Usuario.obtener_por_id(id_usuario)
        notificacion = Notificacion(
            id_notificacion=id_generador("NOT"),
            id_usuario=id_usuario,
            titulo=titulo,
            mensaje=mensaje,
            fecha_creacion=datetime.now(),
            tipo=tipo,
        )
        notificacion.guardar()
        return notificacion

    def listar_por_usuario(self, id_usuario: str) -> list[Notificacion]:
        return ManejoDatos("notificaciones").filtrar(id_usuario=id_usuario)

    def marcar_como_leida(self, id_notificacion: str) -> Notificacion:
        notificacion = Notificacion.obtener_por_id(id_notificacion)
        notificacion.marcar_como_leida()
        notificacion.guardar()
        return notificacion
