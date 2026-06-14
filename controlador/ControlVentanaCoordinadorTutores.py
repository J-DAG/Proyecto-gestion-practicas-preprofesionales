from PyQt6 import QtCore, QtWidgets

from modelo.configuracion.ajustes import ROLES
from controlador.ControlAdministrador import ControlAdministrador
from controlador.ControlUsuario import ControlUsuario
from controlador.ControlVentanaCrearTA import ControlVentanaCrearTA
from controlador.ControlVentanaCrearTE import ControlVentanaCrearTE
from controlador.ControlVentanaEditarTA import ControlVentanaEditarTA
from controlador.ControlVentanaEditarTE import ControlVentanaEditarTE
from modelo.Usuario import Coordinador, TutorAcademico, TutorEmpresarial, Usuario
from modelo.utilidades.Excepciones import SistemaPracticasError, ValidacionError
from vista.estilos import EstilosClase
from vista.ui_coordinador_tutores import Ui_frmTutores


class ControlVentanaCoordinadorTutores(QtWidgets.QWidget, Ui_frmTutores):
    def __init__(self, usuario: Coordinador, ventana_coordinador=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_coordinador = ventana_coordinador
        self.login = login
        self.admin = ControlAdministrador()
        self.usuarios = ControlUsuario()
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
        self.btnTutores.clicked.connect(self.cargar_datos)
        self.btnOfertas.clicked.connect(self.abrir_ofertas)
        self.btnEmpresa.clicked.connect(self.abrir_empresas)
        self.btnPracticas.clicked.connect(self.abrir_practicas)
        self.btnPostulaciones.clicked.connect(self.abrir_postulaciones)
        self.btnBuscar.clicked.connect(self.buscar_tutores)
        self.txtBuscar.returnPressed.connect(self.buscar_tutores)
        self.txtBuscar.textChanged.connect(self.buscar_tutores)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnEliminar.clicked.connect(self.eliminar_Tutor)
        self.btnEditar.clicked.connect(self.editar_tutor)
        self.btnNuevoTA.clicked.connect(self.nuevo_TA)
        self.btnNuevoTE.clicked.connect(self.nuevo_TE)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Nombres", "Apellidos", "Cedula", "Email", "Rol", "Detalle"]
        self.tblTutores.setColumnCount(len(columnas))
        self.tblTutores.setHorizontalHeaderLabels(columnas)
        self.tblTutores.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblTutores.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblTutores.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblTutores.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblTutores.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        self._llenar_tabla(self._tutores())

    def buscar_tutores(self):
        texto = self.txtBuscar.text().strip().lower()
        tutores = self._tutores()
        if texto:
            tutores = [
                tutor
                for tutor in tutores
                if texto in tutor.id_usuario.lower()
                or texto in tutor.nombres.lower()
                or texto in tutor.apellidos.lower()
                or texto in tutor.cedula.lower()
                or texto in tutor.email.lower()
                or texto in tutor.rol.lower()
                or texto in str(getattr(tutor, "carrera", getattr(tutor, "id_empresa", ""))).lower()
            ]
        self._llenar_tabla(tutores)

    def _tutores(self):
        return [
            usuario
            for usuario in Usuario.cargar_todos()
            if usuario.rol in {ROLES["TUTOR_ACADEMICO"], ROLES["TUTOR_EMPRESARIAL"]}
        ]

    def _llenar_tabla(self, tutores: list[Usuario]):
        self.tblTutores.setRowCount(len(tutores))
        for fila, tutor in enumerate(tutores):
            detalle = getattr(tutor, "carrera", "") or getattr(tutor, "id_empresa", "")
            valores = [
                tutor.id_usuario,
                tutor.nombres,
                tutor.apellidos,
                tutor.cedula,
                tutor.email,
                tutor.rol,
                detalle,
            ]
            for columna, valor in enumerate(valores):
                self.tblTutores.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def nuevo_TA(self):
        self._abrir_formulario(ControlVentanaCrearTA(self))

    def nuevo_TE(self):
        self._abrir_formulario(ControlVentanaCrearTE(self))

    def editar_tutor(self):
        tutor = self._tutor_seleccionado()
        if tutor is None:
            return

        if isinstance(tutor, TutorAcademico) or tutor.rol == ROLES["TUTOR_ACADEMICO"]:
            self._abrir_formulario(ControlVentanaEditarTA(tutor, self))
        elif isinstance(tutor, TutorEmpresarial) or tutor.rol == ROLES["TUTOR_EMPRESARIAL"]:
            self._abrir_formulario(ControlVentanaEditarTE(tutor, self))
        else:
            QtWidgets.QMessageBox.warning(self, "Rol no soportado", "Seleccione un tutor academico o empresarial.")

    def eliminar_Tutor(self):
        tutor = self._tutor_seleccionado()
        if tutor is None:
            return

        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Eliminar tutor",
            (
                f"Se eliminara permanentemente la cuenta de {tutor.nombre}.\n\n"
                "Solo se permitira si no tiene practicas o actividades historicas "
                "asociadas. Desea continuar?"
            ),
        )
        if respuesta != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        try:
            id_reemplazo = self._pedir_tutor_reemplazo_para_eliminar_si_aplica(tutor)
            self.admin.eliminar_usuario(tutor.id_usuario, id_reemplazo)
            QtWidgets.QMessageBox.information(self, "Tutor eliminado", "Tutor eliminado correctamente.")
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo eliminar", str(error))

    def _tutor_seleccionado(self) -> Usuario | None:
        fila = self.tblTutores.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione un tutor de la tabla.")
            return None

        item = self.tblTutores.item(fila, 0)
        if item is None:
            return None
        return self.usuarios.buscar_usuario(item.text())

    def _pedir_tutor_reemplazo_si_aplica(self, tutor: Usuario) -> str | None:
        practicas = self.admin.listar_practicas_activas_asignadas(tutor.id_usuario)
        if not practicas:
            return None

        tutores = [
            usuario
            for usuario in self.usuarios.listar_usuarios()
            if usuario.rol == tutor.rol and usuario.activo and usuario.id_usuario != tutor.id_usuario
        ]
        if not tutores:
            raise ValidacionError("No hay tutores activos disponibles para reemplazo.")

        opciones = [f"{usuario.id_usuario} - {usuario.nombre}" for usuario in tutores]
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

    def _pedir_tutor_reemplazo_para_eliminar_si_aplica(self, tutor: Usuario) -> str | None:
        if not self.admin.tutor_requiere_reemplazo_para_eliminar(tutor.id_usuario):
            return None

        tutores = [
            usuario
            for usuario in self.usuarios.listar_usuarios()
            if usuario.rol == tutor.rol and usuario.activo and usuario.id_usuario != tutor.id_usuario
        ]
        if not tutores:
            raise ValidacionError("No hay tutores activos disponibles para reemplazo.")

        opciones = [f"{usuario.id_usuario} - {usuario.nombre}" for usuario in tutores]
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

    def abrir_practicas(self):
        from controlador.ControlVentanaCoordinadorPractica import ControlVentanaCoordinadorPractica
        self._abrir_ventana(ControlVentanaCoordinadorPractica(self.usuario, self.ventana_coordinador, self.login))

    def abrir_reportes(self):
        from controlador.ControlVentanaCoordinadorReportes import ControlVentanaCoordinadorReportes
        self._abrir_ventana(ControlVentanaCoordinadorReportes(self.usuario, self.ventana_coordinador, self.login))

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

