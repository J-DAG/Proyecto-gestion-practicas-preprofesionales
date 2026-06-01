from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox

from configuracion.ajustes import ROLES
from controlador.ControlAdministrador import ControlAdministrador
from controlador.ControlVentanaAdminEmpresas import ControlVentanaAdminEmpresas
from controlador.ControlVentanaAdminUsuarios import ControlVentanaAdminUsuarios
from controlador.ControlOferta import ControlOferta
from controlador.ControlUsuario import ControlUsuario
from modelo.Empresa import Empresa
from modelo.Usuario import Administrador
from vista.estilos import EstilosClase
from vista.ui_main_window_admin import Ui_MainWindowAdmin


class ControlVentanaAdmin(QtWidgets.QMainWindow, Ui_MainWindowAdmin):
    def __init__(self, usuario: Administrador, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.login = parent
        self.ventana_usuarios = None
        self.ventana_empresas = None
        self.setupUi(self)
        self.admin = ControlAdministrador()
        self.ofertas = ControlOferta()
        self.usuarios = ControlUsuario()
        self.iniciar_controlador()
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.cargar_resumen()
        self.btnCerrarSesion_1.clicked.connect(self.salir)
        self.btnCerrarSesion.triggered.connect(self.salir)
        self.btnAdminUsuarios.clicked.connect(self.abrir_usuarios)
        self.btnUsuarios.triggered.connect(self.abrir_usuarios)
        self.btnAdminEmpresas.clicked.connect(self.abrir_empresas)
        self.btnEmpresa.triggered.connect(self.abrir_empresas)
        self.btnAcercaDe.triggered.connect(self.acerca_de)

    def configurar_tabla(self):
        columnas = [
            "ID",
            "Nombres",
            "Apellidos",
            "Cedula",
            "Email",
            "Rol",
            "Estado",
        ]
        self.tblUsuarios.setColumnCount(len(columnas))
        self.tblUsuarios.setHorizontalHeaderLabels(columnas)
        self.tblUsuarios.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblUsuarios.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblUsuarios.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblUsuarios.horizontalHeader().setStretchLastSection(True)
        self.tblUsuarios.resizeColumnsToContents()

    def cargar_datos(self):
        lista_usuarios = self.usuarios.listar_usuarios()
        self.tblUsuarios.setRowCount(len(lista_usuarios))

        for fila, usuario in enumerate(lista_usuarios):
            valores = [
                usuario.id_usuario,
                usuario.nombres,
                usuario.apellidos,
                usuario.cedula,
                usuario.email,
                usuario.rol,
                "Activo" if usuario.activo else "Inactivo",
            ]
            for columna, valor in enumerate(valores):
                item = QtWidgets.QTableWidgetItem(str(valor))
                self.tblUsuarios.setItem(fila, columna, item)

        self.tblUsuarios.resizeColumnsToContents()

    def cargar_resumen(self):
        usuarios = self.usuarios.listar_usuarios()
        conteos = {
            ROLES["ESTUDIANTE"]: 0,
            ROLES["TUTOR_ACADEMICO"]: 0,
            ROLES["TUTOR_EMPRESARIAL"]: 0,
            ROLES["COORDINADOR"]: 0,
            ROLES["ADMINISTRADOR"]: 0,
        }

        for usuario in usuarios:
            if usuario.rol in conteos:
                conteos[usuario.rol] += 1

        self.lblNumEstudiantes.setText(str(conteos[ROLES["ESTUDIANTE"]]))
        self.lblNumTA.setText(str(conteos[ROLES["TUTOR_ACADEMICO"]]))
        self.lblTE.setText(str(conteos[ROLES["TUTOR_EMPRESARIAL"]]))
        self.lblNumCoordinadores.setText(str(conteos[ROLES["COORDINADOR"]]))
        self.lblNumAdministradores.setText(str(conteos[ROLES["ADMINISTRADOR"]]))
        self.lblNumEmpresas.setText(str(len(Empresa.cargar_todos())))

    def abrir_usuarios(self):
        self.ventana_usuarios = ControlVentanaAdminUsuarios(self.usuario, self)
        self.ventana_usuarios.show()
        self.hide()

    def abrir_empresas(self):
        self.ventana_empresas = ControlVentanaAdminEmpresas(self.usuario, self)
        self.ventana_empresas.show()
        self.hide()

    def salir(self):
        self.close()
        if self.login is not None and hasattr(self.login, "volver_a_login"):
            self.login.volver_a_login()

    def acerca_de(self):
        QMessageBox.information(
            self,
            "Acerca de",
            "Sistema de Gestion de practicas, panel de administrador",
        )
