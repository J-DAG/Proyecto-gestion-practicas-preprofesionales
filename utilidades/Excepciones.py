
class SistemaPracticasError(Exception):
    """Error base de toda la aplicacion."""
    codigo = "SISTEMA_ERROR"
    mensaje_default = "Ocurrio un error en el sistema."

    def __init__(self, mensaje: str | None = None) -> None:
        self.mensaje = mensaje or self.mensaje_default
        super().__init__(self.mensaje)

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.mensaje}"


class ValidacionError(SistemaPracticasError):
    codigo = "VALIDACION_ERROR"
    mensaje_default = "Los datos ingresados no son validos."


class EntidadNoEncontradaError(SistemaPracticasError):
    codigo = "ENTIDAD_NO_ENCONTRADA"
    mensaje_default = "No se encontro la entidad solicitada."


class EntidadDuplicadaError(SistemaPracticasError):
    codigo = "ENTIDAD_DUPLICADA"
    mensaje_default = "La entidad que intenta registrar ya existe."


class ReglaNegocioError(SistemaPracticasError):
    codigo = "REGLA_NEGOCIO_ERROR"
    mensaje_default = "La operacion no cumple una regla de negocio."


class AutenticacionError(SistemaPracticasError):
    codigo = "AUTENTICACION_ERROR"
    mensaje_default = "Credenciales invalidas o cuenta inactiva."


class AutorizacionError(SistemaPracticasError):
    codigo = "AUTORIZACION_ERROR"
    mensaje_default = "No tiene permisos para ejecutar esta accion."


class PersistenciaError(SistemaPracticasError):
    codigo = "PERSISTENCIA_ERROR"
    mensaje_default = "Ocurrio un error al acceder a los datos."


class ArchivoDatosNoEncontradoError(PersistenciaError):
    codigo = "ARCHIVO_NO_ENCONTRADO"
    mensaje_default = "No se encontro el archivo de datos."


class ArchivoDatosVacioError(PersistenciaError):
    codigo = "ARCHIVO_VACIO"
    mensaje_default = "El archivo de datos esta vacio."


class ArchivoDatosCorruptoError(PersistenciaError):
    codigo = "ARCHIVO_CORRUPTO"
    mensaje_default = "El archivo de datos esta corrupto o no se puede leer."


class FormatoDatosInvalidoError(PersistenciaError):
    codigo = "FORMATO_DATOS_INVALIDO"
    mensaje_default = "El archivo de datos tiene un formato invalido."


class PermisoArchivoError(PersistenciaError):
    codigo = "PERMISO_ARCHIVO_ERROR"
    mensaje_default = "No tiene permisos para leer o escribir el archivo."
