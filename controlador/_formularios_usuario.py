from PyQt6 import QtWidgets

from modelo.Empresa import Empresa
from modelo.utilidades.Excepciones import ValidacionError
from modelo.utilidades.ManejoDatos import ManejoDatos
from modelo.utilidades.ValidacionCedula import validar_cedula_ecuatoriana


CARRERAS = [
    "Computacion",
    "Electricidad",
    "Ingenieria Civil",
    "Telecomunicaciones",
]


def llenar_combo_carreras(combo: QtWidgets.QComboBox) -> None:
    combo.clear()
    combo.addItems(CARRERAS)


def llenar_combo_ciclos(combo: QtWidgets.QComboBox) -> None:
    combo.clear()
    for ciclo in range(1, 11):
        combo.addItem(str(ciclo), ciclo)


def llenar_combo_empresas(combo: QtWidgets.QComboBox) -> None:
    combo.clear()
    for empresa in Empresa.cargar_todos():
        combo.addItem(f"{empresa.id_empresa} - {empresa.nombre_empresa}", empresa.id_empresa)


def seleccionar_combo_por_texto(combo: QtWidgets.QComboBox, texto: str) -> None:
    indice = combo.findText(texto)
    if indice >= 0:
        combo.setCurrentIndex(indice)


def seleccionar_combo_por_dato(combo: QtWidgets.QComboBox, dato: object) -> None:
    indice = combo.findData(dato)
    if indice >= 0:
        combo.setCurrentIndex(indice)


def valor_combo(combo: QtWidgets.QComboBox) -> object:
    dato = combo.currentData()
    return dato if dato is not None else combo.currentText()


def validar_basicos(nombres: str, apellidos: str, cedula: str, email: str) -> None:
    if not nombres.strip():
        raise ValidacionError("Los nombres son obligatorios.")
    if not apellidos.strip():
        raise ValidacionError("Los apellidos son obligatorios.")
    try:
        validar_cedula_ecuatoriana(cedula)
    except ValueError as error:
        raise ValidacionError(str(error)) from error
    if "@" not in email:
        raise ValidacionError("El email ingresado no tiene un formato valido.")


def validar_password(password: str, confirmar: str, requerido: bool) -> None:
    if requerido and not password.strip():
        raise ValidacionError("La contraseÃ±a es obligatoria.")
    if password or confirmar:
        if password != confirmar:
            raise ValidacionError("Las contraseÃ±as no coinciden.")


def validar_unicos_edicion(id_usuario: str, email: str, cedula: str) -> str:
    try:
        cedula = validar_cedula_ecuatoriana(cedula)
    except ValueError as error:
        raise ValidacionError(str(error)) from error

    usuario_email = ManejoDatos("usuarios").buscar_por_campo("email", email)
    if usuario_email is not None and usuario_email.id_usuario != id_usuario:
        raise ValidacionError(f"Ya existe un usuario con email {email}.")

    usuario_cedula = ManejoDatos("usuarios").buscar_por_campo("cedula", cedula)
    if usuario_cedula is not None and usuario_cedula.id_usuario != id_usuario:
        raise ValidacionError(f"Ya existe un usuario con cedula {cedula}.")
    return cedula


def refrescar_padre(parent: object) -> None:
    if parent is None:
        return
    if hasattr(parent, "_refrescar_vistas"):
        parent._refrescar_vistas()
    elif hasattr(parent, "cargar_datos"):
        parent.cargar_datos()

