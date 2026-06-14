from __future__ import annotations

import faulthandler
import shutil
import sys
from pathlib import Path

from PyQt6 import QtWidgets

from controlador.ControlPrincipal import ControlPrincipal
from modelo.utilidades.seed import sembrar_datos_prueba


CRASH_LOG_HANDLE = None


def main() -> None:
    activar_registro_fallos()
    sembrar_datos_prueba()
    preparar_rutas_recursos()
    app = QtWidgets.QApplication(sys.argv)
    ventana = ControlPrincipal()
    ventana.show()
    sys.exit(app.exec())


def preparar_rutas_recursos() -> None:
    base = Path(__file__).resolve().parent
    for carpeta in ("iconos", "imagenes"):
        destino = base / carpeta
        origen = base / "vista" / carpeta
        if destino.exists() or not origen.exists():
            continue
        try:
            destino.symlink_to(origen, target_is_directory=True)
        except OSError:
            shutil.copytree(origen, destino, dirs_exist_ok=True)


def activar_registro_fallos() -> None:
    global CRASH_LOG_HANDLE
    base = Path(__file__).resolve().parent
    gui_log = base / "gui_debug.log"
    if gui_log.exists():
        gui_log.unlink()
    log = base / "qt_crash.log"
    CRASH_LOG_HANDLE = log.open("w", encoding="utf-8")
    faulthandler.enable(file=CRASH_LOG_HANDLE, all_threads=True)


if __name__ == "__main__":
    main()

