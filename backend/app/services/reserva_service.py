"""
Servicio de Reservas — lógica de negocio central.
"""

from datetime import date
from app.extensions import db
from app.models.reserva import Reserva
from app.models.habitacion import Habitacion, TipoHabitacion
from app.models.hotel import Hotel
from app.utils.helpers import generar_codigo, calcular_noches


class ReservaService:
    """Servicio centralizado para operaciones de reserva."""

    @staticmethod
    def verificar_disponibilidad(habitacion_id, fecha_entrada, fecha_salida, excluir_reserva_id=None):
        """
        Verifica si una habitación está disponible en el rango de fechas.
        Retorna True si está disponible.
        """
        query = Reserva.query.filter(
            Reserva.habitacion_id == habitacion_id,
            Reserva.estado_id.notin_([5, 6]),  # excluir cancelada y no_show
            Reserva.fecha_entrada < fecha_salida,
            Reserva.fecha_salida > fecha_entrada
        )
        if excluir_reserva_id:
            query = query.filter(Reserva.id != excluir_reserva_id)

        return query.count() == 0

    @staticmethod
    def buscar_disponibles(fecha_entrada, fecha_salida, adultos=1, tipo_id=None):
        """
        Busca habitaciones disponibles en un rango de fechas.
        """
        # IDs de habitaciones ocupadas en ese rango
        ocupadas = db.session.query(Reserva.habitacion_id).filter(
            Reserva.estado_id.notin_([5, 6]),
            Reserva.fecha_entrada < fecha_salida,
            Reserva.fecha_salida > fecha_entrada
        ).subquery()

        query = Habitacion.query.join(TipoHabitacion).filter(
            Habitacion.activa == True,
            Habitacion.estado == 'disponible',
            TipoHabitacion.capacidad_max >= adultos,
            Habitacion.id.notin_(db.session.query(ocupadas))
        )

        if tipo_id:
            query = query.filter(TipoHabitacion.id == tipo_id)

        return query.order_by(TipoHabitacion.precio_base).all()

    @staticmethod
    def crear_reserva(data, staff_id=None):
        """
        Crea una reserva nueva con validaciones completas.

        Args:
            data: dict con datos de la reserva
            staff_id: ID del empleado que crea la reserva

        Returns:
            tuple: (reserva, error_message)
        """
        habitacion = Habitacion.query.get(data['habitacion_id'])
        if not habitacion or not habitacion.activa:
            return None, 'Habitación no encontrada o inactiva.'

        tipo = habitacion.tipo
        total_personas = data['num_adultos'] + data.get('num_ninos', 0)
        if total_personas > tipo.capacidad_max:
            return None, f'Capacidad máxima de la habitación: {tipo.capacidad_max} personas.'

        # Verificar disponibilidad
        if not ReservaService.verificar_disponibilidad(
            data['habitacion_id'], data['fecha_entrada'], data['fecha_salida']
        ):
            return None, 'La habitación no está disponible en esas fechas.'

        # Validar fechas
        noches = calcular_noches(data['fecha_entrada'], data['fecha_salida'])
        if data['fecha_salida'] <= data['fecha_entrada']:
            return None, 'La fecha de salida debe ser posterior a la fecha de entrada.'

        # Obtener impuesto del hotel
        hotel = Hotel.query.first()
        impuesto_pct = float(hotel.impuesto_pct) if hotel else 18.00

        # Calcular precio
        precio_noche = float(tipo.precio_base)
        if data.get('incluye_desayuno'):
            precio_noche += 650.00  # Tarifa desayuno estándar

        precio_total = round(precio_noche * noches, 2)
        impuesto_total = round(precio_total * impuesto_pct / 100, 2)

        # Generar código
        ultimo = db.session.query(db.func.max(Reserva.id)).scalar() or 0
        codigo = generar_codigo('RES', ultimo)

        reserva = Reserva(
            codigo=codigo,
            huesped_id=data['huesped_id'],
            habitacion_id=data['habitacion_id'],
            canal_id=data.get('canal_id', 1),
            tarifa_id=data.get('tarifa_id'),
            estado_id=1,  # pendiente
            fecha_entrada=data['fecha_entrada'],
            fecha_salida=data['fecha_salida'],
            hora_llegada_est=data.get('hora_llegada_est'),
            num_adultos=data['num_adultos'],
            num_ninos=data.get('num_ninos', 0),
            precio_noche=precio_noche,
            precio_total=precio_total,
            impuesto_total=impuesto_total,
            deposito_req=precio_noche,
            incluye_desayuno=data.get('incluye_desayuno', False),
            incluye_almuerzo=data.get('incluye_almuerzo', False),
            incluye_cena=data.get('incluye_cena', False),
            notas_huesped=data.get('notas_huesped'),
            staff_creador_id=staff_id
        )

        # Auto-confirmar si es canal directo o teléfono
        if reserva.canal_id in (1, 2):
            reserva.estado_id = 2  # confirmada

        db.session.add(reserva)
        db.session.commit()

        return reserva, None

    @staticmethod
    def cancelar_reserva(reserva_id, motivo=''):
        """Cancela una reserva (solo si está pendiente o confirmada)."""
        reserva = Reserva.query.get(reserva_id)
        if not reserva:
            return None, 'Reserva no encontrada.'

        if reserva.estado_id not in (1, 2):
            return None, 'Solo se pueden cancelar reservas pendientes o confirmadas.'

        reserva.estado_id = 5  # cancelada
        notas = reserva.notas_internas or ''
        reserva.notas_internas = f'{notas} | CANCELACIÓN: {motivo}'.strip()

        db.session.commit()
        return reserva, None
