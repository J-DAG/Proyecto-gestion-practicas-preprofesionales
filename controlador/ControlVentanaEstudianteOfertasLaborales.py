from pathlib import Path

from PyQt6 import QtWidgets

from controlador.ControlOferta import ControlOferta
from controlador.ControlPostulacion import ControlPostulacion
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Usuario import Estudiante
from modelo.utilidades.Excepciones import SistemaPracticasError
from modelo.utilidades.ManejoDatos import ManejoDatos
from vista.estilos import EstilosClase
from vista.ui_EST_ofertas_laborales import Ui_FormESTOfertasLaborales


class ControlVentanaEstudianteOfertasLaborales(QtWidgets.QWidget, Ui_FormESTOfertasLaborales):
    def __init__(self, usuario: Estudiante, ventana_estudiante=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_estudiante = ventana_estudiante
        self.login = login
        self.ofertas = ControlOferta()
        self.postulaciones = ControlPostulacion()
        self.cerrando_sesion = False
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnInico.clicked.connect(self.volver_inicio)
        self.btnMiPractica.clicked.connect(self.ver_progreso)
        self.btnMisPostulaciones.clicked.connect(self.ver_postulaciones)
        self.btnOfertaLaboral.clicked.connect(self.cargar_datos)
        self.btnMisFormularios.clicked.connect(self.ver_formularios)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnBuscar.clicked.connect(self.buscar_ofertas)
        self.txtBuscar.returnPressed.connect(self.buscar_ofertas)
        self.txtBuscar.textChanged.connect(self.buscar_ofertas)
        self.btnAplicarPostulacion.clicked.connect(self.aplicar_postulacion)
        self.btnCancelarPostulacion.clicked.connect(self.cancelar_postulacion)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Empresa", "Titulo", "Area", "Cupos", "Cierre", "Estado"]
        self.tblOfertasLaborales.setColumnCount(len(columnas))
        self.tblOfertasLaborales.setHorizontalHeaderLabels(columnas)
        self.tblOfertasLaborales.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblOfertasLaborales.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblOfertasLaborales.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblOfertasLaborales.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblOfertasLaborales.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        self._llenar_tabla(self.ofertas.listar_ofertas(solo_disponibles=True))

    def buscar_ofertas(self):
        texto = self.txtBuscar.text().strip().lower()
        ofertas = self.ofertas.listar_ofertas(solo_disponibles=True)
        if texto:
            ofertas = [
                oferta
                for oferta in ofertas
                if texto in oferta.id_oferta.lower()
                or texto in oferta.titulo.lower()
                or texto in oferta.area.lower()
                or texto in self._nombre_empresa(oferta).lower()
            ]
        self._llenar_tabla(ofertas)

    def aplicar_postulacion(self):
        oferta = self._oferta_seleccionada()
        if oferta is None:
            return
        from controlador.ControlVentanaAdjuntarMalla import ControlVentanaAdjuntarMalla

        self.subventana = ControlVentanaAdjuntarMalla(self.usuario, oferta, self)
        self.subventana.show()

    def cancelar_postulacion(self):
        oferta = self._oferta_seleccionada()
        if oferta is None:
            return
        postulacion = self._postulacion_pendiente_oferta(oferta.id_oferta)
        if postulacion is None:
            QtWidgets.QMessageBox.information(
                self,
                "Sin postulacion pendiente",
                "No existe una postulacion pendiente del estudiante para esta oferta.",
            )
            return

        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Cancelar postulacion",
            f"Se cancelara la postulacion {postulacion.id_postulacion}. Desea continuar?",
        )
        if respuesta != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        datos = {
            p.id_postulacion: p
            for p in Postulacion.cargar_todos()
            if p.id_postulacion != postulacion.id_postulacion
        }
        ManejoDatos("postulaciones").guardar(datos, "id_postulacion")
        self._eliminar_documento_cancelado(postulacion)
        QtWidgets.QMessageBox.information(self, "Postulacion cancelada", "La postulacion pendiente fue cancelada.")
        self._refrescar_vistas()

    def ver_progreso(self):
        from controlador.ControlVentanaEstudiantePractica import ControlVentanaEstudiantePractica
        self._abrir_ventana(ControlVentanaEstudiantePractica(self.usuario, self.ventana_estudiante, self.login))

    def ver_formularios(self):
        from controlador.ControlVentanaEstudianteFormularios import ControlVentanaEstudianteFormularios
        self._abrir_ventana(ControlVentanaEstudianteFormularios(self.usuario, self.ventana_estudiante, self.login))

    def ver_postulaciones(self):
        from controlador.ControlVentanaEstudiantePostulaciones import ControlVentanaEstudiantePostulaciones
        self._abrir_ventana(ControlVentanaEstudiantePostulaciones(self.usuario, self.ventana_estudiante, self.login))

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()
        if self.ventana_estudiante is not None:
            self.ventana_estudiante.salir()

    def closeEvent(self, event):
        if self.cerrando_sesion:
            super().closeEvent(event)
            return
        self._mostrar_principal()
        self.hide()
        event.ignore()

    def _llenar_tabla(self, ofertas: list[Oferta]):
        self.tblOfertasLaborales.setRowCount(len(ofertas))
        for fila, oferta in enumerate(ofertas):
            valores = [
                oferta.id_oferta,
                self._nombre_empresa(oferta),
                oferta.titulo,
                oferta.area,
                oferta.cupos,
                oferta.fecha_cierre,
                oferta.estado,
            ]
            for columna, valor in enumerate(valores):
                self.tblOfertasLaborales.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def _oferta_seleccionada(self) -> Oferta | None:
        fila = self.tblOfertasLaborales.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione una oferta de la tabla.")
            return None
        item = self.tblOfertasLaborales.item(fila, 0)
        if item is None:
            return None
        return Oferta.buscar_por_id(item.text())

    def _postulacion_pendiente_oferta(self, id_oferta: str) -> Postulacion | None:
        for postulacion in Postulacion.cargar_todos():
            if (
                postulacion.id_estudiante == self.usuario.id_usuario
                and postulacion.id_oferta == id_oferta
                and postulacion.estado == "pendiente"
            ):
                return postulacion
        return None

    def _nombre_empresa(self, oferta: Oferta) -> str:
        empresa = Empresa.buscar_por_id(oferta.id_empresa)
        return empresa.nombre_empresa if empresa else oferta.id_empresa

    def _eliminar_documento_cancelado(self, postulacion: Postulacion):
        if not postulacion.ruta_documento_malla:
            return
        try:
            Path(postulacion.ruta_documento_malla).unlink(missing_ok=True)
        except OSError:
            pass

    def _abrir_ventana(self, ventana):
        self.subventana = ventana
        self.subventana.show()
        self.hide()

    def _refrescar_vistas(self):
        self.cargar_datos()
        if self.ventana_estudiante is not None:
            self.ventana_estudiante.cargar_datos()

    def _mostrar_principal(self):
        if self.ventana_estudiante is not None:
            self.ventana_estudiante.cargar_datos()
            self.ventana_estudiante.show()
            self.ventana_estudiante.raise_()
            self.ventana_estudiante.activateWindow()

