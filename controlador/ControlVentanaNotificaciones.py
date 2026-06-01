from PyQt6 import QtWidgets

from controlador.ControlNotificacion import ControlNotificacion
from modelo.Notificacion import Notificacion
from modelo.Usuario import Usuario
from utilidades.Excepciones import SistemaPracticasError


class ControlVentanaNotificaciones(QtWidgets.QWidget):
    def __init__(self, usuario: Usuario, ventana_anterior=None):
        super().__init__()
        self.usuario = usuario
        self.ventana_anterior = ventana_anterior
        self.control_notificacion = ControlNotificacion()
        self.notificaciones: list[Notificacion] = []
        self.volviendo = False
        self.setWindowTitle("Notificaciones")
        self.resize(900, 420)
        self.iniciar_interfaz()
        self.iniciar_controlador()

    def iniciar_interfaz(self):
        layout_principal = QtWidgets.QVBoxLayout(self)

        self.lblTitulo = QtWidgets.QLabel("Notificaciones")
        self.lblTitulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout_principal.addWidget(self.lblTitulo)

        self.tblNotificaciones = QtWidgets.QTableWidget(self)
        layout_principal.addWidget(self.tblNotificaciones)

        layout_botones = QtWidgets.QHBoxLayout()
        layout_botones.addStretch()

        self.btnMarcarLeida = QtWidgets.QPushButton("Marcar como leida", self)
        self.btnActualizar = QtWidgets.QPushButton("Actualizar", self)
        self.btnCerrar = QtWidgets.QPushButton("Cerrar", self)
        layout_botones.addWidget(self.btnMarcarLeida)
        layout_botones.addWidget(self.btnActualizar)
        layout_botones.addWidget(self.btnCerrar)

        layout_principal.addLayout(layout_botones)

    def iniciar_controlador(self):
        self.configurar_tabla()
        self.cargar_datos()
        self.btnMarcarLeida.clicked.connect(self.marcar_como_leida)
        self.btnActualizar.clicked.connect(self.cargar_datos)
        self.btnCerrar.clicked.connect(self.volver)

    def configurar_tabla(self):
        columnas = ["ID", "Titulo", "Mensaje", "Tipo", "Fecha", "Estado"]
        self.tblNotificaciones.setColumnCount(len(columnas))
        self.tblNotificaciones.setHorizontalHeaderLabels(columnas)
        self.tblNotificaciones.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tblNotificaciones.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tblNotificaciones.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tblNotificaciones.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tblNotificaciones.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.tblNotificaciones.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)

    def cargar_datos(self):
        self.notificaciones = sorted(
            self.control_notificacion.listar_por_usuario(self.usuario.id_usuario),
            key=lambda notificacion: str(notificacion.fecha_creacion),
            reverse=True,
        )

        self.tblNotificaciones.setRowCount(len(self.notificaciones))
        for fila, notificacion in enumerate(self.notificaciones):
            valores = [
                notificacion.id_notificacion,
                notificacion.titulo,
                notificacion.mensaje,
                notificacion.tipo,
                self._formatear_fecha(notificacion.fecha_creacion),
                "Leida" if notificacion.leida else "Pendiente",
            ]
            for columna, valor in enumerate(valores):
                item = QtWidgets.QTableWidgetItem(str(valor))
                if not notificacion.leida:
                    fuente = item.font()
                    fuente.setBold(True)
                    item.setFont(fuente)
                self.tblNotificaciones.setItem(fila, columna, item)

    def marcar_como_leida(self):
        notificacion = self._notificacion_seleccionada()
        if notificacion is None:
            return

        try:
            self.control_notificacion.marcar_como_leida(notificacion.id_notificacion)
            self.cargar_datos()
            QtWidgets.QMessageBox.information(self, "Notificacion", "La notificacion fue marcada como leida.")
        except SistemaPracticasError as error:
            QtWidgets.QMessageBox.warning(self, "No se pudo actualizar", str(error))

    def volver(self):
        self.volviendo = True
        if self.ventana_anterior is not None:
            if hasattr(self.ventana_anterior, "cargar_datos"):
                self.ventana_anterior.cargar_datos()
            if hasattr(self.ventana_anterior, "cargar_resumen"):
                self.ventana_anterior.cargar_resumen()
            self.ventana_anterior.show()
            self.ventana_anterior.raise_()
            self.ventana_anterior.activateWindow()
        self.close()

    def closeEvent(self, event):
        if self.volviendo:
            super().closeEvent(event)
            return
        if self.ventana_anterior is not None:
            if hasattr(self.ventana_anterior, "cargar_datos"):
                self.ventana_anterior.cargar_datos()
            if hasattr(self.ventana_anterior, "cargar_resumen"):
                self.ventana_anterior.cargar_resumen()
            self.ventana_anterior.show()
            self.ventana_anterior.raise_()
            self.ventana_anterior.activateWindow()
        super().closeEvent(event)

    def _notificacion_seleccionada(self) -> Notificacion | None:
        fila = self.tblNotificaciones.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.information(self, "Seleccion requerida", "Seleccione una notificacion de la tabla.")
            return None
        item = self.tblNotificaciones.item(fila, 0)
        if item is None:
            return None
        return Notificacion.buscar_por_id(item.text())

    def _formatear_fecha(self, fecha):
        if hasattr(fecha, "strftime"):
            return fecha.strftime("%Y-%m-%d %H:%M")
        return fecha
