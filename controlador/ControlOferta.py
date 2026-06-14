from __future__ import annotations

from datetime import date

from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.utilidades.Excepciones import EntidadDuplicadaError, ReglaNegocioError, ValidacionError
from modelo.utilidades.IDgenerator import generar_id
from modelo.utilidades.ManejoDatos import ManejoDatos


class ControlOferta:

    def registrar_empresa(
        self,
        nombre_empresa: str,
        email: str,
        razon_social: str,
        ruc: str,
        sector: str,
        ubicacion: str,
        mision: str,
        vision: str,
        convenio_vigente: bool,
    ) -> Empresa:
        if not nombre_empresa.strip():
            raise ValidacionError("El nombre de la empresa es obligatorio.")
        if "@" not in email:
            raise ValidacionError("El email de la empresa no tiene un formato valido.")
        if not ruc.strip():
            raise ValidacionError("El RUC de la empresa es obligatorio.")
        if ManejoDatos("empresas").buscar_por_campo("ruc", ruc):
            raise EntidadDuplicadaError(f"Ya existe una empresa con RUC {ruc}.")

        empresa = Empresa(
            id_empresa=generar_id("EMP"),
            nombre_empresa=nombre_empresa,
            email=email,
            razon_social=razon_social,
            ruc=ruc,
            sector=sector,
            ubicacion=ubicacion,
            mision=mision,
            vision=vision,
            convenio_vigente=convenio_vigente,
        )
        empresa.guardar()
        return empresa

    def editar_estado_convenio(self, id_empresa: str, estado: bool) -> Empresa:
        empresa = Empresa.obtener_por_id(id_empresa)
        empresa.editar_estado_convenio(estado)
        empresa.guardar()
        return empresa

    def crear_oferta(
        self,
        id_empresa: str,
        titulo: str,
        descripcion: str,
        requisitos: str,
        area: str,
        cupos: int,
        fecha_cierre: date,
    ) -> Oferta:
        Empresa.obtener_por_id(id_empresa)
        if cupos <= 0:
            raise ValidacionError("La oferta debe tener al menos un cupo.")
        if fecha_cierre < date.today():
            raise ValidacionError("La fecha de cierre no puede estar vencida.")

        oferta = Oferta(
            id_oferta=generar_id("OFE"),
            id_empresa=id_empresa,
            titulo=titulo,
            descripcion=descripcion,
            requisitos=requisitos,
            area=area,
            cupos=cupos,
            fecha_publicacion=date.today(),
            fecha_cierre=fecha_cierre,
        )
        oferta.guardar()
        return oferta

    def listar_empresas(self) -> list[Empresa]:
        return Empresa.cargar_todos()

    def listar_ofertas(self, solo_disponibles: bool = False) -> list[Oferta]:
        ofertas = Oferta.cargar_todos()
        if solo_disponibles:
            return [oferta for oferta in ofertas if oferta.esta_disponible()]
        return ofertas

    def cerrar_oferta(self, id_oferta: str) -> Oferta:
        oferta = Oferta.obtener_por_id(id_oferta)
        oferta.estado = "cerrada"
        oferta.guardar()
        return oferta

