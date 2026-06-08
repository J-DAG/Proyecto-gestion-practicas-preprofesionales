from PyQt6 import QtWidgets

from configuracion.ajustes import ROLES
from modelo.Empresa import Empresa
from modelo.Postulacion import Postulacion
from modelo.Practica import Practica
from modelo.Usuario import Coordinador, Usuario
from vista.estilos import EstilosClase
from vista.ui_main_window_coordinadador import Ui_MainWindowCoordinador


class ControlVentanaCoordinador(QtWidgets.QMainWindow, Ui_MainWindowCoordinador):
    def __init__(self, usuario: Coordinador, login=None, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.login = login
        self.ventana_empresas = None
        self.ventana_estudiantes = None
        self.ventana_ofertas = None
        self.ventana_postulaciones = None
        self.ventana_practicas = None
        self.ventana_reportes = None
        self.ventana_tutores = None
        self.ventana_notificaciones = None
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.cargar_resumen()
        self.btnCerrarSesion_2.clicked.connect(self.salir)
        self.btnCerrarSesion.triggered.connect(self.salir)
        self.btnInformacioReportes.clicked.connect(self.abrir_reportes)
        self.btnReportes.triggered.connect(self.abrir_reportes)
        self.btnAdministracionEstudiantes.clicked.connect(self.abrir_estudiantes)
        self.btnEstudiantes.triggered.connect(self.abrir_estudiantes)
        self.btnAdminTutores.clicked.connect(self.abrir_tutores)
        self.btnTutores.triggered.connect(self.abrir_tutores)
        self.btnAdminEmpresas.clicked.connect(self.abrir_empresas)
        self.btnEmpresa.triggered.connect(self.abrir_empresas)
        self.btnAdminPracticas.clicked.connect(self.abrir_practicas)
        self.actionPracticas.triggered.connect(self.abrir_practicas)
        self.btnAdminPostulaciones.clicked.connect(self.abrir_postulaciones)
        self.btnPostulacion.triggered.connect(self.abrir_postulaciones)
        self.btnAdminOfertas.clicked.connect(self.abrir_ofertas)
        self.btnCrearOferta.triggered.connect(self.abrir_ofertas)
        self.btnNotificaciones.triggered.connect(self.ver_notificaciones)
        self.btnVerNotificaciones.clicked.connect(self.ver_notificaciones)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Estudiante", "Oferta", "Fecha", "Estado"]
        self.tblPostulaciones.setColumnCount(len(columnas))
        self.tblPostulaciones.setHorizontalHeaderLabels(columnas)
        self.tblPostulaciones.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblPostulaciones.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblPostulaciones.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblPostulaciones.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblPostulaciones.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        postulaciones = Postulacion.cargar_todos()
        self.tblPostulaciones.setRowCount(len(postulaciones))
        for fila, postulacion in enumerate(postulaciones):
            valores = [
                postulacion.id_postulacion,
                postulacion.id_estudiante,
                postulacion.id_oferta,
                postulacion.fecha_postulacion,
                postulacion.estado,
            ]
            for columna, valor in enumerate(valores):
                self.tblPostulaciones.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def cargar_resumen(self):
        usuarios = Usuario.cargar_todos()
        practicas = Practica.cargar_todos()
        self.lblNumEstudiantes.setText(str(len([u for u in usuarios if u.rol == ROLES["ESTUDIANTE"]])))
        self.lblNumTA.setText(str(len([u for u in usuarios if u.rol == ROLES["TUTOR_ACADEMICO"]])))
        self.lblNumEmpresas.setText(str(len(Empresa.cargar_todos())))
        self.lblNumPostulaciones.setText(str(len(Postulacion.cargar_todos())))
        self.lblNumPracActiva.setText(str(len([p for p in practicas if p.estado == "activa"])))

    def abrir_empresas(self):
        from controlador.ControlVentanaCoordinadorEmpresa import ControlVentanaCoordinadorEmpresa

        self.ventana_empresas = ControlVentanaCoordinadorEmpresa(self.usuario, self, self.login)
        self.ventana_empresas.show()
        self.hide()

    def abrir_estudiantes(self):
        from controlador.ControlVentanaCoordinadorEstudiantes import ControlVentanaCoordinadorEstudiantes

        self.ventana_estudiantes = ControlVentanaCoordinadorEstudiantes(self.usuario, self, self.login)
        self.ventana_estudiantes.show()
        self.hide()

    def abrir_ofertas(self):
        from controlador.ControlVentanaCoordinadorOferta import ControlVentanaCoordinadorOferta

        self.ventana_ofertas = ControlVentanaCoordinadorOferta(self.usuario, self, self.login)
        self.ventana_ofertas.show()
        self.hide()

    def abrir_postulaciones(self):
        from controlador.ControlVentanaCoordinadorPostulacion import ControlVentanaCoordinadorPostulacion

        self.ventana_postulaciones = ControlVentanaCoordinadorPostulacion(self.usuario, self, self.login)
        self.ventana_postulaciones.show()
        self.hide()

    def abrir_practicas(self):
        from controlador.ControlVentanaCoordinadorPractica import ControlVentanaCoordinadorPractica

        self.ventana_practicas = ControlVentanaCoordinadorPractica(self.usuario, self, self.login)
        self.ventana_practicas.show()
        self.hide()

    def abrir_reportes(self):
        from controlador.ControlVentanaCoordinadorReportes import ControlVentanaCoordinadorReportes

        self.ventana_reportes = ControlVentanaCoordinadorReportes(self.usuario, self, self.login)
        self.ventana_reportes.show()
        self.hide()

    def abrir_tutores(self):
        from controlador.ControlVentanaCoordinadorTutores import ControlVentanaCoordinadorTutores

        self.ventana_tutores = ControlVentanaCoordinadorTutores(self.usuario, self, self.login)
        self.ventana_tutores.show()
        self.hide()

    def ver_notificaciones(self):
        from controlador.ControlVentanaNotificaciones import ControlVentanaNotificaciones

        self.ventana_notificaciones = ControlVentanaNotificaciones(self.usuario, self)
        self.ventana_notificaciones.show()
        self.hide()

    def ver_notificaiones(self):
        self.ver_notificaciones()

    def salir(self):
        self.close()
        if self.login is not None:
            self.login.volver_a_login()
