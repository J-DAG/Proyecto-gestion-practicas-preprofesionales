from PyQt6 import QtWidgets

from controlador.ControlVentanaVerActividades import ControlVentanaVerActividades
from modelo.Practica import Practica
from modelo.Usuario import Coordinador
from vista.ui_coordinador_practicas import Ui_frmAdministracionPracticas


class ControlVentanaCoordinadorPractica(QtWidgets.QWidget, Ui_frmAdministracionPracticas):
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
        self.btnEmpresa.clicked.connect(self.abrir_empresas)
        self.btnPracticas.clicked.connect(self.cargar_datos)
        self.btnPostulaciones.clicked.connect(self.abrir_postulaciones)
        self.btnBuscar.clicked.connect(self.buscar_practicas)
        self.txtBuscar.returnPressed.connect(self.buscar_practicas)
        self.txtBuscar.textChanged.connect(self.buscar_practicas)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnVerActividades.clicked.connect(self.ver_actividades)

    def configurar_tabla(self):
        columnas = ["ID", "Estudiante", "Empresa", "Inicio", "Fin", "Horas", "Estado"]
        self.tblPracticas.setColumnCount(len(columnas))
        self.tblPracticas.setHorizontalHeaderLabels(columnas)
        self.tblPracticas.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblPracticas.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblPracticas.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblPracticas.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblPracticas.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        self._llenar_tabla(Practica.cargar_todos())

    def buscar_practicas(self):
        texto = self.txtBuscar.text().strip().lower()
        practicas = Practica.cargar_todos()
        if texto:
            practicas = [
                practica
                for practica in practicas
                if texto in practica.id_practica.lower()
                or texto in practica.id_estudiante.lower()
                or texto in practica.id_empresa.lower()
                or texto in practica.estado.lower()
            ]
        self._llenar_tabla(practicas)

    def _llenar_tabla(self, practicas: list[Practica]):
        self.tblPracticas.setRowCount(len(practicas))
        for fila, practica in enumerate(practicas):
            valores = [
                practica.id_practica,
                practica.id_estudiante,
                practica.id_empresa,
                practica.fecha_inicio,
                practica.fecha_fin,
                practica.horas_cumplidas,
                practica.estado,
            ]
            for columna, valor in enumerate(valores):
                self.tblPracticas.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def ver_actividades(self):
        practica = self._practica_seleccionada()
        if practica is None:
            return
        self.subventana = ControlVentanaVerActividades(practica, self)
        self.subventana.show()
        self.hide()

    def _practica_seleccionada(self) -> Practica | None:
        fila = self.tblPracticas.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione una practica de la tabla.")
            return None

        item = self.tblPracticas.item(fila, 0)
        if item is None:
            return None
        return Practica.buscar_por_id(item.text())

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def abrir_empresas(self):
        from controlador.ControlVentanaCoordinadorEmpresa import ControlVentanaCoordinadorEmpresa
        self._abrir_ventana(ControlVentanaCoordinadorEmpresa(self.usuario, self.ventana_coordinador, self.login))

    def abrir_estudiantes(self):
        from controlador.ControlVentanaCoordinadorEstudiantes import ControlVentanaCoordinadorEstudiantes
        self._abrir_ventana(ControlVentanaCoordinadorEstudiantes(self.usuario, self.ventana_coordinador, self.login))

    def abrir_ofertas(self):
        from controlador.ControlVentanaCoordinadorOferta import ControlVentanaCoordinadorOferta
        self._abrir_ventana(ControlVentanaCoordinadorOferta(self.usuario, self.ventana_coordinador, self.login))

    def abrir_postulaciones(self):
        from controlador.ControlVentanaCoordinadorPostulacion import ControlVentanaCoordinadorPostulacion
        self._abrir_ventana(ControlVentanaCoordinadorPostulacion(self.usuario, self.ventana_coordinador, self.login))

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
