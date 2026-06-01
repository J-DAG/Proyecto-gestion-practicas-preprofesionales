from PyQt6 import QtCore, QtWidgets

from controlador.ControlOferta import ControlOferta
from controlador.ControlVentanaCrearEmpresa import ControlVentanaCrearEmpresa
from controlador.ControlVentanaEditarEmpresa import ControlVentanaEditarEmpresa
from modelo.Empresa import Empresa
from modelo.Oferta import Oferta
from modelo.Practica import Practica
from modelo.Usuario import Administrador, TutorEmpresarial, Usuario
from utilidades.Excepciones import ReglaNegocioError, SistemaPracticasError
from utilidades.ManejoDatos import ManejoDatos
from vista.estilos import EstilosClase
from vista.ui_admin_empresa_widget import Ui_formGestionEmpresas


class ControlVentanaAdminEmpresas(QtWidgets.QWidget, Ui_formGestionEmpresas):
    def __init__(self, usuario: Administrador, parent=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_admin = parent
        self.ofertas = ControlOferta()
        self.empresas_tabla: list[Empresa] = []
        self.subventana = None
        self.cerrando_sesion = False
        self.setupUi(self)
        self.iniciar_controlador()

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnInicio.clicked.connect(self.volver_inicio)
        self.btnUsuarios.clicked.connect(self.abrir_usuarios)
        self.btnEmpresa.clicked.connect(self.cargar_datos)
        self.btnBuscar.clicked.connect(self.buscar_empresas)
        self.txtBuscar.returnPressed.connect(self.buscar_empresas)
        self.txtBuscar.textChanged.connect(self.buscar_empresas)
        self.btnNuevoUsuario.clicked.connect(self.crear_empresa)
        self.btnEditar.clicked.connect(self.editar_empresa)
        self.btnEliminar.clicked.connect(self.eliminar_empresa)
        self.btnCerrarSesion.clicked.connect(self.cerrar_sesion)
        self.lblTitulo.setFont(EstilosClase.titulo_usurios())
        self.lblSubTitulo.setFont(EstilosClase.sub_titulo())

    def configurar_tabla(self):
        columnas = ["ID", "Nombre", "RUC", "Email", "Sector", "Ubicacion", "Convenio"]
        self.tblEmpresas.setColumnCount(len(columnas))
        self.tblEmpresas.setHorizontalHeaderLabels(columnas)
        self.tblEmpresas.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblEmpresas.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblEmpresas.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblEmpresas.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblEmpresas.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def cargar_datos(self):
        texto = self.txtBuscar.text().strip()
        if texto:
            self.buscar_empresas()
            return
        self.empresas_tabla = self.ofertas.listar_empresas()
        self._llenar_tabla(self.empresas_tabla)

    def buscar_empresas(self):
        texto = self.txtBuscar.text().strip().lower()
        empresas = self.ofertas.listar_empresas()
        if texto:
            empresas = [
                empresa
                for empresa in empresas
                if texto in empresa.id_empresa.lower()
                or texto in empresa.nombre_empresa.lower()
                or texto in empresa.ruc.lower()
                or texto in empresa.email.lower()
                or texto in empresa.sector.lower()
                or texto in empresa.ubicacion.lower()
                or texto in ("si" if empresa.convenio_vigente else "no")
            ]
        self.empresas_tabla = empresas
        self._llenar_tabla(empresas)

    def crear_empresa(self):
        self._abrir_subventana(ControlVentanaCrearEmpresa(self))

    def editar_empresa(self):
        empresa = self._empresa_seleccionada()
        if empresa is None:
            return
        self._abrir_subventana(ControlVentanaEditarEmpresa(empresa, self))

    def eliminar_empresa(self):
        empresa = self._empresa_seleccionada()
        if empresa is None:
            return

        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Eliminar empresa",
            f"Se eliminara la empresa {empresa.nombre_empresa}. Desea continuar?",
        )
        if respuesta != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        try:
            self._validar_eliminacion(empresa)
            datos = ManejoDatos("empresas").cargar_diccionario("id_empresa")
            datos.pop(empresa.id_empresa, None)
            ManejoDatos("empresas").guardar(datos, "id_empresa")
            QtWidgets.QMessageBox.information(self, "Empresa eliminada", "Empresa eliminada correctamente.")
            self._refrescar_vistas()
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo eliminar", str(error))

    def abrir_usuarios(self):
        from controlador.ControlVentanaAdminUsuarios import ControlVentanaAdminUsuarios

        self.subventana = ControlVentanaAdminUsuarios(self.usuario, self.ventana_admin)
        self.subventana.show()
        self.hide()

    def cerrar_sesion(self):
        self.cerrando_sesion = True
        self.close()
        if self.ventana_admin is not None and hasattr(self.ventana_admin, "salir"):
            self.ventana_admin.salir()

    def volver_inicio(self):
        self._mostrar_ventana_admin()
        self.hide()

    def closeEvent(self, event):
        if self.cerrando_sesion:
            super().closeEvent(event)
            return
        if self.ventana_admin is not None:
            self._mostrar_ventana_admin()
        self.hide()
        event.ignore()

    def _llenar_tabla(self, empresas: list[Empresa]):
        self.tblEmpresas.setRowCount(len(empresas))
        for fila, empresa in enumerate(empresas):
            valores = [
                empresa.id_empresa,
                empresa.nombre_empresa,
                empresa.ruc,
                empresa.email,
                empresa.sector,
                empresa.ubicacion,
                "Si" if empresa.convenio_vigente else "No",
            ]
            for columna, valor in enumerate(valores):
                self.tblEmpresas.setItem(fila, columna, QtWidgets.QTableWidgetItem(str(valor)))
        self.tblEmpresas.resizeColumnsToContents()

    def _empresa_seleccionada(self) -> Empresa | None:
        fila = self.tblEmpresas.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione una empresa de la tabla.")
            return None
        item = self.tblEmpresas.item(fila, 0)
        if item is None:
            return None
        return Empresa.buscar_por_id(item.text())

    def _validar_eliminacion(self, empresa: Empresa):
        if any(oferta.id_empresa == empresa.id_empresa for oferta in Oferta.cargar_todos()):
            raise ReglaNegocioError("No se puede eliminar una empresa con ofertas registradas.")
        if any(practica.id_empresa == empresa.id_empresa for practica in Practica.cargar_todos()):
            raise ReglaNegocioError("No se puede eliminar una empresa con practicas asociadas.")
        if any(
            isinstance(usuario, TutorEmpresarial) and usuario.id_empresa == empresa.id_empresa
            for usuario in Usuario.cargar_todos()
        ):
            raise ReglaNegocioError("No se puede eliminar una empresa con tutores empresariales asociados.")

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
