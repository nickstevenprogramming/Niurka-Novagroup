"""
Rutas de Notificaciones — envío + historial + plantillas.
"""

from flask import request
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.notificacion import Notificacion, PlantillaNotificacion
from app.schemas.notificacion_schema import (
    notificacion_schema, notificaciones_schema,
    plantilla_schema, plantillas_schema,
)
from app.utils.decorators import role_required
from app.utils.pagination import paginate, success_response

ns = Namespace('notificaciones', description='Notificaciones y comunicaciones')


@ns.route('/')
class NotificacionList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def get(self):
        """Listar notificaciones."""
        query = Notificacion.query
        estado = request.args.get('estado')
        canal = request.args.get('canal')

        if estado:
            query = query.filter_by(estado=estado)
        if canal:
            query = query.filter_by(canal=canal)

        query = query.order_by(Notificacion.creado_en.desc())
        return paginate(query, notificaciones_schema)


@ns.route('/enviar')
class NotificacionEnviar(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente', 'recepcion'])
    def post(self):
        """Crear y enviar notificación."""
        data = request.json
        notif = Notificacion(
            reserva_id=data.get('reserva_id'),
            huesped_id=data.get('huesped_id'),
            empleado_id=data.get('empleado_id'),
            destinatario=data.get('destinatario'),
            asunto=data.get('asunto'),
            mensaje=data['mensaje'],
            canal=data.get('canal', 'email'),
            estado='pendiente'
        )
        db.session.add(notif)
        db.session.commit()
        return success_response(notificacion_schema.dump(notif), 'Notificación creada.', 201)


@ns.route('/plantillas')
class PlantillaList(Resource):
    @jwt_required()
    @role_required(['admin', 'gerente'])
    def get(self):
        """Listar plantillas de notificación."""
        plantillas_list = PlantillaNotificacion.query.all()
        return success_response(plantillas_schema.dump(plantillas_list))

    @jwt_required()
    @role_required(['admin'])
    def post(self):
        """Crear plantilla."""
        data = request.json
        plantilla = plantilla_schema.load(data, session=db.session)
        db.session.add(plantilla)
        db.session.commit()
        return success_response(plantilla_schema.dump(plantilla), 'Plantilla creada.', 201)


@ns.route('/plantillas/<int:id>')
class PlantillaDetail(Resource):
    @jwt_required()
    @role_required(['admin'])
    def put(self, id):
        """Actualizar plantilla."""
        p = PlantillaNotificacion.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            if hasattr(p, key) and key not in ('id',):
                setattr(p, key, value)
        db.session.commit()
        return success_response(plantilla_schema.dump(p), 'Plantilla actualizada.')
