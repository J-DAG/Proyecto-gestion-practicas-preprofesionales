from PyQt6 import QtWidgets

from configuracion.ajustes import ROLES
from modelo.Usuario import Coordinador, Usuario
from vista.estilos import EstilosClase
from vista.ui_coordinador_estudiante import Ui_frmEstudiantes


class ControlVentanaCoordinadorEstudiantes(QtWidgets.QWidget, Ui_frmEstudiantes):
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
        self.btnEstudiantes.clicked.connect(self.cargar_datos)
        self.btnTutores.clicked.connect(self.abrir_tutores)
        self.btnOfertas.clicked.connect(self.abrir_ofertas)
        self.btnEmpresa.clicked.connect(self.abrir_empresas)
        self.btnPracticas.clicked.connect(self.abrir_practicas)
        self.btnPostulaciones.clicked.connect(self.abrir_postulaciones)
        self.btnBuscar.clicked.connect(self.buscar_estudiantes)
        self.txtBuscar.returnPressed.connect(self.buscar_estudiantes)
        self.txtBuscar.textChanged.connect(self.buscar_estudiantes)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Nombres", "Apellidos", "Cedula", "Email", "Carrera", "Ciclo"]
        self.tblEstudiantes.setColumnCount(len(columnas))
        self.tblEstudiantes.setHorizontalHeaderLabels(columnas)
        self.tblEstudiantes.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblEstudiantes.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblEstudiantes.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblEstudiantes.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblEstudiantes.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        self._llenar_tabla(self._estudiantes())

    def buscar_estudiantes(self):
        texto = self.txtBuscar.text().strip().lower()
        estudiantes = self._estudiantes()
        if texto:
            estudiantes = [
                estudiante
                for estudiante in estudiantes
                if texto in estudiante.id_usuario.lower()
                or texto in estudiante.nombres.lower()
                or texto in estudiante.apellidos.lower()
                or texto in estudiante.cedula.lower()
                or texto in estudiante.email.lower()
                or texto in estudiante.carrera.lower()
            ]
        self._llenar_tabla(estudiantes)

    def _estudiantes(self):
        return [usuario for usuario in Usuario.cargar_todos() if usuario.rol == ROLES["ESTUDIANTE"]]

    def _llenar_tabla(self, estudiantes: list[Usuario]):
        self.tblEstudiantes.setRowCount(len(estudiantes))
        for fila, estudiante in enumerate(estudiantes):
            valores = [
                estudiante.id_usuario,
                estudiante.nombres,
                estudiante.apellidos,
                estudiante.cedula,
                estudiante.email,
                getattr(estudiante, "carrera", ""),
                getattr(estudiante, "ciclo_actual", ""),
            ]
            for columna, valor in enumerate(valores):
                self.tblEstudiantes.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def abrir_empresas(self):
        from controlador.ControlVentanaCoordinadorEmpresa import ControlVentanaCoordinadorEmpresa
        self._abrir_ventana(ControlVentanaCoordinadorEmpresa(self.usuario, self.ventana_coordinador, self.login))

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
