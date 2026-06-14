from PyQt6 import QtCore, QtWidgets

from modelo.configuracion.ajustes import ROLES
from controlador.ControlAdministrador import ControlAdministrador
from controlador.ControlUsuario import ControlUsuario
from controlador.ControlVentanaCrearAdministrador import ControlVentanaCrearAdministrador
from controlador.ControlVentanaCrearCoordinador import ControlVentanaCrearCoordinador
from controlador.ControlVentanaCrearEstudiante import ControlVentanaCrearEstudiante
from controlador.ControlVentanaCrearTA import ControlVentanaCrearTA
from controlador.ControlVentanaCrearTE import ControlVentanaCrearTE
from controlador.ControlVentanaEditarAdministrador import ControlVentanaEditarAdministrador
from controlador.ControlVentanaEditarCoordinador import ControlVentanaEditarCoordinador
from controlador.ControlVentanaEditarEstudiante import ControlVentanaEditarEstudiante
from controlador.ControlVentanaEditarTA import ControlVentanaEditarTA
from controlador.ControlVentanaEditarTE import ControlVentanaEditarTE
from modelo.Usuario import Administrador, Coordinador, Estudiante, TutorAcademico, TutorEmpresarial, Usuario
from modelo.utilidades.Excepciones import SistemaPracticasError, ValidacionError
from vista.estilos import EstilosClase
from vista.ui_admin_usuario_widget import Ui_formGestionUsuarios


