from decimal import Decimal

def validar_calificacion(valor):
    # TODO: rechazar valores nulos, booleanos, texto no numérico, NaN, Infinity, fuera de 0..100 y >2 decimales.
    # No redondear entradas incorrectas.
    return Decimal(str(valor))
