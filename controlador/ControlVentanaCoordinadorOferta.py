from PyQt6 import QtCore, QtWidgets

from controlador.ControlVentanaCrearOferta import ControlVentanaCrearOferta
from controlador.ControlVentanaEditarOferta import ControlVentanaEditarOferta
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Usuario import Coordinador
from utilidades.Excepciones import ReglaNegocioError, SistemaPracticasError
from utilidades.ManejoDatos import ManejoDatos
from vista.estilos import EstilosClase
from vista.ui_coordinador_ofertas import Ui_frmOfertas


class ControlVentanaCoordinadorOferta(QtWidgets.QWidget, Ui_frmOfertas):
    def __init__(self, usuario: Coordinador, ventana_coordinador=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_coordinador = ventana_coordinador
        self.login = login
        self.subventana = None
        self.cerrando_sesion = False
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnInicio.clicked.connect(self.volver_inicio)
        self.btnReportes.clicked.connect(self.abrir_reportes)
        self.btnEstudiantes.clicked.connect(self.abrir_estudiantes)
        self.btnTutores.clicked.connect(self.abrir_tutores)
        self.btnOfertas.clicked.connect(self.cargar_datos)
        self.btnEmpresa.clicked.connect(self.abrir_empresas)
        self.btnPracticas.clicked.connect(self.abrir_practicas)
        self.btnPostulaciones.clicked.connect(self.abrir_postulaciones)
        self.btnBuscar.clicked.connect(self.buscar_ofertas)
        self.txtBuscar.returnPressed.connect(self.buscar_ofertas)
        self.txtBuscar.textChanged.connect(self.buscar_ofertas)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnEditar.clicked.connect(self.editar_oferta)
        self.btnEliminar.clicked.connect(self.eliminar_oferta)
        self.btnNuevaOferta.clicked.connect(self.nueva_oferta)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Empresa", "Titulo", "Area", "Cupos", "Cierre", "Estado"]
        self.tblOfertas.setColumnCount(len(columnas))
        self.tblOfertas.setHorizontalHeaderLabels(columnas)
        self.tblOfertas.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblOfertas.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblOfertas.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblOfertas.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblOfertas.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        self._llenar_tabla(Oferta.cargar_todos())

    def buscar_ofertas(self):
        texto = self.txtBuscar.text().strip().lower()
        ofertas = Oferta.cargar_todos()
        if texto:
            ofertas = [
                oferta
                for oferta in ofertas
                if texto in oferta.id_oferta.lower()
                or texto in oferta.id_empresa.lower()
                or texto in oferta.titulo.lower()
                or texto in oferta.area.lower()
                or texto in oferta.estado.lower()
            ]
        self._llenar_tabla(ofertas)

    def _llenar_tabla(self, ofertas: list[Oferta]):
        self.tblOfertas.setRowCount(len(ofertas))
        for fila, oferta in enumerate(ofertas):
            valores = [
                oferta.id_oferta,
                oferta.id_empresa,
                oferta.titulo,
                oferta.area,
                oferta.cupos,
                oferta.fecha_cierre,
                oferta.estado,
            ]
            for columna, valor in enumerate(valores):
                self.tblOfertas.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def nueva_oferta(self):
        self._abrir_formulario(ControlVentanaCrearOferta(self))

    def editar_oferta(self):
        oferta = self._oferta_seleccionada()
        if oferta is None:
            return
        self._abrir_formulario(ControlVentanaEditarOferta(oferta, self))

    def eliminar_oferta(self):
        oferta = self._oferta_seleccionada()
        if oferta is None:
            return

        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Eliminar oferta",
            f"Se eliminara la oferta {oferta.titulo}. Desea continuar?",
        )
        if respuesta != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        try:
            self._validar_eliminacion(oferta)
            datos = ManejoDatos("ofertas").cargar_diccionario("id_oferta")
            datos.pop(oferta.id_oferta, None)
            ManejoDatos("ofertas").guardar(datos, "id_oferta")
            QtWidgets.QMessageBox.information(self, "Oferta eliminada", "Oferta eliminada correctamente.")
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo eliminar", str(error))

    def _oferta_seleccionada(self) -> Oferta | None:
        fila = self.tblOfertas.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione una oferta de la tabla.")
            return None

        item = self.tblOfertas.item(fila, 0)
        if item is None:
            return None
        return Oferta.buscar_por_id(item.text())

    def _validar_eliminacion(self, oferta: Oferta):
        postulaciones = [
            postulacion
            for postulacion in Postulacion.cargar_todos()
            if postulacion.id_oferta == oferta.id_oferta
        ]
        if postulaciones:
            raise ReglaNegocioError(
                "No se puede eliminar una oferta con postulaciones registradas. "
                "Conserve la oferta o cierrela para no aceptar nuevas postulaciones."
            )

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def abrir_empresas(self):
        from controlador.ControlVentanaCoordinadorEmpresa import ControlVentanaCoordinadorEmpresa
        self._abrir_ventana(ControlVentanaCoordinadorEmpresa(self.usuario, self.ventana_coordinador, self.login))

    def abrir_estudiantes(self):
        from controlador.ControlVentanaCoordinadorEstudiantes import ControlVentanaCoordinadorEstudiantes
        self._abrir_ventana(ControlVentanaCoordinadorEstudiantes(self.usuario, self.ventana_coordinador, self.login))

    def abrir_postulaciones(self):
        from controlador.ControlVentanaCoordinadorPostulacion import ControlVentanaCoordinadorPostulacion
        self._abrir_ventana(ControlVentanaCoordinadorPostulacion(self.usuario, self.ventana_coordinador, self.login))

    def abrir_practicas(self):
        from controlador.ControlVentanaCoordinadorPractica import ControlVentanaCoordinadorPractica
        self._abrir_ventana(ControlVentanaCoordinadorPractica(self.usuario, self.ventana_coordinador, self.login))

    def abrir_reportes(self):
        from controlador.ControlVentanaCoordinadorReportes import ControlVentanaCoordinadorReportes
        self._abrir_ventana(ControlVentanaCoordinadorReportes(self.usuario, self.ventana_coordinador, self.login))

    def abrir_tutores(self):
        from controlador.ControlVentanaCoordinadorTutores import ControlVentanaCoordinadorTutores
        self._abrir_ventana(ControlVentanaCoordinadorTutores(self.usuario, self.ventana_coordinador, self.login))

    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()
        if self.ventana_coordinador is not None:
            self.ventana_coordinador.salir()

    def closeEvent(self, event):
        if self.cerrando_sesion:
            super().closeEvent(event)
            return
        self._mostrar_principal()
        self.hide()
        event.ignore()

    def _abrir_ventana(self, ventana):
        self.subventana = ventana
        self.subventana.show()
        self.hide()

    def _abrir_formulario(self, ventana):
        self.subventana = ventana
        self.subventana.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.subventana.destroyed.connect(self._volver_desde_formulario)
        self.subventana.show()
        self.hide()

    def _volver_desde_formulario(self):
        self.subventana = None
        self._refrescar_vistas()
        self.show()

    def _refrescar_vistas(self):
        self.cargar_datos()
        if self.ventana_coordinador is not None:
            self.ventana_coordinador.cargar_datos()
            self.ventana_coordinador.cargar_resumen()

    def _mostrar_principal(self):
        if self.ventana_coordinador is not None:
            self.ventana_coordinador.cargar_datos()
            self.ventana_coordinador.cargar_resumen()
            self.ventana_coordinador.show()
            self.ventana_coordinador.raise_()
            self.ventana_coordinador.activateWindow()