class ControlVentanaAdminUsuarios(QtWidgets.QWidget, Ui_formGestionUsuarios):
    def __init__(self, usuario: Administrador, parent=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_admin = parent
        self.usuarios = ControlUsuario()
        self.admin = ControlAdministrador()
        self.usuarios_tabla: list[Usuario] = []
        self.subventana = None
        self.cerrando_sesion = False
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnInicio.clicked.connect(self.volver_inicio)
        self.btnEmpresa.clicked.connect(self.abrir_empresas)
        self.btnBuscar.clicked.connect(self.buscar_usuarios)
        self.txtBuscar.returnPressed.connect(self.buscar_usuarios)
        self.txtBuscar.textChanged.connect(self.buscar_usuarios)
        self.btnNuevoUsuario.clicked.connect(self.crear_usuario)
        self.btnEditar.clicked.connect(self.editar_usuario)
        self.btnEliminar.clicked.connect(self.eliminar_usuario)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

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
        texto = self.txtBuscar.text().strip()
        if texto:
            self.buscar_usuarios()
            return
        self.usuarios_tabla = self.usuarios.listar_usuarios()
        self._llenar_tabla(self.usuarios_tabla)

    def buscar_usuarios(self):
        texto = self.txtBuscar.text().strip().lower()
        usuarios = self.usuarios.listar_usuarios()
        if texto:
            usuarios = [
                usuario
                for usuario in usuarios
                if texto in usuario.id_usuario.lower()
                or texto in usuario.nombres.lower()
                or texto in usuario.apellidos.lower()
                or texto in usuario.cedula.lower()
                or texto in usuario.email.lower()
                or texto in usuario.rol.lower()
                or texto in ("activo" if usuario.activo else "inactivo")
            ]
        self.usuarios_tabla = usuarios
        self._llenar_tabla(usuarios)

    def crear_usuario(self):
        opciones = {
            "Estudiante": ControlVentanaCrearEstudiante,
            "Coordinador": ControlVentanaCrearCoordinador,
            "Tutor academico": ControlVentanaCrearTA,
            "Tutor empresarial": ControlVentanaCrearTE,
            "Administrador": ControlVentanaCrearAdministrador,
        }
        etiqueta, aceptado = QtWidgets.QInputDialog.getItem(
            self,
            "Tipo de usuario",
            "Seleccione el tipo de usuario a registrar:",
            list(opciones.keys()),
            0,
            False,
        )
        if not aceptado:
            return
        self._abrir_subventana(opciones[etiqueta](self))

    def editar_usuario(self):
        usuario = self._usuario_seleccionado()
        if usuario is None:
            return

        if isinstance(usuario, Estudiante):
            subventana = ControlVentanaEditarEstudiante(usuario, self)
        elif isinstance(usuario, TutorAcademico):
            subventana = ControlVentanaEditarTA(usuario, self)
        elif isinstance(usuario, TutorEmpresarial):
            subventana = ControlVentanaEditarTE(usuario, self)
        elif isinstance(usuario, Administrador):
            subventana = ControlVentanaEditarAdministrador(usuario, self)
        elif isinstance(usuario, Coordinador):
            subventana = ControlVentanaEditarCoordinador(usuario, self)
        else:
            QtWidgets.QMessageBox.warning(self, "Rol no soportado", "El rol asignado no cioncide con las credenciales del sistema.")
            return
        self._abrir_subventana(subventana)

    def eliminar_usuario(self):
        usuario = self._usuario_seleccionado()
        if usuario is None:
            return

        if usuario.id_usuario == self.usuario.id_usuario:
            QtWidgets.QMessageBox.warning(
                self,
                "Accion no permitida",
                "No puede eliminar su propia cuenta desde la sesion actual.",
            )
            return

        detalle = (
            "Se eliminaran sus postulaciones, practicas, actividades, "
            "formularios, documentos y solicitudes asociadas."
            if usuario.rol == ROLES["ESTUDIANTE"]
            else (
                "Solo se permitira si no deja referencias sueltas. "
                "Para tutores con practicas o actividades se pedira un reemplazo."
            )
        )
        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Eliminar usuario",
            f"Se eliminara permanentemente la cuenta de {usuario.nombre}.\n\n{detalle}\n\nDesea continuar?",
        )
        if respuesta != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        try:
            id_reemplazo = self._pedir_tutor_reemplazo_para_eliminar_si_aplica(usuario)
            self.admin.eliminar_usuario(usuario.id_usuario, id_reemplazo)
            QtWidgets.QMessageBox.information(self, "Usuario eliminado", "Usuario eliminado correctamente.")
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo eliminar", str(error))

    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()
        if self.ventana_admin is not None and hasattr(self.ventana_admin, "salir"):
            self.ventana_admin.salir()

    def volver_inicio(self):
        self._mostrar_ventana_admin()
        self.hide()

    def abrir_empresas(self):
        from controlador.ControlVentanaAdminEmpresas import ControlVentanaAdminEmpresas

        self.subventana = ControlVentanaAdminEmpresas(self.usuario, self.ventana_admin)
        self.subventana.show()
        self.hide()

    def closeEvent(self, event):
        if self.cerrando_sesion:
            super().closeEvent(event)
            return
        if self.ventana_admin is not None:
            self._mostrar_ventana_admin()
        self.hide()
        event.ignore()

    def _llenar_tabla(self, usuarios: list[Usuario]):
        self.tblUsuarios.setRowCount(len(usuarios))
        for fila, usuario in enumerate(usuarios):
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
                self.tblUsuarios.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))
        self.tblUsuarios.resizeColumnsToContents()

    def _usuario_seleccionado(self) -> Usuario | None:
        fila = self.tblUsuarios.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione un usuario de la tabla.")
            return None
        item = self.tblUsuarios.item(fila, 0)
        if item is None:
            return None
        return self.usuarios.buscar_usuario(item.text())

    def _pedir_tutor_reemplazo_si_aplica(self, usuario: Usuario) -> str | None:
        practicas = self.admin.listar_practicas_activas_asignadas(usuario.id_usuario)
        if not practicas:
            return None

        tutores = [
            tutor
            for tutor in self.usuarios.listar_usuarios()
            if tutor.rol == usuario.rol and tutor.activo and tutor.id_usuario != usuario.id_usuario
        ]
        if not tutores:
            raise ValidacionError("No hay tutores activos disponibles para reemplazo.")

        opciones = [f"{tutor.id_usuario} - {tutor.nombre}" for tutor in tutores]
        opcion, aceptado = QtWidgets.QInputDialog.getItem(
            self,
            "Tutor reemplazo",
            "Seleccione el tutor que recibira las practicas activas:",
            opciones,
            0,
            False,
        )
        if not aceptado:
            raise ValidacionError("Debe seleccionar un tutor reemplazo.")
        return opcion.split(" - ", 1)[0]

    def _pedir_tutor_reemplazo_para_eliminar_si_aplica(self, usuario: Usuario) -> str | None:
        if usuario.rol not in {ROLES["TUTOR_ACADEMICO"], ROLES["TUTOR_EMPRESARIAL"]}:
            return None
        if not self.admin.tutor_requiere_reemplazo_para_eliminar(usuario.id_usuario):
            return None

        tutores = [
            tutor
            for tutor in self.usuarios.listar_usuarios()
            if tutor.rol == usuario.rol and tutor.activo and tutor.id_usuario != usuario.id_usuario
        ]
        if not tutores:
            raise ValidacionError("No hay tutores activos disponibles para reemplazo.")

        opciones = [f"{tutor.id_usuario} - {tutor.nombre}" for tutor in tutores]
        opcion, aceptado = QtWidgets.QInputDialog.getItem(
            self,
            "Tutor reemplazo",
            "Seleccione el tutor que recibira las practicas y actividades asociadas:",
            opciones,
            0,
            False,
        )
        if not aceptado:
            raise ValidacionError("Debe seleccionar un tutor reemplazo.")
        return opcion.split(" - ", 1)[0]

    def _abrir_subventana(self, subventana: QtWidgets.QWidget):
        self.subventana = subventana
        self.subventana.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.subventana.destroyed.connect(self._volver_desde_subventana)
        self.subventana.show()
        self.hide()

    def _volver_desde_subventana(self):
        self.subventana = None
        self._refrescar_vistas()
        self.show()

    def _refrescar_vistas(self):
        self.cargar_datos()
        if self.ventana_admin is not None:
            if hasattr(self.ventana_admin, "cargar_datos"):
                self.ventana_admin.cargar_datos()
            if hasattr(self.ventana_admin, "cargar_resumen"):
                self.ventana_admin.cargar_resumen()

    def _mostrar_ventana_admin(self):
        if self.ventana_admin is None:
            return
        if hasattr(self.ventana_admin, "cargar_datos"):
            self.ventana_admin.cargar_datos()
        if hasattr(self.ventana_admin, "cargar_resumen"):
            self.ventana_admin.cargar_resumen()
        self.ventana_admin.show()
        self.ventana_admin.raise_()
        self.ventana_admin.activateWindow()

