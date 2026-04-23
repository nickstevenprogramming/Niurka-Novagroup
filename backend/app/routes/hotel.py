"""
Rutas de Configuración del Hotel.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.hotel import Hotel
from app.schemas.hotel_schema import hotel_schema
from app.utils.decorators import role_required
from app.utils.pagination import success_response, error_response

ns = Namespace('hotel', description='Configuración del hotel')


@ns.route('/')
class HotelConfig(Resource):
    @jwt_required()
    def get(self):
        """Obtener configuración del hotel."""
        hotel = Hotel.query.first()
        if not hotel:
            return error_response('Configuración del hotel no encontrada.', 404)
        return success_response(hotel_schema.dump(hotel))

    @jwt_required()
    @role_required(['admin', 'gerente'])
    def put(self):
        """Actualizar configuración del hotel."""
        hotel = Hotel.query.first()
        if not hotel:
            return error_response('Configuración del hotel no encontrada.', 404)

        data = request.json
        for key, value in data.items():
            if hasattr(hotel, key) and key not in ('id', 'creado_en'):
                setattr(hotel, key, value)

        db.session.commit()
        return success_response(hotel_schema.dump(hotel), 'Configuración actualizada.')
