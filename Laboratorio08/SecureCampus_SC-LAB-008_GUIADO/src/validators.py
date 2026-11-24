from decimal import Decimal, InvalidOperation

def validar_calificacion(valor):
    if valor is None or isinstance(valor, bool):
        raise ValueError("Calificación inválida")
    try:
        numero = Decimal(str(valor))
    except InvalidOperation as exc:
        raise ValueError("Calificación inválida") from exc
    if not numero.is_finite() or numero < 0 or numero > 100 or numero.as_tuple().exponent < -2:
        raise ValueError("Calificación inválida")
    return numero
