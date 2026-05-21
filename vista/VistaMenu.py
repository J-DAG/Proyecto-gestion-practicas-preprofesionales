class VistaMenu:
    def iniciar(self):
        while True:
            print("=== SISTEMA DE PRÁCTICAS ===")
            print("1. Registrarse")
            print("2. Iniciar sesión")
            print("3. Salir")
            opcion = input("Seleccione una opción: ")
            if opcion == '1':
                print('Registro de usuario')
            elif opcion == '2':
                print('Login')
            elif opcion == '3':
                print("Saliendo...")
                break
            else:
                print("Opción inválida")
