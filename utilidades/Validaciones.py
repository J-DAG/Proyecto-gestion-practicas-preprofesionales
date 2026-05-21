class Validaciones:
    @staticmethod
    def validar_email(email)->bool:
        return '@' in email and '.' in email

    @staticmethod
    def validar_cedula(cedula)->bool:
        return cedula.isdigit() and len(cedula) == 10

    @staticmethod
    def validar_ciclo(ciclo: int)-> bool:
        return ciclo >= 1
