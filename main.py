from utilidades.seed import sembrar_datos_prueba
from vista.main_menu import MainMenu


def main() -> None:
    sembrar_datos_prueba()
    MainMenu().iniciar()


if __name__ == "__main__":
    main()
