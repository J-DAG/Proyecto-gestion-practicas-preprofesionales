from PyQt6 import QtCore, QtWidgets

from controlador.ControlPractica import ControlPractica
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.Postulacion import Postulacion
from modelo.Practica import Practica
from modelo.Usuario import Estudiante
from modelo.Usuario import Usuario
from vista.estilos import EstilosClase
from vista.ui_EST_formularios import Ui_FormEST


class ControlVentanaEstudianteFormularios(QtWidgets.QWidget, Ui_FormEST):
    def __init__(self, usuario: Estudiante, ventana_estudiante=None, login=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_estudiante = ventana_estudiante
        self.login = login
        self.practicas = ControlPractica()
        self.cerrando_sesion = False
        self.setupUi(self)
        self._preparar_widgets_formularios()
        self.iniciar_controlador()

    def _preparar_widgets_formularios(self):
        self.txtFormulario1 = QtWidgets.QTextEdit(self.widgetF1)
        self.txtFormulario1.setReadOnly(True)
        self.txtFormulario1.setGeometry(QtCore.QRect(0, 0, self.widgetF1.width(), self.widgetF1.height()))
        self.txtFormulario1.setObjectName("txtFormulario1")

        self.txtFormulario2 = QtWidgets.QTextEdit(self.widgetF2)
        self.txtFormulario2.setReadOnly(True)
        self.txtFormulario2.setGeometry(QtCore.QRect(0, 0, self.widgetF2.width(), self.widgetF2.height()))
        self.txtFormulario2.setObjectName("txtFormulario2")

    def iniciar_controlador(self):
        self.cargar_datos()
        self.btnInico.clicked.connect(self.volver_inicio)
        self.btnMiPractica.clicked.connect(self.ver_progreso)
        self.btnMisPostulaciones.clicked.connect(self.ver_postulaciones)
        self.btnOfertaLaboral.clicked.connect(self.ver_ofertas)
        self.btnMisFormularios.clicked.connect(self.cargar_datos)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())
        self.btnCartaCompromiso.clicked.connect(self.ver_carta_compromiso)

    def cargar_datos(self):
        formularios = self.practicas.listar_formularios_estudiante(self.usuario.id_usuario)
        tipos = {formulario.tipo for formulario in formularios}
        self.lblTitulo_2.setText("Formulario 1: enviado" if "Formulario 1" in tipos else "Formulario 1: pendiente")
        finales = {"Formulario 2", "Formulario 3"} & tipos
        self.lblTitulo_3.setText("Formularios finales: enviados" if finales else "Formularios finales: pendientes")
        self._llenar_formulario_1()
        self._llenar_formulario_2()

    def _llenar_formulario_1(self):
        practica = self.practicas.obtener_practica_visible_estudiante(self.usuario.id_usuario)
        if practica is None:
            self.txtFormulario1.setPlainText("No existe una practica asociada para mostrar el Formulario 1.")
            return

        datos = self._datos_practica(practica)
        self.txtFormulario1.setPlainText(
            "\n".join(
                [
                    "Formulario 1 - Inicio de practica",
                    "",
                    f"Codigo de practica: {practica.id_practica}",
                    f"Nombre de la empresa: {datos['empresa']}",
                    f"Fecha de inicio: {practica.fecha_inicio}",
                    f"Tutor academico: {datos['tutor_academico']}",
                    f"Tutor empresarial: {datos['tutor_empresarial']}",
                    "",
                    "Informacion de postulacion:",
                    f"Codigo de postulacion: {practica.id_postulacion}",
                    f"Titulo de la practica/oferta: {datos['titulo_oferta']}",
                    f"Area: {datos['area_oferta']}",
                ]
            )
        )

    def _llenar_formulario_2(self):
        practica = self.practicas.obtener_practica_visible_estudiante(self.usuario.id_usuario)
        if practica is None:
            self.txtFormulario2.setPlainText("No existe una practica asociada para mostrar el Formulario 2.")
            return
        if practica.estado != "finalizada":
            self.txtFormulario2.setPlainText("El Formulario 2 estara disponible cuando la practica este finalizada.")
            return

        datos = self._datos_practica(practica)
        calificacion = practica.calificacion if practica.calificacion is not None else "Pendiente de calificacion"
        self.txtFormulario2.setPlainText(
            "\n".join(
                [
                    "Formulario 2 - Evaluacion de practica",
                    "",
                    f"Codigo de practica: {practica.id_practica}",
                    f"Nombre de la empresa: {datos['empresa']}",
                    f"Fecha de inicio: {practica.fecha_inicio}",
                    f"Fecha fin: {practica.fecha_fin}",
                    f"Tutor academico: {datos['tutor_academico']}",
                    f"Tutor empresarial: {datos['tutor_empresarial']}",
                    "",
                    "Informacion de postulacion:",
                    f"Codigo de postulacion: {practica.id_postulacion}",
                    f"Titulo de la practica/oferta: {datos['titulo_oferta']}",
                    f"Area: {datos['area_oferta']}",
                    f"Calificacion: {calificacion}",
                ]
            )
        )

    def _datos_practica(self, practica: Practica) -> dict[str, str]:
        empresa = Empresa.buscar_por_id(practica.id_empresa)
        tutor_academico = Usuario.buscar_por_id(practica.id_tutor_academico)
        tutor_empresarial = Usuario.buscar_por_id(practica.tutor_empresarial)
        postulacion = Postulacion.buscar_por_id(practica.id_postulacion)
        oferta = Oferta.buscar_por_id(postulacion.id_oferta) if postulacion is not None else None
        return {
            "empresa": empresa.nombre_empresa if empresa else practica.id_empresa,
            "tutor_academico": tutor_academico.nombre if tutor_academico else practica.id_tutor_academico,
            "tutor_empresarial": tutor_empresarial.nombre if tutor_empresarial else practica.tutor_empresarial,
            "titulo_oferta": oferta.titulo if oferta else "Oferta no encontrada",
            "area_oferta": oferta.area if oferta else "No registrada",
        }

    def ver_progreso(self):
        from controlador.ControlVentanaEstudiantePractica import ControlVentanaEstudiantePractica
        self._abrir_ventana(ControlVentanaEstudiantePractica(self.usuario, self.ventana_estudiante, self.login))

    def ver_postulaciones(self):
        from controlador.ControlVentanaEstudiantePostulaciones import ControlVentanaEstudiantePostulaciones
        self._abrir_ventana(ControlVentanaEstudiantePostulaciones(self.usuario, self.ventana_estudiante, self.login))

    def ver_ofertas(self):
        from controlador.ControlVentanaEstudianteOfertasLaborales import ControlVentanaEstudianteOfertasLaborales
        self._abrir_ventana(ControlVentanaEstudianteOfertasLaborales(self.usuario, self.ventana_estudiante, self.login))

    def ver_carta_compromiso(self):
        documentos = [
            documento
            for documento in self.practicas.listar_documentos_estudiante(self.usuario.id_usuario)
            if documento.tipo == "Carta compromiso"
        ]
        if not documentos:
            QtWidgets.QMessageBox.information(
                self,
                "Carta compromiso",
                "No existe carta compromiso para este estudiante.",
            )
            return

        documento = documentos[-1]
        dialogo = QtWidgets.QDialog(self)
        dialogo.setWindowTitle("Carta compromiso")
        dialogo.resize(700, 500)
        layout = QtWidgets.QVBoxLayout(dialogo)
        texto = QtWidgets.QTextEdit(dialogo)
        texto.setReadOnly(True)
        texto.setPlainText(documento.contenido or "Carta compromiso generada sin contenido adicional.")
        btnCerrar = QtWidgets.QPushButton("Cerrar", dialogo)
        btnCerrar.clicked.connect(dialogo.close)
        layout.addWidget(texto)
        layout.addWidget(btnCerrar)
        dialogo.exec()

    def volver_inicio(self):
        self._mostrar_principal()
        self.hide()

    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()
        if self.ventana_estudiante is not None:
            self.ventana_estudiante.salir()

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
        if self.ventana_estudiante is not None:
            self.ventana_estudiante.cargar_datos()
            self.ventana_estudiante.show()
            self.ventana_estudiante.raise_()
            self.ventana_estudiante.activateWindow()
