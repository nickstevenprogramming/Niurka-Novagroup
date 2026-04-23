"""
Servicio de Check-In / Check-Out — lógica de negocio.
"""

from datetime import datetime, date
from app.extensions import db
from app.models.reserva import Reserva
from app.models.checkin import CheckIn, CheckOut
from app.models.habitacion import Habitacion
from app.models.facturacion import Factura, ItemFactura
from app.utils.helpers import generar_codigo


class CheckInService:
    """Servicio para operaciones de check-in."""

    @staticmethod
    def realizar_check_in(reserva_id, staff_id, observaciones=None, num_llaves=1):
        """
        Realiza el check-in de una reserva.

        Validaciones:
        - Reserva debe estar confirmada (estado_id = 2)
        - No debe tener check-in previo

        Acciones:
        - Crea registro de check_in
        - Cambia estado de reserva a 'en_curso' (3)
        - Cambia estado de habitación a 'ocupada'
        """
        reserva = Reserva.query.get(reserva_id)
        if not reserva:
            return None, 'Reserva no encontrada.'

        if reserva.estado_id != 2:
            return None, 'La reserva debe estar confirmada para hacer check-in.'

        if reserva.check_in:
            return None, 'Esta reserva ya tiene un check-in registrado.'

        # Crear check-in
        checkin = CheckIn(
            reserva_id=reserva_id,
            huesped_id=reserva.huesped_id,
            habitacion_id=reserva.habitacion_id,
            staff_id=staff_id,
            fecha_hora=datetime.now(),
            num_llaves=num_llaves,
            observaciones=observaciones
        )
        db.session.add(checkin)

        # Actualizar estado de reserva y habitación
        reserva.estado_id = 3  # en_curso
        habitacion = Habitacion.query.get(reserva.habitacion_id)
        if habitacion:
            habitacion.estado = 'ocupada'

        db.session.commit()
        return checkin, None


class CheckOutService:
    """Servicio para operaciones de check-out."""

    @staticmethod
    def realizar_check_out(reserva_id, staff_id, cargo_extra=0, motivo_cargo=None,
                            satisfaccion=None):
        """
        Realiza el check-out de una reserva.

        Acciones:
        - Crea registro de check_out
        - Cambia estado de reserva a 'completada' (4)
        - Cambia estado de habitación a 'limpieza'
        - Genera factura automática
        """
        reserva = Reserva.query.get(reserva_id)
        if not reserva:
            return None, None, 'Reserva no encontrada.'

        if reserva.estado_id != 3:
            return None, None, 'La reserva debe estar en curso para hacer check-out.'

        # Crear check-out
        checkout = CheckOut(
            reserva_id=reserva_id,
            huesped_id=reserva.huesped_id,
            habitacion_id=reserva.habitacion_id,
            staff_id=staff_id,
            fecha_hora=datetime.now(),
            cargo_extra=cargo_extra or 0,
            motivo_cargo=motivo_cargo,
            satisfaccion=satisfaccion
        )
        db.session.add(checkout)

        # Actualizar estados
        reserva.estado_id = 4  # completada
        habitacion = Habitacion.query.get(reserva.habitacion_id)
        if habitacion:
            habitacion.estado = 'limpieza'
            habitacion.estado_limpieza = 'sucia'

        # Generar factura automática
        factura = CheckOutService._generar_factura(reserva, staff_id, cargo_extra)

        db.session.commit()
        return checkout, factura, None

    @staticmethod
    def _generar_factura(reserva, staff_id, cargo_extra=0):
        """Genera factura al hacer check-out."""
        ultimo = db.session.query(db.func.max(Factura.id)).scalar() or 0
        numero = generar_codigo('FAC', ultimo)

        subtotal = float(reserva.precio_total) + float(cargo_extra or 0)
        impuesto = float(reserva.impuesto_total)
        total = subtotal + impuesto

        factura = Factura(
            numero=numero,
            reserva_id=reserva.id,
            huesped_id=reserva.huesped_id,
            subtotal=subtotal,
            impuesto=impuesto,
            total=total,
            estado='emitida',
            tipo='hospedaje',
            creado_por=staff_id
        )
        db.session.add(factura)
        db.session.flush()

        # Ítem principal: noches de hospedaje
        item = ItemFactura(
            factura_id=factura.id,
            descripcion=f'Hospedaje - {reserva.habitacion.tipo.nombre} ({reserva.noches} noches)',
            cantidad=reserva.noches,
            precio_unit=float(reserva.precio_noche),
            subtotal=float(reserva.precio_total),
            tipo='noche'
        )
        db.session.add(item)

        # Ítem de cargo extra si existe
        if cargo_extra and float(cargo_extra) > 0:
            item_extra = ItemFactura(
                factura_id=factura.id,
                descripcion='Cargo adicional al checkout',
                cantidad=1,
                precio_unit=float(cargo_extra),
                subtotal=float(cargo_extra),
                tipo='otro'
            )
            db.session.add(item_extra)

        return factura
