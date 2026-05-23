from modelo.Actividad import Actividad
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Practica import Practica
from modelo.Usuario import Usuario
from utilidades.ManejoDatos import ManejoDatos


class ControlAdministrador:

    def listar_entidades(self, nombre_archivo: str) -> list[object]:
        return ManejoDatos(nombre_archivo).cargar()

    def activar_desactivar_cuenta(self, id_usuario: str, activo: bool) -> Usuario:
        usuario = Usuario.obtener_por_id(id_usuario)
        usuario.activo = activo
        usuario.guardar()
        return usuario

    def generar_reportes(self) -> dict[str, int]:
        practicas = Practica.cargar_todo()
        return {
            "usuarios": len(Usuario.cargar_todo()),
            "empresas": len(Empresa.cargar_todo()),
            "ofertas": len(Oferta.cargar_todo()),
            "postulaciones": len(Postulacion.cargar_todo()),
            "practicas_activas": len([p for p in practicas if p.estado == "activa"]),
            "practicas_finalizadas": len([p for p in practicas if p.estado == "finalizada"]),
            "actividades": len(Actividad.cargar_todo()),
        }

    def mantenimiento_general(self) -> dict[str, int]:
        """Retorna conteos por archivo sin modificar datos."""

        archivos = [
            "usuarios",
            "empresas",
            "ofertas",
            "postulaciones",
            "practicas",
            "actividades",
            "formularios",
            "documentos",
            "solicitudes",
            "convenios",
        ]
        return {archivo: len(ManejoDatos(archivo).cargar()) for archivo in archivos}
