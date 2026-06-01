from PyQt6 import QtWidgets

from modelo.Empresa import Empresa
from modelo.Usuario import Coordinador
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

    def _mostrar_principal(self):
        if self.ventana_coordinador is not None:
            self.ventana_coordinador.cargar_datos()
            self.ventana_coordinador.cargar_resumen()
            self.ventana_coordinador.show()
            self.ventana_coordinador.raise_()
            self.ventana_coordinador.activateWindow()
