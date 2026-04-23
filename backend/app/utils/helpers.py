"""
Funciones auxiliares del sistema.
"""

from datetime import date


def generar_codigo(prefijo, ultimo_id):
    """Genera código secuencial: RES-2025-000001, FAC-2025-0001, etc."""
    year = date.today().year
    return f'{prefijo}-{year}-{str(ultimo_id + 1).zfill(6)}'


def calcular_noches(fecha_entrada, fecha_salida):
    """Calcula el número de noches entre dos fechas."""
    delta = fecha_salida - fecha_entrada
    return max(delta.days, 1)


def calcular_precio_total(precio_noche, noches, impuesto_pct=18.00, descuento=0):
    """Calcula precio total con impuesto y descuento."""
    subtotal = float(precio_noche) * noches
    impuesto = round(subtotal * float(impuesto_pct) / 100, 2)
    total = subtotal + impuesto - float(descuento)
    return {
        'subtotal': round(subtotal, 2),
        'impuesto': impuesto,
        'total': round(total, 2),
        'noches': noches
    }
