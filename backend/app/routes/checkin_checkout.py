"""
Rutas de Check-In / Check-Out.
"""

from datetime import date
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt
from app.models.reserva import Reserva
from app.services.checkin_service import CheckInService, CheckOutService
from app.utils.decorators import role_required
from app.utils.pagination import success_response, error_response
from app.schemas.reserva_schema import reserva_list_schema

ns = Namespace('operaciones', description='Check-in y check-out')


@ns.route('/check-in')
class CheckInEndpoint(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self):
        """Realizar check-in de una reserva."""
        data = request.json
        reserva_id = data.get('reserva_id')
        claims = get_jwt()
        staff_id = claims.get('empleado_id')

        if not reserva_id:
            return error_response('Se requiere reserva_id.', 400)

        checkin, error = CheckInService.realizar_check_in(
            reserva_id=reserva_id,
            staff_id=staff_id,
            observaciones=data.get('observaciones'),
            num_llaves=data.get('num_llaves', 1)
        )

        if error:
            return error_response(error, 400)

        return success_response({
            'check_in_id': checkin.id,
            'reserva_id': checkin.reserva_id,
            'habitacion': checkin.habitacion.numero,
            'fecha_hora': checkin.fecha_hora.isoformat(),
        }, 'Check-in realizado exitosamente.')


@ns.route('/check-out')
class CheckOutEndpoint(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self):
        """Realizar check-out de una reserva (genera factura automática)."""
        data = request.json
        reserva_id = data.get('reserva_id')
        claims = get_jwt()
        staff_id = claims.get('empleado_id')

        if not reserva_id:
            return error_response('Se requiere reserva_id.', 400)

        checkout, factura, error = CheckOutService.realizar_check_out(
            reserva_id=reserva_id,
            staff_id=staff_id,
            cargo_extra=data.get('cargo_extra', 0),
            motivo_cargo=data.get('motivo_cargo'),
            satisfaccion=data.get('satisfaccion')
        )

        if error:
            return error_response(error, 400)

        return success_response({
            'check_out_id': checkout.id,
            'reserva_id': checkout.reserva_id,
            'habitacion': checkout.habitacion.numero,
            'fecha_hora': checkout.fecha_hora.isoformat(),
            'factura': {
                'id': factura.id,
                'numero': factura.numero,
                'total': float(factura.total),
            }
        }, 'Check-out realizado. Factura generada.')


@ns.route('/llegadas-hoy')
class LlegadasHoy(Resource):
    @jwt_required()
    def get(self):
        """Reservas con llegada programada para hoy."""
        hoy = date.today()
        reservas = Reserva.query.filter(
            Reserva.fecha_entrada == hoy,
            Reserva.estado_id.in_([1, 2])  # pendiente o confirmada
        ).order_by(Reserva.hora_llegada_est).all()
        return success_response(reserva_list_schema.dump(reservas))


@ns.route('/salidas-hoy')
class SalidasHoy(Resource):
    @jwt_required()
    def get(self):
        """Reservas con salida programada para hoy."""
        hoy = date.today()
        reservas = Reserva.query.filter(
            Reserva.fecha_salida == hoy,
            Reserva.estado_id == 3  # en_curso
        ).all()
        return success_response(reserva_list_schema.dump(reservas))
