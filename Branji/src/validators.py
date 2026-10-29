from decimal import Decimal, InvalidOperation

def validar_calificacion(valor):
    # 1. Rechazar nulos y booleanos (en Python bool es subclase de int, por lo que True/False pasan isinstance numérico si no se filtran)
    if valor is None or isinstance(valor, bool):
        raise ValueError("Calificación inválida: valor nulo o booleano.")

    # 2. Intentar convertir a Decimal (maneja texto no numérico, cadenas vacías, etc.)
    try:
        # Si es un string, quitamos espacios en blanco al inicio/final
        val_str = str(valor).strip()
        if not val_str:
            raise ValueError("Calificación vacía.")
            
        d = Decimal(val_str)
    except (InvalidOperation, TypeError):
        raise ValueError("Calificación inválida: texto no numérico.")

    # 3. Rechazar NaN e Infinity
    if d.is_nan() or d.is_infinite():
        raise ValueError("Calificación inválida: valor no finito (NaN o Infinity).")

    # 4. Verificar rango [0, 100]
    if d < Decimal('0') or d > Decimal('100'):
        raise ValueError("Calificación fuera de rango (debe estar entre 0 y 100).")

    # 5. Verificar que no tenga más de 2 decimales (sin redondear silenciosamente)
    # as_tuple().exponent nos indica el número de decimales (si es negativo)
    if d.as_tuple().exponent < -2:
        raise ValueError("Calificación inválida: más de 2 decimales.")

    return d