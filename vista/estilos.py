
from PyQt6.QtGui import QFont

class EstilosClase:
    @staticmethod
    def negrita(tamano=10):
        fuente = QFont("Segoe UI")
        fuente.setPointSize(tamano)
        fuente.setBold(True)
        return fuente

    @staticmethod
    def titulo():
        fuente = QFont("Segoe UI")
        fuente.setPointSize(16)
        fuente.setBold(True)
        return fuente

    @staticmethod
    def sub_titulo():
        fuente = QFont("Segoe UI")
        fuente.setPointSize(18)
        fuente.setBold(True)
        return fuente

    @staticmethod
    def titulo_usurios():
        fuente = QFont("Segoe UI")
        fuente.setPointSize(15)
        fuente.setBold(True)
        return fuente
