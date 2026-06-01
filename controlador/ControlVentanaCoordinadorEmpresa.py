from PyQt6 import QtCore, QtWidgets

from controlador.ControlVentanaCrearEmpresa import ControlVentanaCrearEmpresa
from controlador.ControlVentanaEditarEmpresa import ControlVentanaEditarEmpresa
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.Practica import Practica
from modelo.Usuario import Coordinador, TutorEmpresarial, Usuario
from utilidades.Excepciones import ReglaNegocioError, SistemaPracticasError
from utilidades.ManejoDatos import ManejoDatos
from vista.ui_coordinador_empresa import Ui_frmAdministracionEmpresas


class ControlVentanaCoordinadorEmpresa(QtWidgets.QWidget, Ui_frmAdministracionEmpresas):
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
        self.btnOfertas.clicked.connect(self.abrir_ofertas)
        self.btnPracticas.clicked.connect(self.abrir_practicas)
        self.btnPostulaciones.clicked.connect(self.abrir_postulaciones)
        self.btnEmpresa.clicked.connect(self.cargar_datos)
        self.btnBuscar.clicked.connect(self.buscar_empresas)
        self.txtBuscar.returnPressed.connect(self.buscar_empresas)
        self.txtBuscar.textChanged.connect(self.buscar_empresas)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnEliminar.clicked.connect(self.eliminar_empresa)
        self.btnNuevoEmpresa.clicked.connect(self.crear_empresa)
        self.btnEditar.clicked.connect(self.editar_empresa)

    def configurar_tabla(self):
        columnas = ["ID", "Nombre", "RUC", "Email", "Sector", "Ubicacion", "Convenio"]
        self.tblEmpresas.setColumnCount(len(columnas))
        self.tblEmpresas.setHorizontalHeaderLabels(columnas)
        self.tblEmpresas.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblEmpresas.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblEmpresas.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblEmpresas.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblEmpresas.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        self._llenar_tabla(Empresa.cargar_todos())

    def buscar_empresas(self):
        texto = self.txtBuscar.text().strip().lower()
        empresas = Empresa.cargar_todos()
        if texto:
            empresas = [
                empresa
                for empresa in empresas
                if texto in empresa.id_empresa.lower()
                or texto in empresa.nombre_empresa.lower()
                or texto in empresa.ruc.lower()
                or texto in empresa.email.lower()
                or texto in empresa.sector.lower()
                or texto in empresa.ubicacion.lower()
            ]
        self._llenar_tabla(empresas)

    def _llenar_tabla(self, empresas: list[Empresa]):
        self.tblEmpresas.setRowCount(len(empresas))
        for fila, empresa in enumerate(empresas):
            valores = [
                empresa.id_empresa,
                empresa.nombre_empresa,
                empresa.ruc,
                empresa.email,
                empresa.sector,
                empresa.ubicacion,
                "Si" if empresa.convenio_vigente else "No",
            ]
            for columna, valor in enumerate(valores):
                self.tblEmpresas.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def crear_empresa(self):
        self._abrir_formulario(ControlVentanaCrearEmpresa(self))

    def editar_empresa(self):
        empresa = self._empresa_seleccionada()
        if empresa is None:
            return
        self._abrir_formulario(ControlVentanaEditarEmpresa(empresa, self))

    def eliminar_empresa(self):
        empresa = self._empresa_seleccionada()
        if empresa is None:
            return

        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Eliminar empresa",
            f"Se eliminara la empresa {empresa.nombre_empresa}. Desea continuar?",
        )
        if respuesta != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        try:
            self._validar_eliminacion(empresa)
            datos = ManejoDatos("empresas").cargar_diccionario("id_empresa")
            datos.pop(empresa.id_empresa, None)
            ManejoDatos("empresas").guardar(datos, "id_empresa")
            QtWidgets.QMessageBox.information(self, "Empresa eliminada", "Empresa eliminada correctamente.")
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo eliminar", str(error))

    def _empresa_seleccionada(self) -> Empresa | None:
        fila = self.tblEmpresas.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione una empresa de la tabla.")
            return None

        item = self.tblEmpresas.item(fila, 0)
        if item is None:
            return None
        return Empresa.buscar_por_id(item.text())

    def _validar_eliminacion(self, empresa: Empresa):
        if any(oferta.id_empresa == empresa.id_empresa for oferta in Oferta.cargar_todos()):
            raise ReglaNegocioError("No se puede eliminar una empresa con ofertas registradas.")
        if any(practica.id_empresa == empresa.id_empresa for practica in Practica.cargar_todos()):
            raise ReglaNegocioError("No se puede eliminar una empresa con practicas asociadas.")
        if any(
            isinstance(usuario, TutorEmpresarial) and usuario.id_empresa == empresa.id_empresa
            for usuario in Usuario.cargar_todos()
        ):
            raise ReglaNegocioError("No se puede eliminar una empresa con tutores empresariales asociados.")

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def abrir_empresas(self):
        self.cargar_datos()

    def abrir_estudiantes(self):
        from controlador.ControlVentanaCoordinadorEstudiantes import ControlVentanaCoordinadorEstudiantes
        self._abrir_ventana(ControlVentanaCoordinadorEstudiantes(self.usuario, self.ventana_coordinador, self.login))

    def abrir_ofertas(self):
        from controlador.ControlVentanaCoordinadorOferta import ControlVentanaCoordinadorOferta
        self._abrir_ventana(ControlVentanaCoordinadorOferta(self.usuario, self.ventana_coordinador, self.login))

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
