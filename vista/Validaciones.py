from datetime import date


def leer_texto(mensaje: str) -> str:
    return input(mensaje).strip()


def leer_entero(mensaje: str) -> int:
    while True:
        try:
            return int(input(mensaje).strip())
        except ValueError:
            print("Ingrese un numero valido.")


def leer_bool(mensaje: str) -> bool:
    valor = input(f"{mensaje} (s/n): ").strip().lower()
    return valor in {"s", "si", "y", "yes"}


def leer_fecha(mensaje: str) -> date:
    while True:
        valor = input(f"{mensaje} (YYYY-MM-DD): ").strip()
        try:
            return date.fromisoformat(valor)
        except ValueError:
            print("Formato de fecha invalido.")


def pausar() -> None:
    input("\nPresione Enter para continuar...")


def imprimir_tabla(objetos: list[object]) -> None:
    if not objetos:
        print("No hay registros.")
        return

    for objeto in objetos:
        print(objeto)
