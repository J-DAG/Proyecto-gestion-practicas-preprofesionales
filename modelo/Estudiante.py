import Usuario

class Estudiante(Usuario):
    def __init__(self,
                 id_usuario,
                 nombre,
                 email,
                 clave,
                 cedula,
                 carrera,
                 ciclo_actual,
                 matriculado = True
                 ):
        super().__init__(id_usuario,nombre,email,clave,tipo_usuario = "estudiante")
        self.cedula = cedula
        self.carrera = carrera
        self.ciclo_actual = ciclo_actual
        self.matriculado = matriculado
        self.practica_previa = False
        self.practica_activa_id = None

    def puede_realizar_practicas(self)->bool:
        return ( self.ciclo_actual >= 6 and
                 self.practica_activa_id is None and
                 self.matriculado)

    def tiene_practica_activa(self)->bool:
        return self.practica_activa_id is not None

    def asignar_practica(self,practica_id: str):
        if self.tiene_practica_activa():
            raise ValueError("El estudiante ya tiene una practica activa")
        self.practica_id = practica_id


