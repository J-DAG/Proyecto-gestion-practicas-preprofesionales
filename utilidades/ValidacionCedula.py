from __future__ import annotations


def limpiar_cedula(cedula: str) -> str:
    return "".join(filter(str.isdigit, cedula.strip()))


def es_cedula_ecuatoriana_valida(cedula: str) -> bool:
    digitos = limpiar_cedula(cedula)
    if len(digitos) != 10 or not digitos.isdigit():
        return False

    numeros = list(map(int, digitos))
    provincia = int(digitos[:2])
    tercer_digito = numeros[2]
    if provincia < 1 or provincia > 24 or tercer_digito >= 6:
        return False

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    productos = map(lambda par: par[0] * par[1], zip(numeros[:9], coeficientes))
    suma = sum(map(lambda valor: valor - 9 if valor >= 10 else valor, productos))
    digito_verificador = 0 if suma % 10 == 0 else 10 - (suma % 10)
    return digito_verificador == numeros[9]


def validar_cedula_ecuatoriana(cedula: str) -> str:
    digitos = limpiar_cedula(cedula)
    if not es_cedula_ecuatoriana_valida(digitos):
        raise ValueError("La cedula ingresada no cumple las directrices de Ecuador.")
    return digitos
