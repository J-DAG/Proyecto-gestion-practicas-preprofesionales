from PyQt6 import QtWidgets

from controlador.ControlPostulacion import ControlPostulacion
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Usuario import Coordinador, Usuario
from utilidades.Excepciones import ReglaNegocioError, SistemaPracticasError
from vista.estilos import EstilosClase
from vista.ui_coordinador_postulaciones import Ui_frmPostulaciones


class ControlVentanaCoordinadorPostulacion(QtWidgets.QWidget, Ui_frmPostulaciones):
    def __init__(self, usuario: Coordinador, ventana_coordinador=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_coordinador = ventana_coordinador
        self.login = login
        self.postulaciones = ControlPostulacion()
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
        self.btnPracticas.clicked.connect(self.abrir_practicas)
        self.btnPostulaciones.clicked.connect(self.cargar_datos)
        self.btnBuscar.clicked.connect(self.buscar_postulaciones)
        self.txtBuscar.returnPressed.connect(self.buscar_postulaciones)
        self.txtBuscar.textChanged.connect(self.buscar_postulaciones)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.btnAprobar.clicked.connect(self.aprobar_postulacion)
        self.btnNegar.clicked.connect(self.negar_postulacion)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Estudiante", "Oferta", "Fecha", "Estado", "Documento"]
        self.tblPostulaciones.setColumnCount(len(columnas))
        self.tblPostulaciones.setHorizontalHeaderLabels(columnas)
        self.tblPostulaciones.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblPostulaciones.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblPostulaciones.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblPostulaciones.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblPostulaciones.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        self._llenar_tabla(Postulacion.cargar_todos())

    def buscar_postulaciones(self):
        texto = self.txtBuscar.text().strip().lower()
        postulaciones = Postulacion.cargar_todos()
        if texto:
            postulaciones = [
                postulacion
                for postulacion in postulaciones
                if texto in postulacion.id_postulacion.lower()
                or texto in postulacion.id_estudiante.lower()
                or texto in postulacion.id_oferta.lower()
                or texto in self._nombre_estudiante(postulacion.id_estudiante).lower()
                or texto in self._titulo_oferta(postulacion.id_oferta).lower()
                or texto in postulacion.estado.lower()
            ]
        self._llenar_tabla(postulaciones)

    def _llenar_tabla(self, postulaciones: list[Postulacion]):
        self.tblPostulaciones.setRowCount(len(postulaciones))
        for fila, postulacion in enumerate(postulaciones):
            valores = [
                postulacion.id_postulacion,
                self._nombre_estudiante(postulacion.id_estudiante),
                self._titulo_oferta(postulacion.id_oferta),
                postulacion.fecha_postulacion,
                postulacion.estado,
                "Adjunto" if postulacion.tiene_documento_malla() else "Sin adjunto",
            ]
            for columna, valor in enumerate(valores):
                self.tblPostulaciones.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))

    def _nombre_estudiante(self, id_estudiante: str) -> str:
        estudiante = Usuario.buscar_por_id(id_estudiante)
        return estudiante.nombre if estudiante else id_estudiante

    def _titulo_oferta(self, id_oferta: str) -> str:
        oferta = Oferta.buscar_por_id(id_oferta)
        return oferta.titulo if oferta else id_oferta

    def aprobar_postulacion(self):
        postulacion = self._postulacion_seleccionada()
        if postulacion is None:
            return

        try:
            if postulacion.estado != "pendiente":
                raise ReglaNegocioError("Solo se puede aprobar una postulacion pendiente.")
            from controlador.ControlVentanaRevisarDocumentoPostulacion import ControlVentanaRevisarDocumentoPostulacion

            self.subventana = ControlVentanaRevisarDocumentoPostulacion(postulacion, self.usuario, self)
            self.subventana.show()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo aprobar", str(error))

    def negar_postulacion(self):
        postulacion = self._postulacion_seleccionada()
        if postulacion is None:
            return

        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Negar postulacion",
            f"Se rechazara la postulacion {postulacion.id_postulacion}. Desea continuar?",
        )
        if respuesta != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        try:
            if postulacion.estado == "aceptada":
                raise ReglaNegocioError("No se puede negar una postulacion aceptada.")
            postulacion = self.postulaciones.rechazar_postulacion(postulacion.id_postulacion)
            QtWidgets.QMessageBox.information(
                self,
                "Postulacion negada",
                f"Postulacion {postulacion.id_postulacion} actualizada a estado: {postulacion.estado}.",
            )
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo negar", str(error))

    def _postulacion_seleccionada(self) -> Postulacion | None:
        fila = self.tblPostulaciones.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione una postulacion de la tabla.")
            return None

        item = self.tblPostulaciones.item(fila, 0)
        if item is None:
            return None
        return Postulacion.buscar_por_id(item.text())

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
