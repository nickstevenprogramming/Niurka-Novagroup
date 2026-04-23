"""
Rutas de Parking — Estacionamiento + registro de uso.
"""

from datetime import datetime
from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.parking import Estacionamiento, UsoParking
from app.schemas.parking_schema import (
    estacionamiento_schema, estacionamientos_schema,
    uso_parking_schema, usos_parking_schema,
)
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response, error_response

ns = Namespace('parking', description='Estacionamiento')


@ns.route('/espacios')
class EspacioList(Resource):
    @jwt_required()
    def get(self):
        """Estado del estacionamiento."""
        espacios = Estacionamiento.query.order_by(Estacionamiento.numero).all()
        return success_response(estacionamientos_schema.dump(espacios))


@ns.route('/registrar-entrada')
class ParkingEntrada(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion', 'seguridad'])
    def post(self):
        """Registrar entrada de vehículo."""
        data = request.json
        espacio = Estacionamiento.query.get(data.get('espacio_id'))
        if not espacio:
            return error_response('Espacio no encontrado.', 404)
        if not espacio.disponible:
            return error_response('Espacio ocupado.', 400)

        uso = UsoParking(
            espacio_id=espacio.id,
            reserva_id=data.get('reserva_id'),
            huesped_id=data.get('huesped_id'),
            placa=data['placa'],
            marca_modelo=data.get('marca_modelo'),
        )
        espacio.disponible = False
        db.session.add(uso)
        db.session.commit()
        return success_response(uso_parking_schema.dump(uso), 'Entrada registrada.', 201)


@ns.route('/<int:id>/registrar-salida')
class ParkingSalida(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion', 'seguridad'])
    def patch(self, id):
        """Registrar salida de vehículo."""
        uso = UsoParking.query.get_or_404(id)
        if uso.salida:
            return error_response('Ya se registró la salida.', 400)

        uso.salida = datetime.now()
        data = request.json or {}
        uso.costo = data.get('costo', 0)

        # Liberar espacio
        espacio = Estacionamiento.query.get(uso.espacio_id)
        if espacio:
            espacio.disponible = True

        db.session.commit()
        return success_response(uso_parking_schema.dump(uso), 'Salida registrada.')
