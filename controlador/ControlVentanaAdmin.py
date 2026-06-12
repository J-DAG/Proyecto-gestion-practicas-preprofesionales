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
        self.btnUsuarios.triggered.connect(self.abrir_usuarios)
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
        self.tblUsuarios.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblUsuarios.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

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

    def cargar_resumen(self):
        usuarios = self.usuarios.listar_usuarios()
        resumen = self._generar_resumen(usuarios, Empresa.cargar_todos())
        self.lblNumEstudiantes.setText(str(resumen["estudiantes"]))
        self.lblNumTA.setText(str(resumen["tutores_academicos"]))
        self.lblTE.setText(str(resumen["tutores_empresariales"]))
        self.lblNumCoordinadores.setText(str(resumen["coordinadores"]))
        self.lblNumAdministradores.setText(str(resumen["administradores"]))
        self.lblNumEmpresas.setText(str(resumen["empresas"]))

    def _generar_resumen(self, usuarios: list[object], empresas: list[object]) -> dict[str, int]:
        contar_rol = lambda rol: sum(map(lambda usuario: usuario.rol == rol, usuarios))
        return {
            "estudiantes": contar_rol(ROLES["ESTUDIANTE"]),
            "tutores_academicos": contar_rol(ROLES["TUTOR_ACADEMICO"]),
            "tutores_empresariales": contar_rol(ROLES["TUTOR_EMPRESARIAL"]),
            "coordinadores": contar_rol(ROLES["COORDINADOR"]),
            "administradores": contar_rol(ROLES["ADMINISTRADOR"]),
            "empresas": len(empresas),
        }

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
