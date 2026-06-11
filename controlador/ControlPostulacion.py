from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

from configuracion.ajustes import DATOS_DIR, ROLES
from controlador.ControlNotificacion import ControlNotificacion
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Usuario import Estudiante, Usuario
from utilidades.Excepciones import AutorizacionError, EntidadDuplicadaError, ReglaNegocioError, ValidacionError
from utilidades.IDgenerator import generar_id
from utilidades.ManejoDatos import ManejoDatos


class ControlPostulacion:

    def crear_postulacion(
        self,
        id_estudiante: str,
        id_oferta: str,
        ruta_documento_malla: str | None = None,
    ) -> Postulacion:
        estudiante = self._obtener_estudiante(id_estudiante)
        oferta = Oferta.obtener_por_id(id_oferta)

        if not oferta.esta_disponible():
            raise ReglaNegocioError("La oferta no esta disponible.")
        if not estudiante.matriculado or estudiante.ciclo_actual < 6:
            raise ReglaNegocioError("Solo estudiantes matriculados desde sexto ciclo pueden postular.")
        if estudiante.tiene_practica_activa():
            raise ReglaNegocioError("El estudiante ya tiene una practica activa.")
        if self._tiene_postulacion_aceptada(id_estudiante):
            raise ReglaNegocioError(
                "El estudiante ya fue aceptado en una oferta y no puede seguir postulando."
            )

        existente = ManejoDatos("postulaciones").filtrar(
            id_estudiante=id_estudiante,
            id_oferta=id_oferta,
        )
        if existente:
            raise EntidadDuplicadaError("El estudiante ya postulo a esta oferta.")

        postulacion = Postulacion(
            id_postulacion=generar_id("POS"),
            id_estudiante=id_estudiante,
            id_oferta=id_oferta,
            fecha_postulacion=date.today(),
        )
        if ruta_documento_malla:
            postulacion.adjuntar_documento_malla(
                self._guardar_documento_malla(postulacion.id_postulacion, ruta_documento_malla)
            )
        postulacion.guardar()
        return postulacion

    def validar_postulacion(self, id_postulacion: str, usuario_validador: Usuario) -> Postulacion:
        if usuario_validador.rol != ROLES["COORDINADOR"]:
            raise AutorizacionError("Solo el Coordinador puede validar postulaciones.")

        postulacion = Postulacion.obtener_por_id(id_postulacion)
        if not postulacion.tiene_documento_malla():
            raise ReglaNegocioError("La postulacion no tiene adjunto el avance de malla en PDF.")
        postulacion.validar()
        postulacion.guardar()
        return postulacion

    def aceptar_postulacion(self, id_postulacion: str) -> Postulacion:
        postulacion = Postulacion.obtener_por_id(id_postulacion)
        if postulacion.estado not in {"validada", "en_terna"}:
            raise ReglaNegocioError("Solo una postulacion validada o en terna puede aceptarse.")
        if self._tiene_postulacion_aceptada(postulacion.id_estudiante, postulacion.id_postulacion):
            raise ReglaNegocioError("El estudiante ya tiene otra postulacion aceptada.")

        oferta = Oferta.obtener_por_id(postulacion.id_oferta)
        if not oferta.esta_disponible():
            raise ReglaNegocioError("La oferta no tiene cupos disponibles o ya esta cerrada.")

        postulacion.aceptar()
        postulacion.guardar()
        self._descontar_cupo_oferta(oferta)
        self._rechazar_otras_postulaciones_abiertas(postulacion)
        self._notificar_estudiante_aceptado(postulacion)
        return postulacion

    def rechazar_postulacion(self, id_postulacion: str) -> Postulacion:
        postulacion = Postulacion.obtener_por_id(id_postulacion)
        postulacion.rechazar()
        postulacion.guardar()
        return postulacion

    def generar_terna(self, id_oferta: str) -> list[Postulacion]:
        Oferta.obtener_por_id(id_oferta)
        postulaciones = ManejoDatos("postulaciones").filtrar(
            lambda p: p.id_oferta == id_oferta and p.estado == "validada"
        )

        postulaciones.sort(key=lambda p: self._obtener_estudiante(p.id_estudiante).practicas_previas)
        terna = postulaciones[:3]
        for postulacion in terna:
            postulacion.marcar_en_terna()
            postulacion.guardar()
        return terna

    def listar_postulaciones(self) -> list[Postulacion]:
        return Postulacion.cargar_todos()

    def obtener_documento_malla(self, id_postulacion: str) -> Path:
        postulacion = Postulacion.obtener_por_id(id_postulacion)
        if not postulacion.tiene_documento_malla():
            raise ReglaNegocioError("La postulacion no tiene documento adjunto.")
        ruta = Path(postulacion.ruta_documento_malla)
        if not ruta.exists():
            raise ReglaNegocioError("El archivo adjunto no existe en el almacenamiento local.")
        return ruta

    def _guardar_documento_malla(self, id_postulacion: str, ruta_origen: str) -> str:
        origen = Path(ruta_origen)
        if not origen.exists() or not origen.is_file():
            raise ValidacionError("Seleccione un archivo PDF valido.")
        if origen.suffix.lower() != ".pdf":
            raise ValidacionError("El avance de malla debe ser un archivo PDF.")

        destino_dir = DATOS_DIR / "documentos_postulacion"
        destino_dir.mkdir(parents=True, exist_ok=True)
        destino = destino_dir / f"{id_postulacion}_avance_malla.pdf"
        try:
            shutil.copy2(origen, destino)
        except OSError as error:
            raise ValidacionError(f"No se pudo guardar el PDF adjunto: {error}") from error
        return str(destino)

    def _tiene_postulacion_aceptada(
        self,
        id_estudiante: str,
        id_postulacion_excluida: str | None = None,
    ) -> bool:
        postulaciones = ManejoDatos("postulaciones").filtrar(
            id_estudiante=id_estudiante,
            estado="aceptada",
        )
        return any(
            postulacion.id_postulacion != id_postulacion_excluida
            for postulacion in postulaciones
        )

    def _rechazar_otras_postulaciones_abiertas(self, postulacion_aceptada: Postulacion) -> None:
        estados_abiertos = {"pendiente", "validada", "en_terna"}
        postulaciones = ManejoDatos("postulaciones").filtrar(
            lambda postulacion: (
                postulacion.id_estudiante == postulacion_aceptada.id_estudiante
                and postulacion.id_postulacion != postulacion_aceptada.id_postulacion
                and postulacion.estado in estados_abiertos
            )
        )

        for postulacion in postulaciones:
            postulacion.rechazar()
            postulacion.guardar()

    def _notificar_estudiante_aceptado(self, postulacion: Postulacion) -> None:
        oferta = Oferta.obtener_por_id(postulacion.id_oferta)
        empresa = Empresa.obtener_por_id(oferta.id_empresa)
        ControlNotificacion().crear_notificacion(
            id_usuario=postulacion.id_estudiante,
            titulo="Postulacion aceptada",
            mensaje=(
                f"Su postulacion a '{oferta.titulo}' fue aceptada por "
                f"{empresa.nombre_empresa}. El coordinador continuara con la generacion "
                "formal de la practica."
            ),
            tipo="postulacion",
        )

    def _descontar_cupo_oferta(self, oferta: Oferta) -> None:
        oferta.cupos = max(0, oferta.cupos - 1)
        if oferta.cupos == 0:
            oferta.estado = "cerrada"
        oferta.guardar()

    def _obtener_estudiante(self, id_estudiante: str) -> Estudiante:
        usuario = Usuario.obtener_por_id(id_estudiante)
        if not isinstance(usuario, Estudiante):
            raise ReglaNegocioError("El usuario indicado no es estudiante.")
        return usuario
