from PyQt6 import QtWidgets

from configuracion.ajustes import ROLES
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
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
        self.btnReportes.triggered.connect(self.abrir_reportes)
        self.btnEstudiantes.triggered.connect(self.abrir_estudiantes)
        self.btnTutores.triggered.connect(self.abrir_tutores)
        self.btnEmpresa.triggered.connect(self.abrir_empresas)
        self.actionPracticas.triggered.connect(self.abrir_practicas)
        self.btnPostulacion.triggered.connect(self.abrir_postulaciones)
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
                self._nombre_usuario(postulacion.id_estudiante),
                self._titulo_oferta(postulacion.id_oferta),
                postulacion.fecha_postulacion,
                postulacion.estado,
            ]
            for columna, valor in enumerate(valores):
                self.tblPostulaciones.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def cargar_resumen(self):
        usuarios = Usuario.cargar_todos()
        practicas = Practica.cargar_todos()
        postulaciones = Postulacion.cargar_todos()
        resumen = self._generar_resumen(
            usuarios,
            practicas,
            Empresa.cargar_todos(),
            postulaciones,
        )
        self.lblNumEstudiantes.setText(str(resumen["estudiantes"]))
        self.lblNumTA.setText(str(resumen["tutores_academicos"]))
        self.lblTE.setText(str(resumen["tutores_empresariales"]))
        self.lblNumEmpresas.setText(str(resumen["empresas"]))
        self.lblNumPostulaciones.setText(str(resumen["postulaciones"]))
        self.lblNumPracActiva.setText(str(resumen["practicas_activas"]))

    def _generar_resumen(
        self,
        usuarios: list[Usuario],
        practicas: list[Practica],
        empresas: list[Empresa],
        postulaciones: list[Postulacion],
    ) -> dict[str, int]:
        contar_rol = lambda rol: sum(map(lambda usuario: usuario.rol == rol, usuarios))
        contar_practicas = lambda estado: sum(map(lambda practica: practica.estado == estado, practicas))
        return {
            "estudiantes": contar_rol(ROLES["ESTUDIANTE"]),
            "tutores_academicos": contar_rol(ROLES["TUTOR_ACADEMICO"]),
            "tutores_empresariales": contar_rol(ROLES["TUTOR_EMPRESARIAL"]),
            "empresas": len(empresas),
            "postulaciones": len(postulaciones),
            "practicas_activas": contar_practicas("activa"),
        }

    def _nombre_usuario(self, id_usuario: str) -> str:
        usuario = Usuario.buscar_por_id(id_usuario)
        return usuario.nombre if usuario else id_usuario

    def _titulo_oferta(self, id_oferta: str) -> str:
        oferta = Oferta.buscar_por_id(id_oferta)
        return oferta.titulo if oferta else id_oferta

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
